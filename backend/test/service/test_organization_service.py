# tests/test_organization_service.py
from __future__ import annotations

import pytest

from app.exceptions import BadRequest, DuplicateEntity, EntityNotPresent
from app.model.permission import Permission
from app.schema.organization import (
    CreateOrganizationRequest,
    CreateOrganizationRoleRequest,
    UpdateOrganizationRequest,
    UpdateOrganizationRoleRequest,
)


@pytest.mark.asyncio
async def test_create_organization_and_admin_role(org_svc, user):
    req = CreateOrganizationRequest(name="Acme", description="acme")
    org = await org_svc.create_organization(user_id=user.id, req=req)
    assert org.name == "Acme"

    roles = await org_svc.read_organization_roles(org.id)
    assert roles[0].name == "admin"
    assert await org_svc.user_is_organization_member(org_id=org.id, user_id=user.id)


@pytest.mark.asyncio
async def test_duplicate_org_name(org_svc, user):
    await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Dup", description="d")
    )
    with pytest.raises(DuplicateEntity):
        await org_svc.create_organization(
            user_id=user.id, req=CreateOrganizationRequest(name="Dup", description="x")
        )


@pytest.mark.asyncio
async def test_read_organization_by_id_and_name(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="ReadMe", description="d")
    )
    assert (await org_svc.read_organization(org.id, include=())).name == "ReadMe"
    assert (await org_svc.read_organization_by_name("ReadMe", include=())).id == org.id


@pytest.mark.asyncio
async def test_update_organization(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Upd", description="d")
    )
    upd = await org_svc.update_organization(
        org.id, changes=UpdateOrganizationRequest(description="new")
    )
    assert upd.description == "new"


@pytest.mark.asyncio
async def test_delete_organization(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Del", description="d")
    )
    await org_svc.delete_organization(org.id)
    with pytest.raises(EntityNotPresent):
        await org_svc.read_organization(org.id)


@pytest.mark.asyncio
async def test_list_organizations(org_svc, user):
    await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Org1", description="d")
    )
    await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Org2", description="d")
    )
    assert len(await org_svc.read_organizations()) >= 2


@pytest.mark.asyncio
async def test_list_organizations_for_user(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="UserOrg", description="d")
    )
    orgs = await org_svc.read_organizations_for_user(user.id)
    assert any(o.id == org.id for o in orgs)


@pytest.mark.asyncio
async def test_delete_user_from_organization(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Kick", description="d")
    )
    await org_svc.delete_organization_user(org_id=org.id, user_id=user.id)
    assert not await org_svc.user_is_organization_member(org_id=org.id, user_id=user.id)


@pytest.mark.asyncio
async def test_delete_user_not_member_raises(org_svc):
    with pytest.raises(EntityNotPresent):
        await org_svc.delete_organization_user(org_id=999, user_id=999)


@pytest.mark.asyncio
async def test_list_organization_users(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Members", description="d")
    )
    users = await org_svc.read_organization_users(org.id)
    assert users[0].user.id == user.id


@pytest.mark.asyncio
async def test_read_organization_user(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="ReadUser", description="d")
    )
    ou = await org_svc.read_organization_user(org_id=org.id, user_id=user.id)
    assert ou.user.id == user.id


@pytest.mark.asyncio
async def test_user_is_member_boolean(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="BoolOrg", description="d")
    )
    assert await org_svc.user_is_organization_member(org_id=org.id, user_id=user.id)


@pytest.mark.asyncio
async def test_create_organization_role(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="RoleOrg", description="d")
    )
    role = await org_svc.create_organization_role(
        org.id,
        req=CreateOrganizationRoleRequest(
            name="editor", permissions=[Permission.MANAGE_USERS]
        ),
    )
    assert role.name == "editor"


@pytest.mark.asyncio
async def test_duplicate_role_name(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="DupRoleOrg", description="d"),
    )

    await org_svc.create_organization_role(
        org.id,
        req=CreateOrganizationRoleRequest(name="dup", permissions=[]),
    )

    with pytest.raises(DuplicateEntity):
        await org_svc.create_organization_role(
            org.id,
            req=CreateOrganizationRoleRequest(name="dup", permissions=[]),
        )


@pytest.mark.asyncio
async def test_read_organization_role(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="ReadRoleOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="visitor", permissions=[])
    )
    fetched = await org_svc.read_organization_role(role.id, org_id=org.id)
    assert fetched.id == role.id


@pytest.mark.asyncio
async def test_update_organization_role(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="UpdRoleOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="old", permissions=[])
    )
    upd = await org_svc.update_organization_role(
        role.id,
        org_id=org.id,
        changes=UpdateOrganizationRoleRequest(
            name="new", permissions=[Permission.MANAGE_USERS]
        ),
    )
    assert upd.name == "new"
    assert Permission.MANAGE_USERS in upd.permissions


