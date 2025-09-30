from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.model.base import Base
from app.model.permission import Permission

if TYPE_CHECKING:
    from app.model.blueprint import MappingBlueprint
    from app.model.job import MappingJob
    from app.model.log import Log
    from app.model.user import User

from app.config import INVITE_EXPIRATION_DAYS


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    address: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    system_prompt: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    branch: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    model_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # The users belonging to this organization.
    users: Mapped[list["OrganizationUser"]] = relationship(
        "OrganizationUser", back_populates="organization"
    )

    # The roles defined for this organization.
    roles: Mapped[list["OrganizationRole"]] = relationship(
        "OrganizationRole", back_populates="organization"
    )

    # The blueprints associated with this organization.
    blueprints: Mapped[list["MappingBlueprint"]] = relationship()

    # The logs associated with this organization.
    logs: Mapped[list["Log"]] = relationship("Log", back_populates="organization")

    # The invites associated with this organization.
    invites: Mapped[list["Invite"]] = relationship(
        "Invite", back_populates="organization"
    )

    # The mapping jobs associated with this organization.
    mapping_jobs: Mapped[list["MappingJob"]] = relationship(
        "MappingJob", back_populates="organization", cascade="all, delete-orphan"
    )


class OrganizationUser(Base):
    __tablename__ = "organization_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    blacklist_reason: Mapped[Optional[str]] = mapped_column(nullable=True)
    blacklisted_at: Mapped[Optional[datetime]] = mapped_column(
        default=None, nullable=True
    )

    # The user associated with this organization.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], back_populates="organizations"
    )

    # The organization associated with this user.
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="users"
    )

    # The role this user has within this organization.
    role_id: Mapped[int] = mapped_column(
        ForeignKey("organization_roles.id", ondelete="CASCADE")
    )
    role: Mapped["OrganizationRole"] = relationship(
        "OrganizationRole", back_populates="users"
    )

    # Blacklisting fields
    blacklisted_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    blacklisted_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[blacklisted_by_id],
    )


class OrganizationRole(Base):
    __tablename__ = "organization_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # The organization this role belongs to.
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="roles"
    )

    # The permissions this role has.
    permissions: Mapped[list[RolePermission]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # The users who have this role.
    users: Mapped[list[OrganizationUser]] = relationship(
        "OrganizationUser", back_populates="role"
    )

    # The invites associated with this role.
    invites: Mapped[list["Invite"]] = relationship(
        "Invite", back_populates="role", cascade="all, delete-orphan"
    )

    @property
    def permissions_enum(self) -> list[Permission]:
        """Returns a list of enum values instead of RolePermission objects."""
        return [rp.permission for rp in self.permissions]


class RolePermission(Base):
    __tablename__ = "role_permissions"

    # The permission the permission added to the role.
    permission: Mapped["Permission"] = mapped_column(Enum(Permission), primary_key=True)

    # The role this instance belongs to.
    role_id: Mapped[int] = mapped_column(
        ForeignKey("organization_roles.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped["OrganizationRole"] = relationship(
        "OrganizationRole", back_populates="permissions"
    )


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    joined_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now() + timedelta(days=INVITE_EXPIRATION_DAYS),
    )

    # the user who created this invite
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # user: Mapped[User] = relationship("User")

    # The organization this invite is for.
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="invites"
    )

    # The role this invite is for.
    role_id: Mapped[int] = mapped_column(
        ForeignKey("organization_roles.id", ondelete="CASCADE")
    )
    role: Mapped["OrganizationRole"] = relationship(
        "OrganizationRole", back_populates="invites"
    )
