from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.user import User


class UsageReportFrequency(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    NEVER = "NEVER"


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)

    usage_report: Mapped[UsageReportFrequency] = mapped_column(
        SqlEnum(UsageReportFrequency), default=UsageReportFrequency.WEEKLY
    )

    email_notifications: Mapped[bool] = mapped_column(Boolean, default=False)

    # The user associated with this notification preference.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="notification_preferences"
    )
