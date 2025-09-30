from unittest.mock import AsyncMock, patch

import pytest
import respx
from fastapi import status
from httpx import AsyncClient

from app.config import AUTH_KEY
from app.model.job import MappingJobType, MappingStatus
from app.model.organization import Organization
from app.model.user import User
from app.schema.mapping.blueprint import (
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
)
from app.schema.mapping.job import CreateMappingJobRequest
from app.service.mapping.blueprint import MappingBlueprintService
from app.service.mapping.job import MappingJobService

"""
Create a mapping job
"""


@pytest.mark.asyncio
@respx.mock
async def test_create_mapping_job_endpoint(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="BP Desc"), user_id=user.id
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp"),
    )
    assert inp.name == "Inp"

    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        "/mappings/jobs",
        json={
            "user_id": user.id,
            "organization_id": populated_org.id,
            "input_definition_id": inp.id,
            "name": "Job",
            "type": MappingJobType.STATIC.value,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    job = response.json()

    assert job["name"] == "Job"
    assert job["type"] == MappingJobType.STATIC.value
    assert job["status"] == MappingStatus.PENDING.value
    assert "createdAt" in job


@pytest.mark.asyncio
@respx.mock
async def test_create_mapping_job_org_endpoint(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="BP", description="BP Desc", organization_id=populated_org.id
        ),
        user_id=user.id,
    )

    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="Inp"),
    )
    assert inp.name == "Inp"

    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        "/mappings/jobs",
        json={
            "user_id": user.id,
            "input_definition_id": inp.id,
            "name": "Job",
            "type": MappingJobType.STATIC.value,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    job = response.json()

    assert job["name"] == "Job"
    assert job["type"] == MappingJobType.STATIC.value
    assert job["status"] == MappingStatus.PENDING.value
    assert "createdAt" in job

    response = await async_client.get(f"/mappings/jobs/organization/{populated_org.id}")
    job = response.json()
    assert job[0]["organizationId"] == populated_org.id


@pytest.mark.asyncio
@respx.mock
async def test_handle_dynamic_mapping_endpoint_non_existent_job(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    """Test dynamic mapping endpoint with non-existent job."""
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
            jsonata_mapping='{"bar": $.foo}',
            input_json_schema={"type": "object"},
            output_json_schema={"type": "object"},
        ),
    )

    async_client.cookies.set(AUTH_KEY, session_id)

    # Test with non-existent job
    response = await async_client.post(
        f"/mappings/jobs/dynamic/invalid-uuid/{source_mapping.id}",
        json={"data": {"test": "data"}},
    )
    assert response.status_code == 404
    assert "Mapping job with UUID invalid-uuid not found" in response.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_handle_dynamic_mapping_endpoint_invalid_source_mapping(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    """Test dynamic mapping endpoint with invalid source mapping."""
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
        job_uuid = response.uuid

    async_client.cookies.set(AUTH_KEY, session_id)

    # Test with invalid source mapping
    response = await async_client.post(
        f"/mappings/jobs/dynamic/{job_uuid}/999",
        json={"data": {"test": "data"}},
    )
    assert response.status_code == 404
    assert (
        "Source mapping 999 not found in job's input definition"
        in response.json()["detail"]
    )


@pytest.mark.asyncio
@respx.mock
async def test_handle_dynamic_mapping_endpoint_large_payload(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    """Test dynamic mapping endpoint with too large payload."""
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
            jsonata_mapping='{"bar": $.foo}',
            input_json_schema={"type": "object"},
            output_json_schema={"type": "object"},
        ),
    )

    # Create dynamic job
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
        job_uuid = response.uuid

    async_client.cookies.set(AUTH_KEY, session_id)

    # Test with too large payload
    large_data = {"data": "x" * (1024 * 1024 + 1)}  # > 1MB
    response = await async_client.post(
        f"/mappings/jobs/dynamic/{job_uuid}/{source_mapping.id}",
        json=large_data,
    )
    assert response.status_code == 400
    assert "Request body too large" in response.json()["detail"]


@pytest.mark.asyncio
@respx.mock
async def test_handle_dynamic_mapping_endpoint_success(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    """Test successful dynamic mapping endpoint."""
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
            jsonata_mapping='{"bar": $.foo}',
            input_json_schema={"type": "object"},
            output_json_schema={"type": "object"},
        ),
    )

    # Create dynamic job
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
        job_uuid = response.uuid

    async_client.cookies.set(AUTH_KEY, session_id)

    # Test successful mapping
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await async_client.post(
            f"/mappings/jobs/dynamic/{job_uuid}/{source_mapping.id}",
            json={"data": {"foo": "data"}},
        )
        assert response.status_code == 200
        assert response.json() == {"bar": "data"}


@pytest.mark.asyncio
@respx.mock
async def test_handle_dynamic_mapping_endpoint_failed_api_call(
    async_client: AsyncClient,
    user: User,
    session_id: str,
    populated_org: Organization,
    bp_svc: MappingBlueprintService,
    mapping_job_svc: MappingJobService,
):
    """Test dynamic mapping endpoint with failed external API call."""
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
            jsonata_mapping='{"bar": $.foo}',
            input_json_schema={"type": "object"},
            output_json_schema={"type": "object"},
        ),
    )

    # Create dynamic job
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
        job_uuid = response.uuid

    async_client.cookies.set(AUTH_KEY, session_id)

    # Test failed external API call
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await async_client.post(
            f"/mappings/jobs/dynamic/{job_uuid}/{source_mapping.id}",
            json={"data": {"test": "data"}},
        )
        assert response.status_code == 400
        assert (
            "Failed to post results to external endpoint: 500"
            in response.json()["detail"]
        )
