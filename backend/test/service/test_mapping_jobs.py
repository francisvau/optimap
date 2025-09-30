from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from pydantic import ValidationError

from app.exceptions import BadRequest, EntityNotPresent
from app.model.job import MappingJobType, MappingStatus
from app.model.organization import Organization
from app.model.user import User
from app.schema.mapping.blueprint import (
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
)
from app.schema.mapping.job import CreateMappingJobRequest, UpdateMappingJobRequest


@pytest.mark.asyncio
async def test_create_mapping_job_with_organization(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="BP", description="BP Desc", organization_id=populated_org.id
        ),
        user_id=1,
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp"),
    )
    assert inp.name == "Inp"

    req = CreateMappingJobRequest(
        user_id=user.id,
        input_definition_id=inp.id,
        name="Job",
        type=MappingJobType.STATIC,
    )

    response = await mapping_job_svc.create_mapping_job(
        user_id=user.id, req=req, include=("user", "organization")
    )

    assert response.id is not None
    assert response.user.id == user.id
    assert response.organization.id == populated_org.id
    assert response.name == "Job"
    assert response.type == MappingJobType.STATIC
    assert response.created_at is not None


@pytest.mark.asyncio
async def test_read_mapping_job(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test reading an existing mapping job."""
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="BP",
            description="BP Desc",
            organization_id=populated_org.id,
        ),
        user_id=user.id,
    )
    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp"),
    )
    created_job = await mapping_job_svc.create_mapping_job(
        user_id=user.id,
        req=CreateMappingJobRequest(
            user_id=user.id,
            input_definition_id=inp.id,
            name="Job",
            type=MappingJobType.STATIC,
        ),
        include=("user", "organization"),
    )

    # Test: Read the mapping job
    response = await mapping_job_svc.read_mapping_job(
        created_job.id, include=("user", "organization", "input_definition")
    )

    assert response.id == created_job.id
    assert response.user.id == user.id
    assert response.organization.id == populated_org.id
    assert response.input_definition.id == inp.id
    assert response.name == "Job"
    assert response.type == MappingJobType.STATIC
    assert response.created_at is not None


@pytest.mark.asyncio
async def test_delete_mapping_job(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test deleting an existing mapping job."""
    # Setup: Create a mapping job
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="BP Desc"), user_id=user.id
    )
    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp", source_mapping_ids=[]),
    )
    req = CreateMappingJobRequest(
        user_id=user.id,
        organization_id=populated_org.id,
        input_definition_id=inp.id,
        name="Job",
        type=MappingJobType.STATIC,
    )
    created_job = await mapping_job_svc.create_mapping_job(user_id=user.id, req=req)

    # Test: Delete the mapping job
    await mapping_job_svc.delete_mapping_job(created_job.id)

    # Verify deletion
    with pytest.raises(
        EntityNotPresent, match=f"Mapping job with ID {created_job.id} not found"
    ):
        await mapping_job_svc.read_mapping_job(created_job.id)


@pytest.mark.asyncio
async def test_update_mapping_job(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test updating an existing mapping job."""
    # Setup: Create a mapping job
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="BP", description="BP Desc", organization_id=populated_org.id
        ),
        user_id=user.id,
    )
    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp", source_mapping_ids=[]),
    )
    created_job = await mapping_job_svc.create_mapping_job(
        user_id=user.id,
        include=("user", "organization"),
        req=CreateMappingJobRequest(
            user_id=user.id,
            input_definition_id=inp.id,
            name="Job",
            type=MappingJobType.STATIC,
        ),
    )

    # Test: Update the mapping job
    response = await mapping_job_svc.update_mapping_job(
        created_job.id,
        changes=UpdateMappingJobRequest.model_validate(
            {
                "status": MappingStatus.SUCCESS,
                "completed_at": "2023-10-01T00:00:00Z",
            }
        ),
        include=("user", "organization"),
    )

    assert response.id == created_job.id
    assert response.status == MappingStatus.SUCCESS
    assert str(response.completed_at) == "2023-10-01 00:00:00+00:00"
    assert response.user.id == user.id  # Unchanged field
    assert response.organization.id == populated_org.id  # Unchanged field


@pytest.mark.asyncio
async def test_create_dynamic_mapping_job(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test creating a dynamic mapping job."""
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="Dynamic BP",
            description="Dynamic BP Desc",
            organization_id=populated_org.id,
        ),
        user_id=user.id,
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Dynamic Inp"),
    )

    # Test creating job without external endpoint
    with pytest.raises(ValidationError):
        await mapping_job_svc.create_mapping_job(
            user_id=user.id,
            req=CreateMappingJobRequest(
                user_id=user.id,
                input_definition_id=inp.id,
                name="Dynamic Job",
                type=MappingJobType.DYNAMIC,
            ),
        )

    # Test creating job with invalid endpoint
    with patch("aiohttp.ClientSession.head") as mock_head:
        mock_head.side_effect = aiohttp.ClientError("Connection failed")

        with pytest.raises(BadRequest, match="External API endpoint is not reachable"):
            await mapping_job_svc.create_mapping_job(
                user_id=user.id,
                req=CreateMappingJobRequest(
                    user_id=user.id,
                    input_definition_id=inp.id,
                    name="Dynamic Job",
                    type=MappingJobType.DYNAMIC,
                    external_api_endpoint="http://invalid-endpoint.com",
                ),
            )

    # Test creating job with valid endpoint
    with patch("aiohttp.ClientSession.head") as mock_head:
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_head.return_value.__aenter__.return_value = mock_response

        response = await mapping_job_svc.create_mapping_job(
            user_id=user.id,
            req=CreateMappingJobRequest(
                user_id=user.id,
                input_definition_id=inp.id,
                name="Dynamic Job",
                type=MappingJobType.DYNAMIC,
                external_api_endpoint="http://valid-endpoint.com",
            ),
        )

        assert response.id is not None
        assert response.user_id == user.id
        assert response.organization_id == populated_org.id
        assert response.name == "Dynamic Job"
        assert response.type == MappingJobType.DYNAMIC
        assert response.external_api_endpoint == "http://valid-endpoint.com"
        assert response.created_at is not None


