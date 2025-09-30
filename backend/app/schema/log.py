from datetime import datetime
from typing import Any, List, Optional

from app.model.log import LogAction, LogLevel, LogType
from app.schema import BaseSchema
from app.schema.organization import OrganizationResponse
from app.schema.user import UserResponse


class LogResponse(BaseSchema):
    """
    Log response schema for API responses.

    This schema is used to represent a log entry in the API response.
    It includes the log level, message, created_at, and optional user and organization information.
    """

    id: int
    level: LogLevel
    action: Optional[LogAction] = None
    type: Optional[LogType] = None
    context: Optional[dict[str, Any]] = None
    message: str
    created_at: datetime
    user: Optional["UserResponse"] = None
    organization: Optional["OrganizationResponse"] = None


class LogQueryRequest(BaseSchema):
    """
    Log query request schema for filtering logs.

    - level: Optional log level to filter logs by.
    - type: Optional log type to filter logs by.
    - action: Optional log action to filter logs by.
    - context_keys: Optional list of context keys to filter logs by.
    - context_values: Optional list of context values to filter logs by.
    - limit: Maximum number of logs to return (default is 50).
    """

    level: Optional[LogLevel] = None
    type: Optional[LogType] = None
    action: Optional[LogAction] = None
    context_keys: Optional[List[str]] = None
    context_values: Optional[List[str]] = None
    limit: int = 50
