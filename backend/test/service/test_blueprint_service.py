from __future__ import annotations

import pytest
import respx
from fastapi import status
from httpx import HTTPStatusError, Response
from sqlalchemy import select

from app.config import AUTH_KEY, ENGINE_URL_PREFIX
from app.exceptions import BadRequest, EngineError, EntityNotPresent
from app.model.blueprint import InputDefinition
from app.schema.mapping.blueprint import (
    BlueprintResponse,
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
    CreateOutputDefinitionRequest,
    JsonataGenerationRequest,
    UpdateBlueprintRequest,
    UpdateInputDefinitionRequest,
    UpdateMappingRequest,
    UpdateOutputDefinitionRequest,
)
from app.service.mapping.blueprint import MappingBlueprintService
from app.util.schema import DEFAULT_JSON_SCHEMA

# ---------------------------------------------------------------------------
# Helper data
# ---------------------------------------------------------------------------

MOCK_MAPPING_JSON = {
    "name": "Mock Mapping",
    "file_type": "JSON",
    "input_json_schema": {"foo": "bar"},
    "jsonata_mapping": "$.foo",
    "output_json_schema": {"baz": "qux"},
    "model": None,
}

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_blueprint_crud(user, bp_svc):
    # *-Create a blueprint-*
    create_req = CreateBlueprintRequest(
        name="Blueprint A", description="desc", model_prompt="prompt"
    )
    created = await bp_svc.create_blueprint(req=create_req, user_id=user.id)
    assert isinstance(created, BlueprintResponse)
    assert created.name == "Blueprint A"

    # *-Read without includes-*
    fetched = await bp_svc.read_blueprint(created.id)
    assert fetched.id == created.id

    # *-Update-*
    updated = await bp_svc.update_blueprint(
        created.id, changes=UpdateBlueprintRequest(name="Blueprint B")
    )
    blueprint = updated.model_dump(exclude_unset=True)

    assert blueprint["name"] == "Blueprint B"
    assert "output_definition" not in blueprint
    assert "input_definitions" not in blueprint

    # *-Delete-*
    respx.delete(f"{ENGINE_URL_PREFIX}/mappings").mock(
        return_value=Response(204, json={})
    )
    await bp_svc.delete_blueprint(created.id)

    with pytest.raises(EntityNotPresent):
        await bp_svc.read_blueprint(created.id)


@pytest.mark.asyncio
@respx.mock
async def test_read_blueprint_with_input_defs_and_remote_mappings(user, bp_svc):
    """Ensure nested source_mappings are injected when 'include' is used."""
    # Create blueprint and input-definition that references a remote mapping
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="BP Desc"), user_id=user.id
    )

    input = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Input", source_mapping_ids=["map-123"]),
    )

    source_mapping = await bp_svc.create_source_mapping(
        input_id=input.id,
        req=CreateMappingRequest(
            name="Map1",
            model_id="deepseek",
        ),
    )

    bp_full = await bp_svc.read_blueprint(
        bp.id, include=("input_definitions.source_mappings")
    )

    [input_definition] = bp_full.input_definitions
    [source_mapping] = input_definition.source_mappings

    assert source_mapping.id == source_mapping.id
    assert source_mapping.name == "Map1" == source_mapping.name
    assert source_mapping.model_id == "deepseek" == source_mapping.model_id


# ---------------------------------------------------------------------------
# Input definitions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_input_definition_crud(user, bp_svc):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="BP Desc"), user_id=user.id
    )

    # *-Create-*
    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp", source_mapping_ids=[]),
    )
    assert inp.name == "Inp"

    # *-Read-*
    respx.get(f"{ENGINE_URL_PREFIX}/mappings").mock(return_value=Response(200, json=[]))

    fetched = await bp_svc.read_input_definition(inp.id)
    assert fetched.id == inp.id
    assert fetched.source_mappings == []

    # *-Update-*
    upd = await bp_svc.update_input_definition(
        inp.id, changes=UpdateInputDefinitionRequest(name="Inp-2")
    )
    assert upd.name == "Inp-2"

    # *-Delete-*
    await bp_svc.delete_input_definition(inp.id)
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_input_definition(inp.id)


# ---------------------------------------------------------------------------
# Output definitions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_output_definition_crud(user, bp_svc):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="BP Desc"), user_id=user.id
    )

    create_req = CreateOutputDefinitionRequest(
        name="Out", description=None, json_schema={"type": "object"}
    )
    out = await bp_svc.create_output_definition(blueprint_id=bp.id, req=create_req)
    assert out.json_schema["type"] == "object"

    fetched = await bp_svc.read_output_definition(out.id)
    assert fetched.id == out.id

    upd = await bp_svc.update_output_definition(
        out.id, changes=UpdateOutputDefinitionRequest(name="Out-2")
    )
    assert upd.name == "Out-2"

    await bp_svc.delete_output_definition(out.id)
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_output_definition(out.id)


