from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Iterable

from sqlalchemy import delete, extract, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import coalesce

from app.config import INVITE_EXPIRATION_DAYS
from app.exceptions import (
    BadRequest,
    DuplicateEntity,
    EntityNotPresent,
    OptimapApiError,
    Unauthorized,
)
from app.model.job import MappingJob, MappingJobExecution
from app.model.organization import (
    Invite,
    Organization,
    OrganizationRole,
    OrganizationUser,
    RolePermission,
)
from app.model.permission import Permission
from app.model.user import User
from app.schema.organization import (
    CreateOrganizationRequest,
    CreateOrganizationRoleRequest,
    InviteResponse,
    OrganizationResponse,
    OrganizationRoleResponse,
    OrganizationStatsResponse,
    OrganizationUserResponse,
    UpdateOrganizationRequest,
    UpdateOrganizationRoleRequest,
    UpdateOrganizationUserRequest,
)
from app.service.model import ModelService

if TYPE_CHECKING:
    pass

if TYPE_CHECKING:
    pass


class OrganizationService:
    """Business-level operations for organizations."""

    # ORGANIZATION_REL_DEFAULT = ("models",)
    # ORGANIZATION_REL_MAP = {}

    def __init__(self, db: AsyncSession, model_svc: ModelService) -> None:
        self.db = db
        self.model_svc = model_svc

    async def create_organization(
        self, *, user_id: int, req: CreateOrganizationRequest
    ) -> OrganizationResponse:
        """Add a new organization and make *creator* its admin."""
        # Check if the organization name is already used.
        stmt = select(Organization).where(Organization.name == req.name)

        if await self.db.scalar(stmt):
            raise DuplicateEntity("name already used")

        # Create the organization.
        result = await self.db.execute(
            insert(Organization)
            .values(req.model_dump(by_alias=False))
            .returning(Organization)
        )
        organization = result.scalar_one()

        # Create admin role.
        role = await self.create_organization_role(
            organization.id,
            req=CreateOrganizationRoleRequest(
                name="admin",
                permissions=[
                    Permission.MANAGE_USERS,
                    Permission.MANAGE_ORGANIZATION,
                ],
            ),
        )

        # Create default role.
        await self.create_organization_role(
            organization.id,
            req=CreateOrganizationRoleRequest(
                name="viewer",
                permissions=[
                    Permission.VIEW_BLUEPRINT,
                    Permission.VIEW_STATIC_JOB,
                ],
            ),
        )

        # Link creator as user with admin role
        await self.add_user_to_organization(
            user_id=user_id,
            org_id=organization.id,
            role_id=role.id,
        )

        return OrganizationResponse.model_validate(organization.to_dict())

    async def read_organization(
        self, org_id: int, *, include: Iterable[str] = ()
    ) -> OrganizationResponse:
        """Get one organization by id, error if missing."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )

        org = result.scalar_one_or_none()

        if not org:
            raise EntityNotPresent("organization not found")

        return OrganizationResponse.model_validate(org.to_dict())

    async def read_organization_by_name(
        self, name: str, include: Iterable[str] = ()
    ) -> OrganizationResponse:
        """Get one organization by name, error if missing."""
        result = await self.db.execute(
            select(Organization).where(Organization.name == name)
        )

        org = result.scalar_one_or_none()

        if not org:
            raise EntityNotPresent("organization not found")

        return OrganizationResponse.model_validate(org.to_dict())

    async def update_organization(
        self, org_id: int, *, changes: UpdateOrganizationRequest
    ) -> OrganizationResponse:
        """Patch organization fields given in *changes* dict."""
        values = changes.model_dump(exclude_unset=True, by_alias=False)

        if not values:
            raise BadRequest("no changes provided")

        updated = await self.db.scalar(
            update(Organization)
            .where(Organization.id == org_id)
            .values(values)
            .returning(Organization)
        )

        if not updated:
            raise EntityNotPresent("Blueprint not found")

        return OrganizationResponse.model_validate(updated.to_dict())

    async def delete_organization(self, org_id: int) -> None:
        """Remove an organization permanently."""
        deleted = await self.db.execute(
            delete(Organization).where(Organization.id == org_id)
        )

        if deleted.rowcount == 0:
            raise EntityNotPresent("organization not found")

    async def read_organizations(self) -> list[OrganizationResponse]:
        """Return every organization (use with care)."""
        organizations = await self.db.scalars(select(Organization))

        return [
            OrganizationResponse.model_validate(res.to_dict()) for res in organizations
        ]

    async def read_organizations_for_user(
        self, user_id: int
    ) -> list[OrganizationResponse]:
        """Return every organization a user belongs to."""
        organizations = await self.db.scalars(
            select(Organization)
            .join(OrganizationUser)
            .filter(
                OrganizationUser.user_id == user_id,
                OrganizationUser.blacklisted_at.is_(None),
            )
        )

        return [
            OrganizationResponse.model_validate(res.to_dict()) for res in organizations
        ]

    async def attach_model_to_organization(
        self, *, org_id: int, model_id: str
    ) -> OrganizationResponse:
        """Attach a model to an organization."""
        # Check if the organization exists.
        org = await self.db.scalar(
            select(Organization).where(Organization.id == org_id)
        )

        if not org:
            raise EntityNotPresent("organization not found")

        # Check if the model is already attached.
        existing = model_id in org.model_ids

        if existing:
            raise DuplicateEntity("model already attached to organization")

        # Attach the model to the organization.
        org = await self.db.scalar(
            update(Organization)
            .where(Organization.id == org_id)
            .values(model_ids=org.model_ids + [model_id])
            .returning(Organization)
        )

        if not org:
            raise EntityNotPresent("organization not found")

        return OrganizationResponse.model_validate(org.to_dict())

    async def detach_model_from_organization(
        self, *, org_id: int, model_id: str
    ) -> OrganizationResponse:
        """Detach a model from an organization."""
        # Check if the organization exists.
        org = await self.db.scalar(
            select(Organization).where(Organization.id == org_id)
        )

        if not org:
            raise EntityNotPresent("organization not found")

        # Check if the model is already attached.
        existing = model_id in org.model_ids

        if not existing:
            raise EntityNotPresent("model not attached to organization")

        # Detach the model from the organization.
        org.model_ids.remove(model_id)
        await self.db.commit()

        return OrganizationResponse.model_validate(org.to_dict())

    async def delete_organization_user(self, *, org_id: int, user_id: int) -> None:
        """Detach a user from an organization."""
        is_deleted = await self.db.execute(
            delete(OrganizationUser).filter_by(user_id=user_id, organization_id=org_id)
        )

        if is_deleted.rowcount == 0:
            raise EntityNotPresent("user not found")

    async def read_organization_users(
        self, org_id: int
    ) -> list[OrganizationUserResponse]:
        """Return every user in an organization."""
        users = await self.db.scalars(
            select(OrganizationUser)
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.role).selectinload(
                    OrganizationRole.permissions,
                ),
            )
            .filter_by(organization_id=org_id)
        )

        return [
            OrganizationUserResponse.model_validate(
                u.to_dict()
                | {
                    "role": OrganizationRoleResponse.model_validate(
                        u.role.to_dict()
                        | {
                            "permissions": [p.permission for p in u.role.permissions],
                        }
                    ),
                }
            )
            for u in users
        ]

    async def read_organization_user(
        self, *, org_id: int, user_id: int
    ) -> OrganizationUserResponse:
        """Return the OrganizationUser link or raise."""
        user = await self.db.scalar(
            select(OrganizationUser)
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.role).selectinload(
                    OrganizationRole.permissions
                ),
            )
            .where(
                OrganizationUser.user_id == user_id,
                OrganizationUser.organization_id == org_id,
            )
        )

        if not user:
            raise EntityNotPresent("user not found in organization")

        return OrganizationUserResponse.model_validate(
            user.to_dict()
            | {
                "role": OrganizationRoleResponse.model_validate(
                    user.role.to_dict()
                    | {
                        "permissions": [p.permission for p in user.role.permissions],
                    }
                ),
            }
        )

    async def user_is_organization_member(self, *, org_id: int, user_id: int) -> bool:
        """Quick membership boolean."""
        result = await self.db.scalar(
            select(OrganizationUser).where(
                OrganizationUser.user_id == user_id,
                OrganizationUser.organization_id == org_id,
            )
        )

        if result is None:
            return False
        elif result.blacklisted_at is not None:
            raise Unauthorized("User is blacklisted from organization")

        return True

    async def read_organization_role(
        self, role_id: int, *, org_id: int
    ) -> OrganizationRoleResponse:
        """Return the OrganizationRole link or raise."""
        role = await self.db.scalar(
            select(OrganizationRole)
            .options(selectinload(OrganizationRole.permissions))
            .where(
                OrganizationRole.id == role_id,
                OrganizationRole.organization_id == org_id,
            )
        )

        if not role:
            raise EntityNotPresent("role not found")

        return OrganizationRoleResponse.model_validate(role)

    async def create_organization_role(
        self,
        org_id: int,
        *,
        req: CreateOrganizationRoleRequest,
    ) -> OrganizationRoleResponse:
        """Add a role with given permissions."""
        # Check if the role already exists.
        existing = await self.db.scalar(
            select(OrganizationRole).where(
                OrganizationRole.organization_id == org_id,
                OrganizationRole.name == req.name,
            )
        )

        if existing is not None:
            raise DuplicateEntity("role with that name already exists")

        # Add the role with its permissions to the organization.
        org = await self.read_organization(org_id, include=())

        values = req.model_dump(by_alias=False, exclude={"permissions"}) | {
            "organization_id": org.id,
        }

        role = await self.db.scalar(
            insert(OrganizationRole).values(values).returning(OrganizationRole)
        )

        if role is None:
            raise OptimapApiError("Could not create organization role.")

        # Add the permissions to the role.
        if req.permissions:
            await self.db.execute(
                insert(RolePermission).values(
                    [
                        {
                            "role_id": role.id,
                            "permission": p,
                        }
                        for p in req.permissions
                    ]
                )
            )

        await self.db.refresh(role, attribute_names=["permissions"])

        return OrganizationRoleResponse.model_validate(
            role.to_dict()
            | {
                "permissions": [p.permission for p in role.permissions],
            }
        )

    async def update_organization_role(
        self, role_id: int, *, org_id: int, changes: UpdateOrganizationRoleRequest
    ) -> OrganizationRoleResponse:
        """Rename role and/or replace its permissions."""

        role_name = await self.db.scalar(
            select(OrganizationRole.name).where(
                OrganizationRole.id == role_id,
                OrganizationRole.organization_id == org_id,
            )
        )
        if role_name and role_name.lower() == "admin":
            raise BadRequest("Cannot update the admin role")

        # Update the role meta.
        values = changes.model_dump(
            exclude_unset=True, by_alias=False, exclude={"permissions"}
        )

        updated = await self.db.scalar(
            update(OrganizationRole)
            .where(
                OrganizationRole.id == role_id,
                OrganizationRole.organization_id == org_id,
            )
            .values(values)
            .returning(OrganizationRole)
        )

        if not updated:
            raise EntityNotPresent("role not found")

        # Update the permissions if they are provided.
        if changes.permissions is not None:
            await self.db.execute(delete(RolePermission).filter_by(role_id=updated.id))

            await self.db.execute(
                insert(RolePermission).values(
                    [
                        {
                            "role_id": updated.id,
                            "permission": p,
                        }
                        for p in changes.permissions
                    ]
                )
            )

        # Refresh the role to get the new permissions.
        await self.db.refresh(updated, attribute_names=["permissions"])

        return OrganizationRoleResponse.model_validate(
            updated.to_dict()
            | {
                "permissions": [p.permission for p in updated.permissions],
            }
        )

    async def delete_organization_role(self, role_id: int, *, org_id: int) -> None:
        """Remove a role from the organization."""

        role_count = (
            await self.db.scalar(
                select(func.count())
                .select_from(OrganizationRole)
                .where(OrganizationRole.organization_id == org_id)
            )
            or 0
        )
        if role_count <= 1:
            raise BadRequest("Cannot delete the last role in the organization")

        is_admin = await self.db.scalar(
            select(OrganizationRole.name).where(
                OrganizationRole.id == role_id,
                OrganizationRole.organization_id == org_id,
            )
        )
        if is_admin and is_admin.lower() == "admin":
            raise BadRequest("Cannot delete the admin role")

        deleted = await self.db.execute(
            delete(OrganizationRole).where(
                OrganizationRole.id == role_id,
                OrganizationRole.organization_id == org_id,
            )
        )

        if not deleted.rowcount:
            raise EntityNotPresent("role not found")

    async def read_organization_roles(
        self, org_id: int
    ) -> list[OrganizationRoleResponse]:
        """List every role in an organization."""
        result = await self.db.scalars(
            select(OrganizationRole)
            .filter_by(organization_id=org_id)
            .options(selectinload(OrganizationRole.permissions))
        )

        return [
            OrganizationRoleResponse.model_validate(
                r.to_dict()
                | {
                    "permissions": [p.permission for p in r.permissions],
                }
            )
            for r in result
        ]

    async def update_organization_user_role(
        self,
        user_id: int,
        *,
        org_id: int,
        role_id: int,
    ) -> OrganizationUserResponse:
        """Replace a member's role in an organization."""
        updated = await self.db.scalar(
            update(OrganizationUser)
            .where(
                OrganizationUser.user_id == user_id,
                OrganizationUser.organization_id == org_id,
            )
            .values(role_id=role_id)
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.role).selectinload(
                    OrganizationRole.permissions,
                ),
            )
            .returning(OrganizationUser)
        )

        if updated is None:
            raise EntityNotPresent("user not found")

        return OrganizationUserResponse.model_validate(updated.to_dict())

    async def _invite_with_email(self, invite: Invite) -> dict[str, Any]:
        email = await self.db.scalar(
            select(User.email).where(User.email == invite.email)
        )
        data = invite.to_dict()
        data["email"] = email
        return data

    async def read_user_permissions(
        self, *, org_id: int, user_id: int
    ) -> list[Permission]:
        """Return flattened list of a user's permissions."""
        perms = await self.db.scalars(
            select(RolePermission.permission)
            .select_from(OrganizationUser)
            .join(OrganizationRole, OrganizationUser.role_id == OrganizationRole.id)
            .join(RolePermission, RolePermission.role_id == OrganizationRole.id)
            .where(
                OrganizationUser.user_id == user_id,
                OrganizationUser.organization_id == org_id,
            )
        )

        return list(perms)

    async def create_organization_invite(
        self, *, user_email: str, org_id: int, role_id: int
    ) -> InviteResponse:
        """Create a join invite and return its token."""
        # Check if the user exists.
        user_id = await self.db.scalar(
            select(User.id).where(
                User.email == user_email,
            )
        )

        if user_id is not None:
            # performs checks if the user is already registered or invited
            # Check if user was already invited.
            already_invited = await self.db.scalar(
                select(OrganizationUser).where(
                    OrganizationUser.user_id == user_id,
                    OrganizationUser.organization_id == org_id,
                )
            )

            existing_invite = await self.db.scalar(
                select(Invite).where(
                    Invite.email == user_email,
                    Invite.organization_id == org_id,
                    Invite.expires_at > datetime.now(),
                )
            )

            if already_invited and already_invited.blacklisted_at is not None:
                raise Unauthorized("User is blacklisted from organization")

            if existing_invite or already_invited:
                raise DuplicateEntity("User with email {email} is already invited.")

        # Create the invite.
        expires_at = datetime.now() + timedelta(days=INVITE_EXPIRATION_DAYS)
        token = str(uuid.uuid4())

        invite = await self.db.scalar(
            insert(Invite)
            .values(
                {
                    "email": user_email,
                    "organization_id": org_id,
                    "role_id": role_id,
                    "expires_at": expires_at,
                    "token": token,
                }
            )
            .returning(Invite)
        )

        if invite is None:
            raise OptimapApiError("Could not create invite for user.")

        # Add the missing email field manually
        invite_data = invite.to_dict()

        return InviteResponse.model_validate(invite_data)

    async def read_organization_invite(self, invite_id: int) -> InviteResponse:
        """Lookup an invite by its id."""
        invite = await self.db.scalar(select(Invite).filter_by(id=invite_id))

        if not invite:
            raise EntityNotPresent("invite not found")

        return InviteResponse.model_validate(await self._invite_with_email(invite))

    async def read_organization_invite_by_token(self, token: str) -> InviteResponse:
        """Lookup an invite by its token."""
        invite = await self.db.scalar(select(Invite).filter_by(token=token))
        if not invite:
            raise EntityNotPresent("invite not found")

        return InviteResponse.model_validate(await self._invite_with_email(invite))

    async def add_user_to_organization(
        self, *, user_id: int, org_id: int, role_id: int
    ) -> OrganizationUserResponse:
        """Add a user to an organization."""
        user = await self.db.scalar(
            insert(OrganizationUser)
            .values(
                user_id=user_id,
                organization_id=org_id,
                role_id=role_id,
            )
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.organization),
                selectinload(OrganizationUser.role).selectinload(
                    OrganizationRole.permissions,
                ),
            )
            .returning(OrganizationUser)
        )

        if user is None:
            raise OptimapApiError("Could not add user to organization.")

        return OrganizationUserResponse.model_validate(
            user.to_dict()
            | {
                "role": OrganizationRoleResponse.model_validate(
                    user.role.to_dict()
                    | {
                        "permissions": [p.permission for p in user.role.permissions],
                    }
                ),
            }
        )

    async def accept_organization_invite(
        self,
        *,
        invite_id: int,
    ) -> OrganizationUserResponse:
        """Add user to org and mark invite as used."""
        invite = await self.db.scalar(
            select(Invite)
            .filter_by(id=invite_id)
            .options(selectinload(Invite.organization))
        )

        if not invite:
            raise EntityNotPresent("invite not found")

        if invite.expires_at < datetime.now():
            raise Unauthorized("invite expired")

        if invite.joined_at is not None:
            raise Unauthorized("invite already accepted")

        # Mark the invite as used.
        await self.db.execute(
            update(Invite)
            .where(Invite.id == invite_id)
            .values(joined_at=datetime.now())
        )
        existing_user = await self.db.scalar(
            select(User).where(User.email == invite.email)
        )
        if not existing_user:
            raise EntityNotPresent("user not found")

        # Add the user to the organization.
        user = await self.add_user_to_organization(
            user_id=existing_user.id,
            org_id=invite.organization_id,
            role_id=invite.role_id,
        )

        return user

    async def read_pending_invites(self, org_id: int) -> list[InviteResponse]:
        """Return invites that are not expired and not yet used."""
        invites = await self.db.scalars(
            select(Invite).filter(
                Invite.organization_id == org_id,
                Invite.joined_at.is_(None),
                Invite.expires_at > datetime.now(),
            )
        )

        return [
            InviteResponse.model_validate(await self._invite_with_email(i))
            for i in invites
        ]

    async def update_organization_user(
        self, *, org_id: int, user_id: int, changes: UpdateOrganizationUserRequest
    ) -> OrganizationUserResponse:
        """Update a user's membership details within an organization."""
        values = changes.model_dump(exclude_unset=True, by_alias=False)

        if not values:
            raise BadRequest("no changes provided")

        updated = await self.db.scalar(
            update(OrganizationUser)
            .where(
                OrganizationUser.organization_id == org_id,
                OrganizationUser.user_id == user_id,
            )
            .values(values)
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.role).selectinload(
                    OrganizationRole.permissions,
                ),
            )
            .returning(OrganizationUser)
        )

        if updated is None:
            raise EntityNotPresent("organization user not found")

        return OrganizationUserResponse.model_validate(
            updated.to_dict()
            | {
                "role": OrganizationRoleResponse.model_validate(
                    updated.role.to_dict()
                    | {
                        "permissions": [p.permission for p in updated.role.permissions],
                    }
                ),
            }
        )

    async def get_organization_stats(self, org_id: int) -> OrganizationStatsResponse:
        """Return statistics about an organization."""
        # Verify organisation exists
        if not await self.db.scalar(
            select(Organization.id).where(Organization.id == org_id).limit(1)
        ):
            raise EntityNotPresent("organization not found")

        # User counts (total and admins)
        user_counts = await self.db.execute(
            select(
                func.count()
                .filter(OrganizationUser.blacklisted_at.is_(None))
                .label("total_users"),
                func.count()
                .filter(
                    OrganizationUser.blacklisted_at.is_(None),
                    func.lower(OrganizationRole.name) == "admin",
                )
                .label("admin_users"),
            )
            .select_from(OrganizationUser)
            .join(OrganizationRole, OrganizationUser.role_id == OrganizationRole.id)
            .where(OrganizationUser.organization_id == org_id)
        )
        user_total, admin_total = user_counts.one()

        # Role count
        role_total = await self.db.scalar(
            select(func.count())
            .select_from(OrganizationRole)
            .where(OrganizationRole.organization_id == org_id)
        )

        # Pending invites
        invite_total = await self.db.scalar(
            select(func.count())
            .select_from(Invite)
            .where(
                Invite.organization_id == org_id,
                Invite.joined_at.is_(None),
                Invite.expires_at > datetime.now(),
            )
        )

        # 5. Execution statistics
        exec_stats = await self.db.execute(
            select(
                coalesce(func.count(), 0).label("job_count"),
                coalesce(func.sum(MappingJobExecution.data_size_bytes), 0).label(
                    "total_bytes"
                ),
                coalesce(
                    func.min(
                        extract(
                            "epoch",
                            MappingJobExecution.completed_at
                            - MappingJobExecution.started_at,
                        )
                    ),
                    0,
                ).label("min_exec"),
                coalesce(
                    func.max(
                        extract(
                            "epoch",
                            MappingJobExecution.completed_at
                            - MappingJobExecution.started_at,
                        )
                    ),
                    0,
                ).label("max_exec"),
                coalesce(
                    func.avg(
                        extract(
                            "epoch",
                            MappingJobExecution.completed_at
                            - MappingJobExecution.started_at,
                        )
                    ),
                    0,
                ).label("avg_exec"),
            )
            .select_from(MappingJobExecution)
            .join(MappingJob, MappingJob.id == MappingJobExecution.mapping_job_id)
            .where(
                MappingJob.organization_id == org_id,
                MappingJobExecution.started_at.is_not(None),
                MappingJobExecution.completed_at.is_not(None),
            )
        )

        job_cnt, total_bytes, min_exec, max_exec, avg_exec = exec_stats.one()

        return OrganizationStatsResponse(
            organization_id=org_id,
            user_count=user_total,
            admin_user_count=admin_total,
            role_count=role_total,
            pending_invite_count=invite_total,
            job_count=job_cnt,
            bytes=total_bytes,
            min_execution_time=round(min_exec, 2),
            max_execution_time=round(max_exec, 2),
            avg_execution_time=round(avg_exec, 2),
        )

    async def get_organization_admin_users(
        self, org_id: int
    ) -> list[OrganizationUserResponse]:
        """Return users in the organization who have the 'admin' role."""
        users = await self.db.scalars(
            select(OrganizationUser)
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.role).selectinload(
                    OrganizationRole.permissions
                ),
            )
            .where(
                OrganizationUser.organization_id == org_id,
                OrganizationUser.blacklisted_at.is_(None),
            )
        )

        admin_users = [
            OrganizationUserResponse.model_validate(
                u.to_dict()
                | {
                    "role": OrganizationRoleResponse.model_validate(
                        u.role.to_dict()
                        | {
                            "permissions": [p.permission for p in u.role.permissions],
                        }
                    )
                }
            )
            for u in users
            if u.role and u.role.name.lower() == "admin"
        ]

        return admin_users
