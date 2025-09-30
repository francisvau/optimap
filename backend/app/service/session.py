from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AUTH_SESSION_EXPIRE
from app.exceptions import EntityNotPresent, OptimapApiError
from app.model.session import Session as AuthSession
from app.model.user import User
from app.schema.session import AuthSessionResponse
from app.schema.user import UserResponse


class AuthSessionService:
    """Business logic around login sessions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, *, user_id: int) -> AuthSessionResponse:
        """Create a new session or extend the existing one for *user_id*."""
        expires = datetime.now() + timedelta(hours=AUTH_SESSION_EXPIRE)

        session = await self.db.scalar(
            select(AuthSession).where(AuthSession.user_id == user_id)
        )

        if session:
            # Extend the existing session
            await self.db.execute(
                update(AuthSession)
                .where(AuthSession.user_id == user_id)
                .values(expires_at=expires)
            )
        else:
            # Create a new session
            session = await self.db.scalar(
                insert(AuthSession)
                .values(user_id=user_id, expires_at=expires)
                .returning(AuthSession)
            )

            if not session:
                raise OptimapApiError("Session not created")

        return AuthSessionResponse.model_validate(session.to_dict())

    async def update_session_expire(self, session_id: str) -> None:
        """Expire the session identified by *session_id*."""
        is_expired = await self.db.execute(
            update(AuthSession)
            .where(AuthSession.session_id == session_id)
            .values(expires_at=datetime.now())
        )

        if is_expired.rowcount == 0:
            raise EntityNotPresent("Session not found")

    async def read_session_user(self, session_id: str) -> UserResponse:
        """Return the user associated with *session_id* or raise."""
        user = await self.db.scalar(
            select(User)
            .join(AuthSession, AuthSession.user_id == User.id)
            .where(AuthSession.session_id == session_id)
        )

        if user is None:
            raise EntityNotPresent("User session not found")

        return UserResponse.model_validate(user)

    async def read_session(self, session_id: str) -> AuthSessionResponse:
        """Return the session identified by *session_id* or raise."""
        session = await self.db.scalar(
            select(AuthSession).where(AuthSession.session_id == session_id)
        )

        if session is None:
            raise EntityNotPresent("Session not found")

        return AuthSessionResponse.model_validate(session.to_dict())