# ---------------------------------------------------------------------------
# Source mappings (engine integration)
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_source_mapping_lifecycle(user, bp_svc):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="BP Desc"), user_id=user.id
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp", source_mapping_ids=[]),
    )

    result = await bp_svc.create_source_mapping(
        inp.id,
        req=CreateMappingRequest(
            name="Map1",
            model_id="openai",
        ),
    )

    assert result.name == "Map1"
    assert result.model_id == "openai"

    upd = await bp_svc.update_source_mapping(
        mapping_id=result.id,
        req=UpdateMappingRequest(jsonata_mapping="$.new"),
    )
    assert upd.jsonata_mapping == "$.new"

    await bp_svc.delete_source_mapping(upd.id)

    with pytest.raises(EntityNotPresent):
        await bp_svc.read_source_mapping(upd.id)


@respx.mock
@pytest.mark.asyncio
async def test_generate_jsonata_mapping(bp_svc, mapping_generation):
    respx.post(f"{ENGINE_URL_PREFIX}/mappings/generate").mock(
        return_value=Response(200, json=mapping_generation)
    )
    expr = await bp_svc.generate_jsonata_mapping(
        request=JsonataGenerationRequest(
            input_json_schema={}, output_json_schema={}, model_id="openai"
        )
    )
    assert expr.mapping == mapping_generation["mapping"]


# ---------------------------------------------------------------------------
# Negative cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_entity_not_present_errors(bp_svc):
    # Blueprint not found
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_blueprint(999)

    with pytest.raises(EntityNotPresent):
        await bp_svc.update_blueprint(999, changes=UpdateBlueprintRequest())

    with pytest.raises(EntityNotPresent):
        await bp_svc.delete_blueprint(999)

    # Input definition not found
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_input_definition(999)

    with pytest.raises(BadRequest):
        await bp_svc.update_input_definition(
            999, changes=UpdateInputDefinitionRequest()
        )

    with pytest.raises(EntityNotPresent):
        await bp_svc.delete_input_definition(999)

    # Output definition not found
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_output_definition(999)

    with pytest.raises(EntityNotPresent):
        await bp_svc.update_output_definition(
            999, changes=UpdateOutputDefinitionRequest()
        )

    with pytest.raises(EntityNotPresent):
        await bp_svc.delete_output_definition(999)


# ---------------------------------------------------------------------------
# Relationship loading
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_read_blueprint_with_all_related(bp_svc, user, organization):
    """include both input_definitions and output_definition at once."""
    # Create a blueprint
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="Full",
            description="d",
            organization_id=organization.id,
        ),
        user_id=user.id,
    )

    # Create input and output definitions
    out = await bp_svc.create_output_definition(
        blueprint_id=bp.id,
        req=CreateOutputDefinitionRequest(
            name="Out",
            description=None,
            json_schema=DEFAULT_JSON_SCHEMA | {"type": "object"},
        ),
    )
    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp"),
    )

    # Create a source mapping
    mapping = await bp_svc.create_source_mapping(
        inp.id, req=CreateMappingRequest(**MOCK_MAPPING_JSON)
    )
    assert mapping.name == MOCK_MAPPING_JSON["name"]

    # Fetch the blueprint with all related entities
    fetched = await bp_svc.read_blueprint(
        bp.id,
        include=MappingBlueprintService.BLUEPRINT_REL_MAP.keys(),
    )

    assert fetched.output_definition.id == out.id
    assert len(fetched.input_definitions) == 1
    assert fetched.input_definitions[0].id == inp.id
    assert fetched.input_definitions[0].source_mappings[0].id == mapping.id
    assert fetched.user.id == user.id
    assert fetched.organization.id == organization.id
    assert fetched.organization.name == organization.name


# ---------------------------------------------------------------------------
# Cascading delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_delete_blueprint_cascades_children(user, bp_svc):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="Cascade", description="d"), user_id=user.id
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp"),
    )

    await bp_svc.delete_blueprint(bp.id)

    # orphan should be gone
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_input_definition(inp.id)


