from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

import bcrypt
from sqlalchemy import Connection, String, event, func, insert
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.blueprint import MappingBlueprint
    from app.model.job import MappingJob
    from app.model.log import Log
    from app.model.notification_preference import NotificationPreference
    from app.model.organization import OrganizationUser
    from app.model.session import Session
    from app.model.upload import Upload


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(60))
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )
    blocked_at: Mapped[Optional[datetime]] = mapped_column(default=None)

    # The blueprints this user has.
    blueprints: Mapped[list["MappingBlueprint"]] = relationship(
        "MappingBlueprint", back_populates="user"
    )

    # The organizations this user belongs to.
    organizations: Mapped[list["OrganizationUser"]] = relationship(
        "OrganizationUser",
        back_populates="user",
        foreign_keys="[OrganizationUser.user_id]",  # Explicitly specify the foreign key
    )

    # The sessions this user has.
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user")

    # The uploaded files this user has.
    uploads: Mapped[list["Upload"]] = relationship("Upload", back_populates="user")

    # The logs this user has.
    logs: Mapped[list["Log"]] = relationship("Log", back_populates="user")

    # The mapping jobs this user has.
    mapping_jobs: Mapped[list["MappingJob"]] = relationship(
        "MappingJob", back_populates="user"
    )

    notification_preferences: Mapped["NotificationPreference"] = relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @staticmethod
    def hash_password(plaintext: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plaintext.encode(), salt).decode()

    def verify_password(self, plaintext: str) -> bool:
        return bcrypt.checkpw(plaintext.encode(), self.password.encode())


@event.listens_for(User, "after_insert")
def create_notification_preferences(
    mapper: Mapper[User], connection: Connection, target: User
) -> None:
    """
    Create a new notification preference for the user after the user is created.
    """
    from app.model.notification_preference import NotificationPreference

    connection.execute(
        insert(NotificationPreference).values(
            user_id=target.id,
        )
    )
