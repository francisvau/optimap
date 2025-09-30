from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import status

from app.config import AUTH_KEY
from app.model.job import MappingJobType, MappingStatus
from app.model.organization import (
    Organization,
    OrganizationRole,
    OrganizationUser,
    RolePermission,
)
from app.model.permission import Permission
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
from app.schema.organization import (
    CreateOrganizationRequest,
    CreateOrganizationRoleRequest,
    InviteRequest,
    JoinRequest,
    OrganizationResponse,
    OrganizationRoleResponse,
    OrganizationUserResponse,
    UpdateOrganizationRequest,
    UpdateOrganizationRoleRequest,
    UpdateRoleRequest,
)


@pytest.mark.asyncio
async def test_create_organization(async_client, session_id):
    """Create succeeds when authed, duplicate 409, unauth 401."""
    # Unauth
    unauth = await async_client.post(
        "/organizations", json=CreateOrganizationRequest(name="X").model_dump()
    )
    assert unauth.status_code == status.HTTP_401_UNAUTHORIZED

    # First create
    async_client.cookies.set(AUTH_KEY, session_id)
    first = await async_client.post(
        "/organizations", json=CreateOrganizationRequest(name="X").model_dump()
    )
    assert first.status_code == status.HTTP_201_CREATED

    # Duplicate
    dup = await async_client.post(
        "/organizations", json=CreateOrganizationRequest(name="X").model_dump()
    )
    assert dup.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_read_organization(
    async_client, user, session_id, other_session_id, org_svc
):
    """Member gets 200, non-member 401."""
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="SeeCo")
    )

    # Non-member
    async_client.cookies.set(AUTH_KEY, other_session_id)
    assert (
        await async_client.get(f"/organizations/{org.id}")
    ).status_code == status.HTTP_401_UNAUTHORIZED

    # Member
    async_client.cookies.set(AUTH_KEY, session_id)
    ok = await async_client.get(f"/organizations/{org.id}")
    assert ok.status_code == status.HTTP_200_OK
    assert OrganizationResponse.model_validate(ok.json()).id == org.id


@pytest.mark.asyncio
async def test_update_and_delete_permission(
    async_client, user, session_id, other_session_id, org_svc
):
    """Owner with MANAGE_ORGANIZATION can patch/delete; others 401."""
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="UpDelCo")
    )

    async_client.cookies.set(AUTH_KEY, other_session_id)
    assert (
        await async_client.patch(
            f"/organizations/{org.id}",
            json=UpdateOrganizationRequest(description="x").model_dump(
                exclude_unset=True
            ),
        )
    ).status_code == status.HTTP_401_UNAUTHORIZED

    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.patch(
            f"/organizations/{org.id}",
            json=UpdateOrganizationRequest(description="new").model_dump(
                exclude_unset=True
            ),
        )
    ).status_code == status.HTTP_200_OK

    assert (
        await async_client.patch(
            f"/organizations/{org.id}/roles/{user.id}",
            json={"role": "NEW_ROLE"},
        )
    ).status_code == status.HTTP_400_BAD_REQUEST

    assert (
        await async_client.delete(f"/organizations/{org.id}")
    ).status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_invite_duplicate_and_join_flow(
    async_client, user, other_user, session_id, other_session_id, org_svc
):
    """Owner invites, duplicate 409, join succeeds, pending count drops."""
    # Create organization and role
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="InvCo")
    )

    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="editor", permissions=[])
    )

    # Invite user
    async_client.cookies.set(AUTH_KEY, session_id)
    first = await async_client.post(
        f"/organizations/{org.id}/invite",
        json=InviteRequest(user_email=other_user.email, role_id=role.id).model_dump(),
    )
    assert first.status_code == status.HTTP_201_CREATED

    # Check that no duplicate invites can be sent
    dup = await async_client.post(
        f"/organizations/{org.id}/invite",
        json=InviteRequest(user_email=other_user.email, role_id=role.id).model_dump(),
    )
    assert dup.status_code == status.HTTP_409_CONFLICT

    pend = await async_client.get(f"/organizations/{org.id}/pending-invites")
    assert len(pend.json()) == 1

    # Join the organization with the invite token
    invite = await org_svc.read_organization_invite(first.json()["id"])

    async_client.cookies.set(AUTH_KEY, other_session_id)
    joined = await async_client.post(
        "/organizations/join", json=JoinRequest(token=invite.token).model_dump()
    )
    assert joined.status_code == status.HTTP_201_CREATED

    # Check that there are no pending invites left
    async_client.cookies.set(AUTH_KEY, session_id)
    pend2 = await async_client.get(f"/organizations/{org.id}/pending-invites")
    assert len(pend2.json()) == 0


