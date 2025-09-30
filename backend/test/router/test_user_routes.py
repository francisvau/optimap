from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pytest
from fastapi import status

from app.config import AUTH_KEY
from app.model.job import MappingJobType, MappingStatus
from app.schema.mapping.blueprint import (
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
)
from app.schema.mapping.job import (
    CreateMappingExecutionRequest,
    CreateMappingJobRequest,
    UpdateMappingExecutionRequest,
)
from app.schema.organization import CreateOrganizationRequest

if TYPE_CHECKING:
    pass


@pytest.mark.asyncio
async def test_read_user_organizations_access(
    async_client,
    user,
    other_user,
    session_id,
    other_session_id,
    org_svc,
):
    """Admin and self can access user organizations; others are denied."""

    # Create organization for `user`
    org1 = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Org1")
    )

    # User reads own organizations → OK
    async_client.cookies.set(AUTH_KEY, session_id)
    resp = await async_client.get(f"/users/{user.id}/organizations")
    assert resp.status_code == status.HTTP_200_OK
    assert org1.id in [org["id"] for org in resp.json()]

    # Other user tries to read → 401
    async_client.cookies.set(AUTH_KEY, other_session_id)
    resp = await async_client.get(f"/users/{user.id}/organizations")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # Promote other_user to admin manually
    other_user.is_admin = True
    await org_svc.db.flush()

    # Admin reads any user's organizations → OK
    async_client.cookies.set(AUTH_KEY, other_session_id)
    resp = await async_client.get(f"/users/{user.id}/organizations")
    assert resp.status_code == status.HTTP_200_OK
    assert org1.id in [org["id"] for org in resp.json()]


@pytest.mark.asyncio
async def test_get_user_stats_endpoint(
    async_client, user, session_id, bp_svc, mapping_job_svc
):
    # Set auth cookie
    async_client.cookies.set(AUTH_KEY, session_id)

    # Create an organization
    org_resp = await async_client.post(
        "/organizations",
        json=CreateOrganizationRequest(
            name="StatsOrg", description="Test stats"
        ).model_dump(),
    )
    assert org_resp.status_code == 201
    org_id = org_resp.json()["id"]

    # Create blueprint and input definition
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(name="BP", description="..."), user_id=user.id
    )
    inp = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="input", source_mapping_ids=[]),
    )

    # Create source mapping
    sm = await bp_svc.create_source_mapping(
        input_id=inp.id,
        req=CreateMappingRequest(name="src", description="...", jsonata_mapping="$"),
    )

    # Create a mapping job
    job = await mapping_job_svc.create_mapping_job(
        user_id=user.id,
        req=CreateMappingJobRequest(
            user_id=user.id,
            organization_id=org_id,
            input_definition_id=inp.id,
            name="Test Job",
            type=MappingJobType.STATIC,
        ),
    )

    # Create 2 executions
    exec1 = await mapping_job_svc.create_mapping_execution(
        req=CreateMappingExecutionRequest(
            mapping_job_id=job.id,
            source_mapping_id=sm.id,
            data_size_bytes=100,
            input_file_name="1.json",
        ),
        original_file_name="1.json",
        input_file_name="1.json",
    )
    await mapping_job_svc.update_mapping_execution(
        exec1.id,
        changes=UpdateMappingExecutionRequest(
            status=MappingStatus.SUCCESS,
            completed_at=datetime.now() - timedelta(days=2),
        ),
    )

    # case 2

    # Create source mapping
    sm2 = await bp_svc.create_source_mapping(
        input_id=inp.id,
        req=CreateMappingRequest(name="src", description="...", jsonata_mapping="$"),
    )

    # Create a mapping job
    job2 = await mapping_job_svc.create_mapping_job(
        user_id=user.id,
        req=CreateMappingJobRequest(
            user_id=user.id,
            organization_id=org_id,
            input_definition_id=inp.id,
            name="Test Job",
            type=MappingJobType.STATIC,
        ),
    )

    # Create 2 executions
    exec2 = await mapping_job_svc.create_mapping_execution(
        req=CreateMappingExecutionRequest(
            mapping_job_id=job2.id,
            source_mapping_id=sm2.id,
            data_size_bytes=150,
            input_file_name="1.json",
        ),
        original_file_name="1.json",
        input_file_name="1.json",
    )
    await mapping_job_svc.update_mapping_execution(
        exec2.id,
        changes=UpdateMappingExecutionRequest(
            status=MappingStatus.SUCCESS,
            completed_at=datetime.now() - timedelta(days=2),
        ),
    )

    # case 3

    # Create source mapping
    sm3 = await bp_svc.create_source_mapping(
        input_id=inp.id,
        req=CreateMappingRequest(name="src", description="...", jsonata_mapping="$"),
    )

    # Create a mapping job
    job3 = await mapping_job_svc.create_mapping_job(
        user_id=user.id,
        req=CreateMappingJobRequest(
            user_id=user.id,
            organization_id=org_id,
            input_definition_id=inp.id,
            name="Test Job",
            type=MappingJobType.STATIC,
        ),
    )

    # Create 2 executions
    exec3 = await mapping_job_svc.create_mapping_execution(
        req=CreateMappingExecutionRequest(
            mapping_job_id=job3.id,
            source_mapping_id=sm3.id,
            data_size_bytes=150,
            input_file_name="1.json",
        ),
        original_file_name="1.json",
        input_file_name="1.json",
    )
    await mapping_job_svc.update_mapping_execution(
        exec3.id,
        changes=UpdateMappingExecutionRequest(
            status=MappingStatus.SUCCESS,
            completed_at=datetime.now() - timedelta(days=20),
        ),
    )

    # Call user stats endpoint
    stats_resp = await async_client.get(f"/users/{user.id}/stats")
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    print(data)
    assert data["userId"] == user.id
    assert data["jobCount"] == 2
    assert data["bytes"] == 250
