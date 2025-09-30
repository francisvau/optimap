import pytest
import respx
from fastapi import status
from httpx import Response

from app.config import AUTH_KEY, ENGINE_URL_PREFIX
from app.exceptions import EntityNotPresent
from app.model.user import User
from app.schema.mapping.blueprint import (
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
    UpdateMappingRequest,
)
from app.service.mapping.blueprint import MappingBlueprintService


async def _owned_input(user: User, svc: MappingBlueprintService):
    bp = await svc.create_blueprint(
        user_id=user.id, req=CreateBlueprintRequest(name="BP", description="d")
    )

    inp = await svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp", description="d"),
    )

    return bp, inp


@pytest.mark.asyncio
async def test_blueprint_create(
    async_client, user, session_id, admin_session_id, bp_svc
):
    req = CreateBlueprintRequest(
        name="Blueprint A",
        description="desc",
        model_prompt="prompt",
    ).model_dump()

    # Create a blueprint as a normal user
    async_client.cookies.set(AUTH_KEY, session_id)
    r1 = await async_client.post("/mappings/blueprints", json=req)
    assert r1.status_code == status.HTTP_201_CREATED

    created = await bp_svc.read_blueprint(r1.json()["id"], include=("user"))
    assert created.user.id == user.id

    # Create a blueprint as an admin
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    r2 = await async_client.post("/mappings/blueprints", json=req | {"userId": user.id})
    assert r2.status_code == status.HTTP_201_CREATED

    created = await bp_svc.read_blueprint(r2.json()["id"], include=("user"))
    assert created.user.id == user.id


@pytest.mark.asyncio
async def test_blueprint_update(
    async_client, admin, session_id, admin_session_id, bp_svc
):
    bp = await bp_svc.create_blueprint(
        user_id=admin.id, req=CreateBlueprintRequest(name="BP", description="d")
    )

    # Update as an admin user
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    ok = await async_client.patch(
        f"/mappings/blueprints/{bp.id}", json={"description": "new"}
    )
    assert ok.status_code == status.HTTP_200_OK
    assert ok.json()["description"] == "New"

    # Update as a normal user
    async_client.cookies.set(AUTH_KEY, session_id)
    bad = await async_client.patch(
        f"/mappings/blueprints/{bp.id}", json={"description": "hack"}
    )
    assert bad.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@respx.mock
async def test_blueprint_delete(
    async_client, admin, user, session_id, admin_session_id, bp_svc
):
    # Mock engine response
    respx.delete(f"{ENGINE_URL_PREFIX}/mappings").mock(
        return_value=Response(status.HTTP_204_NO_CONTENT, json={})
    )

    # Delete as a admin for normal user
    bp = await bp_svc.create_blueprint(
        user_id=user.id,
        req=CreateBlueprintRequest(name="DelBP", description="d"),
    )
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    assert (
        await async_client.delete(f"/mappings/blueprints/{bp.id}")
    ).status_code == status.HTTP_204_NO_CONTENT

    # Delete as a normal user for normal user
    bp = await bp_svc.create_blueprint(
        user_id=user.id,
        req=CreateBlueprintRequest(name="DelBP", description="d"),
    )
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.delete(f"/mappings/blueprints/{bp.id}")
    ).status_code == status.HTTP_204_NO_CONTENT

    # Delete as a normal user for admin
    bp = await bp_svc.create_blueprint(
        user_id=admin.id,
        req=CreateBlueprintRequest(name="DelBP", description="d"),
    )
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.delete(f"/mappings/blueprints/{bp.id}")
    ).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@respx.mock
