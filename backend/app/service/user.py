from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.api.dependency.service import MappingJobServiceDep
from app.exceptions import (
    DuplicateEntity,
    EntityNotPresent,
    OptimapApiError,
    Unauthorized,
)
from app.model.user import User
from app.schema.user import (
    UserCreateRequest,
    UserResponse,
    UserStatsResponse,
    UserUpdateRequest,
)
from app.util.jwt import decode_jwt_token


class UserService:
    """Business logic around user accounts."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(self, req: UserCreateRequest) -> UserResponse:
        """Create a new user account."""
        existing = await self.db.scalar(select(User).where(User.email == req.email))

        if existing:
            raise DuplicateEntity("Email already registered")

        values = req.model_dump(by_alias=False, exclude={"token"}) | {
            "password": User.hash_password(req.password),
        }

        user = await self.db.scalar(insert(User).values(values).returning(User))
        if not user:
            raise OptimapApiError("Could not create the new user.")

        return UserResponse.model_validate(user.to_dict())

    async def update_user(
        self, user_id: int, *, changes: UserUpdateRequest
    ) -> UserResponse:
        """Update user account details."""
        values = changes.model_dump(by_alias=False, exclude_unset=True)

        updated = await self.db.scalar(
            update(User).where(User.id == user_id).values(values).returning(User)
        )

        if updated is None:
            raise EntityNotPresent("User not found")

        return UserResponse.model_validate(updated.to_dict())

    async def read_user(self, user_id: int) -> UserResponse:
        """Return the user identified by *user_id* or raise."""
        user = await self.db.scalar(select(User).where(User.id == user_id))

        if user is None:
            raise EntityNotPresent("User not found")

        return UserResponse.model_validate(user.to_dict())

    async def read_user_by_email(self, email: str) -> UserResponse:
        """Return the user identified by *email* or raise."""
        user = await self.db.scalar(select(User).where(User.email == email))

        if user is None:
            raise EntityNotPresent("User not found")

        return UserResponse.model_validate(user.to_dict())

    async def read_user_by_email_and_password(
        self, email: str, password: str
    ) -> UserResponse:
        """Return the user identified by *email* and *password* or raise."""
        user = await self.db.scalar(select(User).where(User.email == email))

        if user is None:
            raise EntityNotPresent("User not found")

        if not user.verify_password(password):
            raise Unauthorized("Invalid password")

        return UserResponse.model_validate(user.to_dict())

    async def update_user_password(self, email: str, new_password: str) -> UserResponse:
        """Set a new password for the user identified by *email*."""
        user = await self.db.scalar(
            update(User)
            .where(User.email == email)
            .values(password=User.hash_password(new_password))
            .returning(User)
        )

        if user is None:
            raise EntityNotPresent("User not found")

        return UserResponse.model_validate(user.to_dict())

    async def update_user_verify(self, email: str) -> UserResponse:
        """Verify the user identified by *email*."""
        user = await self.db.scalar(
            update(User)
            .where(User.email == email)
            .values(is_verified=True)
            .returning(User)
        )

        if user is None:
            raise EntityNotPresent("User not found")

        return UserResponse.model_validate(user.to_dict())

    async def reset_password_by_token(
        self, token: str, new_password: str
    ) -> UserResponse:
        """Reset the password for the user identified by *token*."""
        email = decode_jwt_token(token).get("sub")

        if not email:
            raise Unauthorized("Invalid reset token")

        return await self.update_user_password(email, new_password)

    async def verify_user_by_token(self, token: str) -> UserResponse:
        """Verify the user identified by *token*."""
        email = decode_jwt_token(token).get("sub")

        if not email:
            raise Unauthorized("Invalid verification token")

        return await self.update_user_verify(email)

    async def read_all_users(self) -> list[UserResponse]:
        """Return all users (admin only)."""
        result = await self.db.execute(select(User))
        users = result.scalars().all()
        return [UserResponse.model_validate(user.to_dict()) for user in users]

    async def get_user_stats(
        self, user_id: int, job_svc: MappingJobServiceDep
    ) -> UserStatsResponse:
        # Optional: validate user exists
        user = await self.db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise EntityNotPresent("user not found")

        executions = await job_svc.read_executions_for_user(user_id, days=7)
        job_count = len(executions)
        bytes = sum(
            e.data_size_bytes for e in executions if e.data_size_bytes is not None
        )

        return UserStatsResponse(
            user_id=user_id,
            job_count=job_count or 0,
            bytes=bytes or 0,
        )