@pytest.mark.asyncio
async def test_organization_roles_crud(
    async_client, user, other_user, session_id, other_session_id, org_svc
):
    """Owner creates/updates/deletes role; non-manager 401; duplicate 409."""
    # Create organization
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="RoleCo")
    )

    # User can create a role
    async_client.cookies.set(AUTH_KEY, session_id)
    role = await async_client.post(
        f"/organizations/{org.id}/roles",
        json=CreateOrganizationRoleRequest(name="EdItOr", permissions=[]).model_dump(),
    )
    role = role.json()
    assert role["name"] == "editor"

    # User cannot create a duplicate role
    dup = await async_client.post(
        f"/organizations/{org.id}/roles",
        json=CreateOrganizationRoleRequest(name="EdItOr", permissions=[]).model_dump(),
    )
    assert dup.status_code == status.HTTP_409_CONFLICT

    # User can update the role
    upd = await async_client.patch(
        f"/organizations/{org.id}/roles/{role['id']}",
        json=UpdateOrganizationRoleRequest(name="editor2").model_dump(
            exclude_unset=True
        ),
    )

    assert upd.status_code == status.HTTP_200_OK
    assert upd.json()["name"] == "editor2"

    # Invite another user to the organization
    invite = await async_client.post(
        f"/organizations/{org.id}/invite",
        json=InviteRequest(
            user_email=other_user.email, role_id=role["id"]
        ).model_dump(),
    )
    assert "token" not in invite.json()

    # Join the organization with the invite token
    invite = await org_svc.read_organization_invite(invite.json()["id"])

    async_client.cookies.set(AUTH_KEY, other_session_id)
    response = await async_client.post(
        "/organizations/join", json=JoinRequest(token=invite.token).model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED

    async_client.cookies.set(AUTH_KEY, other_session_id)
    admin_role_id = 1
    response = await async_client.patch(
        f"/organizations/{org.id}/roles/{admin_role_id}",
        json=UpdateOrganizationRoleRequest(name="new_admin").model_dump(
            exclude_unset=True
        ),
    )

    # Other user cannot create roles in the organization.
    fail = await async_client.post(
        f"/organizations/{org.id}/roles",
        json=CreateOrganizationRoleRequest(name="x", permissions=[]).model_dump(),
    )
    assert fail.status_code == status.HTTP_401_UNAUTHORIZED

    # Owner user can delete the role (was assigned admin)
    async_client.cookies.set(AUTH_KEY, session_id)
    assert (
        await async_client.delete(f"/organizations/{org.id}/roles/{role['id']}")
    ).status_code == status.HTTP_204_NO_CONTENT

    # Test cannot delete the last role (admin role, assuming it's the only one initially)
    async_client.cookies.set(AUTH_KEY, session_id)
    # remove default role
    await async_client.delete(f"/organizations/{org.id}/roles/2")
    admin_role_id = 1  # Assuming the default admin role has id=1
    response = await async_client.delete(
        f"/organizations/{org.id}/roles/{admin_role_id}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json().get("detail")
        == "Cannot delete the last role in the organization"
    )

    # Test cannot delete admin role (even with other roles present)
    # Create a non-admin role to ensure multiple roles exist
    non_admin_role = await async_client.post(
        f"/organizations/{org.id}/roles",
        json=CreateOrganizationRoleRequest(name="member", permissions=[]).model_dump(),
    )
    assert non_admin_role.status_code == status.HTTP_201_CREATED
    response = await async_client.delete(
        f"/organizations/{org.id}/roles/{admin_role_id}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == "Cannot delete the admin role"


@pytest.mark.asyncio
async def test_organization_users_crud(
    async_client, user, other_user, session_id, other_session_id, org_svc
):
    """List, get, patch roles and remove with correct auth rules."""
    # Create organization
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="UserCo")
    )

    # User can create a role in the organization
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/organizations/{org.id}/roles",
        json=CreateOrganizationRoleRequest(name="member", permissions=[]).model_dump(),
    )
    role_id = response.json()["id"]

    # User can invite another user to the organization
    response = await async_client.post(
        f"/organizations/{org.id}/invite",
        json=InviteRequest(user_email=other_user.email, role_id=role_id).model_dump(),
    )
    invite = response.json()
    assert response.status_code == status.HTTP_201_CREATED

    # The other user can join the organization
    invite = await org_svc.read_organization_invite(invite["id"])
    async_client.cookies.set(AUTH_KEY, other_session_id)
    response = await async_client.post(
        "/organizations/join", json=JoinRequest(token=invite.token).model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED

    # The user can list users in the organization
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.get(f"/organizations/{org.id}/users")
    users = response.json()
    assert users[0]["user"]["id"] == user.id

    # The user can get details of the other user
    response = await async_client.get(f"/organizations/{org.id}/users/{other_user.id}")
    org_user = response.json()
    assert org_user["user"]["id"] == other_user.id

    # The user can update the other user's role
    response = await async_client.patch(
        f"/organizations/{org.id}/users/{other_user.id}",
        json=UpdateRoleRequest(role_id=role_id).model_dump(exclude_unset=True),
    )
    assert response.status_code == status.HTTP_200_OK

    # The user cannot remove themselves from the organization
    response = await async_client.delete(f"/organizations/{org.id}/users/{user.id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # The user can remove the other user from the organization
    response = await async_client.delete(
        f"/organizations/{org.id}/users/{other_user.id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    async_client.cookies.set(AUTH_KEY, other_session_id)

    # The other user cannot remove themselves from the organization
    response = await async_client.delete(f"/organizations/{org.id}/users/{user.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_organization_permissions(async_client, user, session_id, org_svc):
    """read_user_permissions returns MANAGE_USERS for admin."""
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="PermCo")
    )
    perms = await org_svc.read_user_permissions(org_id=org.id, user_id=user.id)
    assert Permission.MANAGE_USERS in perms


@pytest.mark.asyncio
async def test_organization_blacklist(
    populated_org: Organization, async_client, other_user, session_id, org_svc, session
):
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/organizations/{populated_org.id}/users/{other_user.id}/blacklist",
        json={"blacklist_reason": "not a Rosé fan"},
    )
    assert response.status_code == 204

    org_user = await org_svc.read_organization_user(
        org_id=populated_org.id, user_id=other_user.id
    )

    assert org_user.blacklisted_at is not None
    assert org_user.blacklist_reason == "not a Rosé fan"


@pytest.mark.asyncio
async def test_organization_whitelist(
    populated_org: Organization, async_client, other_user, session_id, org_svc, session
):
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/organizations/{populated_org.id}/users/{other_user.id}/blacklist",
        json={"blacklist_reason": "not a Rosé fan"},
    )
    assert response.status_code == 204

    response = await async_client.post(
        f"/organizations/{populated_org.id}/users/{other_user.id}/whitelist",
    )
    assert response.status_code == 204

    org_user = await org_svc.read_organization_user(
        org_id=populated_org.id, user_id=other_user.id
    )

    assert org_user.blacklisted_at is None
    assert org_user.blacklist_reason is None