async def test_blueprint_read(
    async_client, admin, session_id, admin_session_id, bp_svc
):
    # Mock engine response
    respx.get(f"{ENGINE_URL_PREFIX}/mappings").mock(
        return_value=Response(status.HTTP_200_OK, json={})
    )

    # Create a blueprint as a normal user
    bp = await bp_svc.create_blueprint(
        user_id=admin.id,
        req=CreateBlueprintRequest(name="Priv", description="d"),
    )

    # Read as normal user
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.get(f"/mappings/blueprints/{bp.id}")
    ).status_code == status.HTTP_401_UNAUTHORIZED

    # Read as admin
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    assert (
        await async_client.get(f"/mappings/blueprints/{bp.id}")
    ).status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_input_definition_create(async_client, user, session_id, bp_svc):
    # Create blueprint
    bp = await bp_svc.create_blueprint(
        user_id=user.id, req=CreateBlueprintRequest(name="BP", description="d")
    )

    # Create an input definition as a normal user
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.post(
            f"/mappings/blueprints/{bp.id}/input", json={"name": "In"}
        )
    ).status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_input_definition_patch(
    async_client, admin, user, session_id, admin_session_id, bp_svc
):
    # Patch as a admin for normal user
    bp, inp = await _owned_input(user, bp_svc)
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    assert (
        await async_client.patch(
            f"/mappings/blueprints/{bp.id}/input/{inp.id}", json={"name": "Hack"}
        )
    ).status_code == status.HTTP_200_OK

    # Patch as a normal user for normal user
    bp, inp = await _owned_input(user, bp_svc)
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.patch(
            f"/mappings/blueprints/{bp.id}/input/{inp.id}", json={"name": "New"}
        )
    ).status_code == status.HTTP_200_OK

    # Patch as a normal user for admin
    bp, inp = await _owned_input(admin, bp_svc)
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.patch(
            f"/mappings/blueprints/{bp.id}/input/{inp.id}", json={"name": "Hack"}
        )
    ).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_input_definition_delete(
    async_client, user, session_id, admin, admin_session_id, bp_svc
):
    # admin deletes someone else’s input
    bp, inp = await _owned_input(user, bp_svc)
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    assert (
        await async_client.delete(f"/mappings/blueprints/{bp.id}/input/{inp.id}")
    ).status_code == status.HTTP_204_NO_CONTENT

    # owner deletes own input
    bp2, inp2 = await _owned_input(user, bp_svc)
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.delete(f"/mappings/blueprints/{bp2.id}/input/{inp2.id}")
    ).status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(EntityNotPresent):
        await bp_svc.read_input_definition(inp2.id)

    # normal user tries to delete admin’s input
    bp_admin, inp_admin = await _owned_input(admin, bp_svc)  # type: ignore[attr-defined]
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.delete(
            f"/mappings/blueprints/{bp_admin.id}/input/{inp_admin.id}"
        )
    ).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_output_definition_crud(
    async_client, user, session_id, admin, admin_session_id, bp_svc
):
    # owner creates output definition
    bp = await bp_svc.create_blueprint(
        user_id=user.id, req=CreateBlueprintRequest(name="BP", description="d")
    )

    async_client.cookies.set(AUTH_KEY, session_id)
    create = await async_client.patch(
        f"/mappings/blueprints/{bp.id}/output",
        json={"name": "Out", "description": "d", "json_schema": {"type": "object"}},
    )

    assert create.status_code == status.HTTP_200_OK
    assert create.json()["name"] == "Out"
    assert create.json()["description"] == "d"

    # admin reads, patches, deletes
    async_client.cookies.set(AUTH_KEY, admin_session_id)

    read = await async_client.get(f"/mappings/blueprints/{bp.id}/output")
    assert read.status_code == status.HTTP_200_OK
    assert read.json()["name"] == "Out"
    assert read.json()["description"] == "d"

    patch = await async_client.patch(
        f"/mappings/blueprints/{bp.id}/output",
        json={"name": "Adminout", "description": "d"},
    )
    assert patch.status_code == status.HTTP_200_OK
    assert patch.json()["name"] == "Adminout"
    assert patch.json()["description"] == "d"

    get = await async_client.get(f"/mappings/blueprints/{bp.id}/output")
    assert get.status_code == status.HTTP_200_OK
    assert get.json()["name"] == "Adminout"
    assert get.json()["description"] == "d"

    patch = await async_client.patch(
        f"/mappings/blueprints/{bp.id}/output",
        json={"name": "Adminout", "description": "new"},
    )
    assert patch.status_code == status.HTTP_200_OK
    assert patch.json()["name"] == "Adminout"
    assert patch.json()["description"] == "new"

    # Normal user cannot touch admin’s output
    bp_admin = await bp_svc.create_blueprint(
        user_id=admin.id,
        req=CreateBlueprintRequest(name="BP-A", description="d"),
    )

    async_client.cookies.set(AUTH_KEY, admin_session_id)
    await async_client.post(
        f"/mappings/blueprints/{bp_admin.id}/output",
        json={"name": "Adminout", "json_schema": {"type": "object"}},
    )

    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.get(f"/mappings/blueprints/{bp_admin.id}/output")
    ).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@respx.mock
async def test_mapping_create(
    async_client, user, session_id, admin, admin_session_id, bp_svc, mapping_payload
):
    # Get owned input
    bp, inp = await _owned_input(user, bp_svc)

    # Mock engine response
    eng_resp = mapping_payload | {"id": "map-c"}
    respx.post(f"{ENGINE_URL_PREFIX}/mappings").mock(
        return_value=Response(200, json=eng_resp)
    )
    respx.get(f"{ENGINE_URL_PREFIX}/mappings").mock(
        return_value=Response(200, json=[eng_resp])
    )

    # Owner creates
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings",
        json=mapping_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Admin also creates for that user
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    response = await async_client.post(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings",
        json=mapping_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Normal user cannot create on admin input
    bp_admin, inp_admin = await _owned_input(admin, bp_svc)
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.post(
            f"/mappings/blueprints/{bp_admin.id}/input/{inp_admin.id}/mappings",
            json=mapping_payload,
        )
    ).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@respx.mock