# ---------------------------------------------------------------------------
# Update all fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_input_and_output_every_field(user, bp_svc):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="UpdateAll", description="d"), user_id=user.id
    )
    out = await bp_svc.create_output_definition(
        blueprint_id=bp.id,
        req=CreateOutputDefinitionRequest(
            name="OldOut",
            description="x",
            json_schema=DEFAULT_JSON_SCHEMA | {"type": "string"},
        ),
    )

    new_schema = DEFAULT_JSON_SCHEMA | {"type": "number"}
    upd_out = await bp_svc.update_output_definition(
        out.id,
        changes=UpdateOutputDefinitionRequest(
            name="NewOut", description=None, json_schema=new_schema
        ),
    )
    assert upd_out.json_schema == DEFAULT_JSON_SCHEMA | new_schema
    assert upd_out.description is None


# ---------------------------------------------------------------------------
# Upstream engine failure bubbles up
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_engine_failure_propagates(bp_svc):
    route = respx.post(f"{ENGINE_URL_PREFIX}/mappings/generate").mock(
        side_effect=HTTPStatusError(
            "Engine boom!", request=None, response=Response(500, json={"boom": "boom"})
        )
    )
    with pytest.raises(EngineError):
        await bp_svc.generate_jsonata_mapping(
            request=JsonataGenerationRequest(
                input_json_schema={}, output_json_schema={}
            )
        )
    assert route.called


@pytest.mark.asyncio
async def test_input_definition_versioning(async_client, session_id, user, bp_svc):
    async_client.cookies.set(AUTH_KEY, session_id)

    # Create a blueprint and an initial input definition
    bp = await bp_svc.create_blueprint(
        user_id=user.id, req=CreateBlueprintRequest(name="VersionedBP", description="d")
    )
    inp1 = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="VersionedInput", description="v1"),
    )

    # Create a new version via a versioning endpoint (or directly via the service for now)
    inp2 = await bp_svc.create_input_definition_version(
        base_input_def_id=inp1.id,
    )

    # Validate version group consistency
    assert inp1.version_group_id == inp2.version_group_id
    assert inp2.version == inp1.version + 1

    # Only the new one is selected
    group = await bp_svc.db.execute(
        select(InputDefinition).where(
            InputDefinition.version_group_id == inp1.version_group_id
        )
    )
    versions = group.scalars().all()
    selected = [v for v in versions if v.is_selected]

    assert len(versions) == 2
    assert len(selected) == 1
    assert selected[0].id == inp2.id


@pytest.mark.asyncio
@respx.mock
async def test_select_input_definition_version(async_client, session_id, user, bp_svc):
    async_client.cookies.set("session", session_id)
    respx.get(f"{ENGINE_URL_PREFIX}/mappings").mock(
        return_value=Response(status.HTTP_200_OK, json={})
    )

    # Create blueprint and initial input definition
    bp = await bp_svc.create_blueprint(
        user_id=user.id, req=CreateBlueprintRequest(name="VersionedBP", description="d")
    )
    v1 = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Input", description="v1"),
    )
    await bp_svc.create_input_definition_version(
        base_input_def_id=v1.id,
    )
    v3 = await bp_svc.create_input_definition_version(
        base_input_def_id=v1.id,
    )

    # Initially the last created version should be selected
    group = await bp_svc.db.execute(
        select(InputDefinition).where(
            InputDefinition.version_group_id == v1.version_group_id
        )
    )
    versions = group.scalars().all()
    selected_before = [v.id for v in versions if v.is_selected]
    assert selected_before == [v3.id]

    # Select v1 as the active version
    await bp_svc.select_input_definition_version(blueprint_id=bp.id, input_id=v1.id)

    # Check selection updated correctly
    group = await bp_svc.db.execute(
        select(InputDefinition).where(
            InputDefinition.version_group_id == v1.version_group_id
        )
    )
    updated_versions = group.scalars().all()
    selected_after = [v.id for v in updated_versions if v.is_selected]

    assert len(selected_after) == 1
    assert selected_after[0] == v1.id


@pytest.mark.asyncio
async def test_get_input_definition_versions(bp_svc, user):
    # Create blueprint and multiple versions
    bp = await bp_svc.create_blueprint(
        user_id=user.id, req=CreateBlueprintRequest(name="TestBP", description="test")
    )

    v1 = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="VersionedInput", description="v1"),
    )
    v2 = await bp_svc.create_input_definition_version(
        base_input_def_id=v1.id,
    )

    v3 = await bp_svc.create_input_definition_version(
        base_input_def_id=v1.id,
    )

    versions = await bp_svc.get_input_definition_versions(input_definition_id=v1.id)

    assert len(versions) == 3
    assert [v.version for v in versions] == [v1.version, v2.version, v3.version]
    assert all(v.version_group_id == v1.version_group_id for v in versions)