@pytest.mark.asyncio
async def test_organization_invite_blacklisted_user(
    populated_org: Organization, async_client, other_user, session_id, org_svc, session
):
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/organizations/{populated_org.id}/users/{other_user.id}/blacklist",
        json={"blacklist_reason": "not a Rosé fan"},
    )
    assert response.status_code == 204

    response = await async_client.post(
        f"/organizations/{populated_org.id}/invite",
        json=InviteRequest(
            user_email=other_user.email, role_id=populated_org.id
        ).model_dump(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User is blacklisted from organization"


@pytest.mark.asyncio
async def test_organization_blacklist_user_acces_denied(
    populated_org: Organization,
    async_client,
    other_user,
    session_id,
    org_svc,
    other_session_id,
):
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        f"/organizations/{populated_org.id}/users/{other_user.id}/blacklist",
        json={"blacklist_reason": "not a Rosé fan"},
    )
    assert response.status_code == 204

    async_client.cookies.set(AUTH_KEY, other_session_id)
    response = await async_client.get(
        f"/organizations/{populated_org.id}/users",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User is blacklisted from organization"

    async_client.cookies.set(AUTH_KEY, other_session_id)
    response = await async_client.get(
        f"/organizations/{populated_org.id}",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User is blacklisted from organization"


@pytest.mark.asyncio
async def test_organization_user_response_model_validate_with_nested_permissions():
    """Test that OrganizationUserResponse correctly extracts Permission enums from nested RolePermission objects."""

    # Fake RolePermission entries
    role_permissions = [
        RolePermission(permission=Permission.MANAGE_USERS, role_id=1),
        RolePermission(permission=Permission.MANAGE_ORGANIZATION, role_id=1),
    ]

    # Fake OrganizationRole with those permissions
    role = OrganizationRole(id=1, name="admin", permissions=role_permissions)

    # Fake OrganizationUser containing the role
    user_obj = OrganizationUser(
        id=42,
        user_id=1,
        organization_id=99,
        created_at=datetime.now(timezone.utc),
        role=role,
        user=None,
        organization=None,
    )

    # Validate to schema
    schema = OrganizationUserResponse.model_validate(user_obj)

    # Assert role got flattened permissions
    assert schema.role is not None
    assert schema.role.permissions == [
        Permission.MANAGE_USERS,
        Permission.MANAGE_ORGANIZATION,
    ]
    assert isinstance(schema.role, OrganizationRoleResponse)


@pytest.mark.asyncio
async def test_get_organization_stats_endpoint(
    async_client, user, session_id, bp_svc, mapping_job_svc
):
    # Create an organization
    async_client.cookies.set(AUTH_KEY, session_id)
    response = await async_client.post(
        "/organizations",
        json=CreateOrganizationRequest(
            name="StatsOrg", description="Test stats"
        ).model_dump(),
    )
    assert response.status_code == 201
    org_id = response.json()["id"]

    # Create blueprint
    bp = await bp_svc.create_blueprint(
        req=CreateBlueprintRequest(
            name="StatsBP", description="desc", organization_id=org_id
        ),
        user_id=user.id,
    )

    # Create input definition
    inp_def = await bp_svc.create_input_definition(
        blueprint_id=bp.id,
        req=CreateInputDefinitionRequest(name="input"),
    )

    # Create source mapping
    sm = await bp_svc.create_source_mapping(
        input_id=inp_def.id,
        req=CreateMappingRequest(
            name="srcmap", description="desc", jsonata_mapping="$"
        ),
    )

    # Create a mapping job
    job = await mapping_job_svc.create_mapping_job(
        user_id=user.id,
        req=CreateMappingJobRequest(
            user_id=user.id,
            input_definition_id=inp_def.id,
            name="Job",
            type=MappingJobType.STATIC,
        ),
    )

    # Create recent execution
    recent_exec = await mapping_job_svc.create_mapping_execution(
        req=CreateMappingExecutionRequest(
            mapping_job_id=job.id,
            source_mapping_id=sm.id,
            data_size_bytes=200,
            input_file_name="recent.json",
        ),
        original_file_name="recent.json",
        input_file_name="recent.json",
    )
    await mapping_job_svc.update_mapping_execution(
        recent_exec.id,
        changes=UpdateMappingExecutionRequest(
            status=MappingStatus.SUCCESS, completed_at=datetime.now()
        ),
    )

    job = await mapping_job_svc.read_mapping_job(job.id, include=("executions",))
    print(len(job.executions))

    # Call stats endpoint
    stats_resp = await async_client.get(f"/organizations/{org_id}/stats")
    assert stats_resp.status_code == 200
    data = stats_resp.json()

    # Base org stats
    assert data["organizationId"] == org_id
    assert data["userCount"] == 1
    assert data["roleCount"] == 2
    assert data["pendingInviteCount"] == 0
    assert data["adminUserCount"] == 1

    assert data.get("jobCount", 1) == 0  # no executions started
    assert data.get("bytes", 0) >= 0  # no executiosn started