async def test_mapping_patch(
    async_client, user, session_id, admin, admin_session_id, bp_svc, mapping_payload
):
    # Create owned blueprint and input
    bp, inp = await _owned_input(user, bp_svc)

    # Create mapping
    mapping = await bp_svc.create_source_mapping(
        inp.id, req=CreateMappingRequest(**mapping_payload)
    )

    # Owner patches
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.patch(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings/{mapping.id}",
        json=UpdateMappingRequest(jsonata_mapping="$.bar").model_dump(
            exclude_unset=True
        ),
    )
    assert response.status_code == status.HTTP_200_OK

    # Admin patches someone else
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    response = await async_client.patch(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings/{mapping.id}",
        json=UpdateMappingRequest(jsonata_mapping="$.foo").model_dump(
            exclude_unset=True
        ),
    )
    assert response.status_code == status.HTTP_200_OK

    # Normal user fails on admin’s mapping
    bp_admin, inp_admin = await _owned_input(admin, bp_svc)

    mapping = await bp_svc.create_source_mapping(
        input_id=inp_admin.id,
        req=CreateMappingRequest(**mapping_payload),
    )

    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.patch(
        f"/mappings/blueprints/{bp_admin.id}/input/{inp_admin.id}/mappings/{mapping.id}",
        json={"jsonata_mapping": "$.hack"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@respx.mock
async def test_mapping_delete(
    async_client, user, session_id, admin_session_id, bp_svc, mapping_payload
):
    # Create owned blueprint and input
    bp, inp = await _owned_input(user, bp_svc)

    mapping = await bp_svc.create_source_mapping(
        inp.id, req=CreateMappingRequest(**mapping_payload)
    )

    # Admin deletes someone else’s mapping
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    response = await async_client.delete(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings/{mapping.id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Owner deletes own mapping
    inp2_bp, inp2 = await _owned_input(user, bp_svc)

    mapping = await bp_svc.create_source_mapping(
        inp2.id, req=CreateMappingRequest(**mapping_payload)
    )

    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.delete(
        f"/mappings/blueprints/{inp2_bp.id}/input/{inp2.id}/mappings/{mapping.id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
@respx.mock
async def test_mapping_generate(
    async_client,
    user,
    session_id,
    admin,
    admin_session_id,
    bp_svc,
    mapping_generation,
    mapping_payload,
):
    # Create owned blueprint and input
    bp, inp = await _owned_input(user, bp_svc)

    mapping = await bp_svc.create_source_mapping(
        inp.id, req=CreateMappingRequest(**mapping_payload)
    )

    # Mock engine response
    respx.post(f"{ENGINE_URL_PREFIX}/mappings/generate").mock(
        return_value=Response(200, json=mapping_generation)
    )

    # Admin generates mapping
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    response = await async_client.post(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings/{mapping.id}/generate",
        json={"organizationId": 1, "finetuning": True},
    )
    response.status_code == status.HTTP_200_OK

    # Owner generates mapping
    async_client.cookies.set(AUTH_KEY, session_id)
    ok = await async_client.post(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/mappings/{mapping.id}/generate",
        json={"organization_id": 1, "finetuning": True},
    )
    assert ok.status_code == status.HTTP_200_OK
    assert ok.json()["mapping"] == mapping_generation["mapping"]

    # Normal user fails on admin mapping
    bp_admin, inp_admin = await _owned_input(admin, bp_svc)
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/mappings/blueprints/{bp_admin.id}/input/{inp_admin.id}/mappings/{mapping.id}/generate",
        json={"organization_id": 1, "finetuning": True},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_input_definition_version_select(async_client, user, session_id, bp_svc):
    bp, inp = await _owned_input(user, bp_svc)
    # Create a second version
    await bp_svc.create_input_definition_version(
        base_input_def_id=inp.id,
    )

    async_client.cookies.set(AUTH_KEY, session_id)
    res = await async_client.post(f"/mappings/blueprints/{bp.id}/input/{inp.id}/select")
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_list_input_definition_versions(async_client, user, session_id, bp_svc):
    bp, inp = await _owned_input(user, bp_svc)

    # Add multiple versions
    for i in range(2, 5):
        await bp_svc.create_input_definition_version(
            base_input_def_id=inp.id,
        )

    async_client.cookies.set(AUTH_KEY, session_id)
    res = await async_client.get(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/versions"
    )
    assert res.status_code == status.HTTP_200_OK
    versions = res.json()
    assert isinstance(versions, list)
    assert len(versions) == 4
    assert all("id" in v for v in versions)


@pytest.mark.asyncio
async def test_create_input_definition_version(
    async_client, user, session_id, bp_svc, mapping_payload
):
    bp, inp = await _owned_input(user, bp_svc)

    mapping = await bp_svc.create_source_mapping(
        inp.id, req=CreateMappingRequest(**mapping_payload)
    )
    print(mapping)

    async_client.cookies.set(AUTH_KEY, session_id)
    res = await async_client.post(
        f"/mappings/blueprints/{bp.id}/input/{inp.id}/new-version"
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    print("hwat the helll")

    assert len(data["sourceMappings"]) == 1
    assert data["sourceMappings"][0]["id"] != mapping.id
    assert data["name"] == "Inp"

    res = await async_client.get(f"/mappings/blueprints/{bp.id}/input/{inp.id}")
    old_data = res.json()
    assert len(old_data["sourceMappings"]) == 1
    assert old_data["sourceMappings"][0]["id"] == mapping.id
    assert old_data["name"] == "Inp"
    assert old_data["version"] == 1
    assert data["version"] == 2