@pytest.mark.asyncio
async def test_handle_dynamic_mapping_non_existent_job(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test handling dynamic mapping with non-existent job."""
    # Test handling mapping with non-existent job
    with pytest.raises(
        EntityNotPresent, match="Mapping job with UUID invalid-uuid not found"
    ):
        await mapping_job_svc.handle_dynamic_mapping(
            uuid="invalid-uuid",
            source_mapping_id=1,
            data={"test": "data"},
        )


@pytest.mark.asyncio
async def test_handle_dynamic_mapping_invalid_source_mapping(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test handling dynamic mapping with invalid source mapping."""
    # Create blueprint and input definition
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="Dynamic BP",
            description="Dynamic BP Desc",
            organization_id=populated_org.id,
        ),
        user_id=user.id,
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Dynamic Inp"),
    )

    # Create dynamic job
    with patch("aiohttp.ClientSession.head") as mock_head:
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_head.return_value.__aenter__.return_value = mock_response

        job = await mapping_job_svc.create_mapping_job(
            user_id=user.id,
            req=CreateMappingJobRequest(
                user_id=user.id,
                input_definition_id=inp.id,
                name="Dynamic Job",
                type=MappingJobType.DYNAMIC,
                external_api_endpoint="http://valid-endpoint.com",
            ),
        )

    # Test handling mapping with invalid source mapping
    with pytest.raises(
        EntityNotPresent, match="Source mapping 999 not found in job's input definition"
    ):
        await mapping_job_svc.handle_dynamic_mapping(
            uuid=job.uuid,
            source_mapping_id=999,
            data={"test": "data"},
        )


@pytest.mark.asyncio
async def test_handle_dynamic_mapping_success(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test successful dynamic mapping."""
    # Create blueprint and input definition
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="Dynamic BP",
            description="Dynamic BP Desc",
            organization_id=populated_org.id,
        ),
        user_id=user.id,
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Dynamic Inp"),
    )

    # Create source mapping
    source_mapping = await bp_svc.create_source_mapping(
        input_id=inp.id,
        req=CreateMappingRequest(
            name="Test Mapping",
            jsonata_mapping='{"mapped": $}',
            input_json_schema={"type": "object"},
            output_json_schema={"type": "object"},
        ),
    )

    # Create dynamic job
    with patch("aiohttp.ClientSession.head") as mock_head:
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_head.return_value.__aenter__.return_value = mock_response

        job = await mapping_job_svc.create_mapping_job(
            user_id=user.id,
            req=CreateMappingJobRequest(
                user_id=user.id,
                input_definition_id=inp.id,
                name="Dynamic Job",
                type=MappingJobType.DYNAMIC,
                external_api_endpoint="http://valid-endpoint.com",
            ),
        )

    # Test successful mapping
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await mapping_job_svc.handle_dynamic_mapping(
            uuid=job.uuid,
            source_mapping_id=source_mapping.id,
            data={"test": "data"},
        )

        assert result is not None
        assert result == {"mapped": {"test": "data"}}
        mock_post.assert_called_once_with(
            "http://valid-endpoint.com",
            json=result,
            headers={"Content-Type": "application/json"},
        )


@pytest.mark.asyncio
async def test_handle_dynamic_mapping_failed_api_call(
    mapping_job_svc, user: User, populated_org: Organization, bp_svc
):
    """Test dynamic mapping with failed external API call."""
    # Create blueprint and input definition
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="Dynamic BP",
            description="Dynamic BP Desc",
            organization_id=populated_org.id,
        ),
        user_id=user.id,
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Dynamic Inp"),
    )

    # Create source mapping
    source_mapping = await bp_svc.create_source_mapping(
        input_id=inp.id,
        req=CreateMappingRequest(
            name="Test Mapping",
            jsonata_mapping='{"mapped": $}',
            input_json_schema={"type": "object"},
            output_json_schema={"type": "object"},
        ),
    )

    # Create dynamic job
    with patch("aiohttp.ClientSession.head") as mock_head:
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_head.return_value.__aenter__.return_value = mock_response

        job = await mapping_job_svc.create_mapping_job(
            user_id=user.id,
            req=CreateMappingJobRequest(
                user_id=user.id,
                input_definition_id=inp.id,
                name="Dynamic Job",
                type=MappingJobType.DYNAMIC,
                external_api_endpoint="http://valid-endpoint.com",
            ),
        )

    # Test failed external API call
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(
            BadRequest, match="Failed to post results to external endpoint: 500"
        ):
            await mapping_job_svc.handle_dynamic_mapping(
                uuid=job.uuid,
                source_mapping_id=source_mapping.id,
                data={"test": "data"},
            )
