from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import JSON, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.blueprint import MappingBlueprint
    from app.model.organization import Organization
    from app.model.user import User


class LogLevel(Enum):
    """
    Enum for log levels.

    This enum defines the different log levels that can be used in the application.
    Each log level is represented as a string.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(Enum):
    """
    Enum for log types.

    This enum defines the different log types that can be used in the application.
    Each log type is represented as a string.
    """

    DEFAULT = "OKAY"
    ERROR = "NOT-OKAY"
    LIMITER = "LIMITER"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"


class LogAction(Enum):
    """
    Enum for log actions.

    This enum defines the different log actions that can be used in the application.
    Each log action is represented as a string.
    """

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


SAEnum(LogType, name="logtype", create_type=True)
SAEnum(LogAction, name="logaction", create_type=True)
SAEnum(LogLevel, name="loglevel", create_type=True)


class Log(Base):
    """
    Log model for storing log entries in the database.
    This model is used to store log entries with a level, message, timestamp, optional user, and context.

    Attributes:
        id (int): The unique identifier for the log entry.
        level (str): The log level (e.g., INFO, ERROR).
        message (str): The log message.
        created_at (datetime): The time the log was created.
        user (User, optional): The associated user.
        organization (Organization, optional): The associated organization.
        context (dict, optional): Additional JSON context for the log.
    """

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[LogLevel] = mapped_column(SAEnum(LogLevel), nullable=False)
    type: Mapped[Optional[LogType]] = mapped_column(
        SAEnum(LogType),
        nullable=False,
        default=LogType.DEFAULT,
    )
    action: Mapped[Optional[LogAction]] = mapped_column(
        SAEnum(LogAction), nullable=True
    )
    message: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # The organization associated with the log entry.
    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", back_populates="logs"
    )

    # The user who triggered the log entry.
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped[Optional["User"]] = relationship("User", back_populates="logs")

    # The blueprint associated with the log entry.
    blueprint_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("blueprints.id", ondelete="SET NULL"), nullable=True
    )
    blueprint: Mapped[Optional["MappingBlueprint"]] = relationship("MappingBlueprint")
