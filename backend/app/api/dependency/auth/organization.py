from __future__ import annotations

from typing import Annotated, Awaitable, Callable, Sequence, Tuple

from fastapi import Depends

from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import OrganizationServiceDep
from app.exceptions import Unauthorized
from app.model.permission import Permission
from app.schema.organization import OrganizationResponse
from app.schema.user import UserResponse


async def _org_member(
    organization_id: int,
    user: AuthUserDep,
    svc: OrganizationServiceDep,
) -> tuple[UserResponse, OrganizationResponse]:
    """Return *(user, org)* if the requester belongs to the org (or is admin)."""
    org = await svc.read_organization(organization_id)

    if user.is_admin or await svc.user_is_organization_member(
        org_id=org.id, user_id=user.id
    ):
        return user, org

    raise Unauthorized("not a member of the organization")


async def _user_orgs(
    user: AuthUserDep,
    svc: OrganizationServiceDep,
) -> list[OrganizationResponse]:
    """All orgs an account can see (admins get everything)."""
    if user.is_admin:
        orgs = await svc.read_organizations()
    else:
        orgs = await svc.read_organizations_for_user(user.id)

    return list(orgs)


async def _ensure_perms(
    *,
    user: UserResponse,
    org: OrganizationResponse,
    svc: OrganizationServiceDep,
    need: Sequence[Permission],
) -> None:
    """Raise if *user* lacks every permission in *need*."""
    if user.is_admin:
        return

    have = await svc.read_user_permissions(org_id=org.id, user_id=user.id)

    if not all(p in have for p in need):
        raise Unauthorized("missing permission")


def make_org_permissions_guard(
    *permissions: Permission,
) -> Callable[..., Awaitable[Tuple[UserResponse, OrganizationResponse]]]:
    """Return a dependency that enforces *permissions* inside an org."""

    async def _dep(
        organization_id: int,
        user: AuthUserDep,
        svc: OrganizationServiceDep,
    ) -> tuple[UserResponse, OrganizationResponse]:
        user_, org = await _org_member(organization_id, user, svc)

        if permissions:
            await _ensure_perms(
                user=user_,
                org=org,
                svc=svc,
                need=list(permissions),
            )

        return user_, org

    return _dep


AuthOrganizationMemberDep = Annotated[
    tuple[UserResponse, OrganizationResponse],
    Depends(_org_member),
]

AuthAllOrganizationsDep = Annotated[
    list[OrganizationResponse],
    Depends(_user_orgs),
]