@pytest.mark.asyncio
async def test_delete_organization_role(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="DelRoleOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="todel", permissions=[])
    )
    await org_svc.delete_organization_role(role.id, org_id=org.id)
    roles = await org_svc.read_organization_roles(org.id)
    assert all(r.id != role.id for r in roles)


@pytest.mark.asyncio
async def test_list_organization_roles(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="ListRolesOrg", description="d"),
    )
    await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="role1", permissions=[])
    )
    roles = await org_svc.read_organization_roles(org.id)
    assert len(roles) >= 2  # admin + role1


@pytest.mark.asyncio
async def test_update_organization_user_role(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="SetRoleOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="member", permissions=[])
    )
    updated = await org_svc.update_organization_user_role(
        user_id=user.id, org_id=org.id, role_id=role.id
    )
    assert role.id == updated.role.id


@pytest.mark.asyncio
async def test_read_user_permissions(org_svc, user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="PermOrg", description="d")
    )
    perms = await org_svc.read_user_permissions(org_id=org.id, user_id=user.id)
    assert Permission.MANAGE_ORGANIZATION in perms


@pytest.mark.asyncio
async def test_create_organization_invite(org_svc, user, other_user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="InviteOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="invite", permissions=[])
    )
    invite = await org_svc.create_organization_invite(
        user_email=other_user.email, org_id=org.id, role_id=role.id
    )
    assert invite.organization_id == org.id
    assert invite.email == other_user.email


@pytest.mark.asyncio
async def test_read_organization_invite(org_svc, user, other_user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="ReadInviteOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="invite", permissions=[])
    )
    invite = await org_svc.create_organization_invite(
        user_email=other_user.email, org_id=org.id, role_id=role.id
    )
    fetched = await org_svc.read_organization_invite_by_token(invite.token)
    assert fetched.id == invite.id
    assert fetched.organization_id == org.id


@pytest.mark.asyncio
async def test_accept_organization_invite(org_svc, user, other_user):
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="AcceptOrg", description="d"),
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="invite", permissions=[])
    )
    invite = await org_svc.create_organization_invite(
        user_email=other_user.email, org_id=org.id, role_id=role.id
    )
    accepted = await org_svc.accept_organization_invite(invite_id=invite.id)
    assert accepted.organization.id == org.id


@pytest.mark.asyncio
async def test_pending_invites(org_svc, user, other_user):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="PendOrg", description="d")
    )
    role = await org_svc.create_organization_role(
        org.id, req=CreateOrganizationRoleRequest(name="invite", permissions=[])
    )
    await org_svc.create_organization_invite(
        user_email=other_user.email, org_id=org.id, role_id=role.id
    )
    invites = await org_svc.read_pending_invites(org.id)
    assert len(invites) == 1


@pytest.mark.asyncio
async def test_entity_not_present_errors(org_svc):
    with pytest.raises(EntityNotPresent):
        await org_svc.read_organization(999)
    with pytest.raises(BadRequest):
        await org_svc.update_organization(999, changes=UpdateOrganizationRequest())
    with pytest.raises(EntityNotPresent):
        await org_svc.read_organization_role(999, org_id=999)
    with pytest.raises(EntityNotPresent):
        await org_svc.delete_organization(999)
    with pytest.raises(EntityNotPresent):
        await org_svc.read_organization_invite_by_token("nope")
    with pytest.raises(EntityNotPresent):
        await org_svc.read_organization_user(org_id=999, user_id=999)


@pytest.mark.asyncio
async def test_get_organization_stats(org_svc, user, other_user):
    # Create the organization
    org = await org_svc.create_organization(
        user_id=user.id,
        req=CreateOrganizationRequest(name="StatsOrg", description="testing stats"),
    )

    # Add a second role
    role = await org_svc.create_organization_role(
        org.id,
        req=CreateOrganizationRoleRequest(name="member", permissions=[]),
    )

    # Add another user with the new role
    # other_user = await org_svc.db.scalar(
    #     insert(user.__class__).values(email="other@example.com", first_name="test").returning(user.__class__)
    # )
    await org_svc.add_user_to_organization(
        user_id=other_user.id, org_id=org.id, role_id=role.id
    )

    # Create a pending invite
    await org_svc.create_organization_invite(
        user_email="rose@blackpink.com", org_id=org.id, role_id=role.id
    )

    # Run stats
    stats = await org_svc.get_organization_stats(org.id)

    assert stats.organization_id == org.id
    assert stats.user_count == 2
    assert stats.role_count == 3  # 2 roles + default
    assert stats.pending_invite_count == 1
    assert stats.admin_user_count == 1
