from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import AUTH_SESSION_EXPIRE
from app.model.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False, default=lambda: str(uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # The user that owns the session.
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user = relationship("User", back_populates="sessions")

    def __init__(self, expires_in: int = AUTH_SESSION_EXPIRE, **kwargs: Any) -> None:
        """Initialize a new session."""
        self.expires_at = datetime.now() + timedelta(hours=expires_in)
        super().__init__(**kwargs)
