from __future__ import annotations

from typing import Annotated, Awaitable, Callable, Sequence

from fastapi import Depends

from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import (
    LogServiceDep,
    MappingBlueprintServiceDep,
    OrganizationServiceDep,
)
from app.exceptions import Unauthorized
from app.model.permission import Permission
from app.schema.mapping.blueprint import BlueprintResponse
from app.schema.user import UserResponse


async def _get_auth_blueprint(
    blueprint_id: int,
    user: AuthUserDep,
    bp_svc: MappingBlueprintServiceDep,
    org_svc: OrganizationServiceDep,
    logger: LogServiceDep,
) -> tuple[UserResponse, BlueprintResponse]:
    """Return *(user, blueprint)* or raise *Unauthorized*."""
    blueprint = await bp_svc.read_blueprint(blueprint_id)

    if not blueprint:
        await logger.warning(
            f"User {user.id} tried to access blueprint {blueprint.id} that does not exist",
            user_id=user.id,
            blueprint_id=blueprint_id,
            context={
                "blueprint_id": blueprint_id,
                "user_id": user.id,
            },
        )
        raise Unauthorized("Blueprint not found")

    if user.is_admin or blueprint.user_id == user.id:
        return user, blueprint

    if blueprint.organization_id is None:
        await logger.warning(
            f"User {user.id} tried to access blueprint {blueprint.id} that is not linked to an organization",
            user_id=user.id,
            blueprint_id=blueprint_id,
            context={
                "blueprint_id": blueprint.id,
                "user_id": user.id,
            },
        )
        raise Unauthorized("Not linked to an organization")

    if not await org_svc.user_is_organization_member(
        org_id=blueprint.organization_id, user_id=user.id
    ):
        await logger.warning(
            f"User {user.id} tried to access blueprint {blueprint.id} while the user is not part of the organization",
            user_id=user.id,
            blueprint_id=blueprint_id,
            context={
                "blueprint_id": blueprint.id,
                "user_id": user.id,
            },
        )
        raise Unauthorized("Not a member of the blueprint's organization")

    return user, blueprint


AuthBlueprintDep = Annotated[
    tuple[UserResponse, BlueprintResponse],
    Depends(_get_auth_blueprint),
]


async def _check_permissions(
    *,
    user: UserResponse,
    blueprint: BlueprintResponse,
    org_svc: OrganizationServiceDep,
    logger: LogServiceDep,
    required: Sequence[Permission],
) -> None:
    """Raise *Unauthorized* unless *user* holds every *required* permission."""
    if user.is_admin or blueprint.user_id == user.id:
        return

    if blueprint.organization_id is not None:
        perms = await org_svc.read_user_permissions(
            org_id=blueprint.organization_id,
            user_id=user.id,
        )

        missing_permissions = [p for p in required if p not in perms]
        if missing_permissions:
            await logger.warning(
                f"User {user.id} tried to access blueprint {blueprint.id} without required permissions",
                context={
                    "user_id": user.id,
                    "blueprint_id": blueprint.id,
                    "missing_permissions": [p.value for p in missing_permissions],
                },
                user_id=user.id,
                organization_id=blueprint.organization_id,
            )
            raise Unauthorized("Missing permission for this blueprint")


def make_blueprint_permissions_guard(
    *permissions: Permission,
) -> Callable[..., Awaitable[tuple[UserResponse, BlueprintResponse]]]:
    """Factory that returns a FastAPI dependency enforcing *permissions*."""

    async def _dep(
        blueprint_id: int,
        user: AuthUserDep,
        bp_svc: MappingBlueprintServiceDep,
        org_svc: OrganizationServiceDep,
        logger_svc: LogServiceDep,
    ) -> tuple[UserResponse, BlueprintResponse]:
        user, bp = await _get_auth_blueprint(
            blueprint_id=blueprint_id,
            user=user,
            bp_svc=bp_svc,
            org_svc=org_svc,
            logger=logger_svc,
        )

        if permissions:
            await _check_permissions(
                user=user,
                blueprint=bp,
                org_svc=org_svc,
                logger=logger_svc,
                required=list(permissions),
            )

        return user, bp

    return _dep
