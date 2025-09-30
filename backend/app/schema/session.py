from datetime import datetime

from app.schema import BaseSchema


class AuthSessionResponse(BaseSchema):
    """Response schema for AuthSession."""

    session_id: str
    user_id: int
    expires_at: datetime
