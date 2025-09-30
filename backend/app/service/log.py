from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import EntityNotPresent, OptimapApiError
from app.model.log import Log, LogAction, LogLevel, LogType
from app.schema.log import LogQueryRequest, LogResponse


class LogService:
    """Combine console logging with optional DB persistence."""

    def __init__(
        self,
        db: AsyncSession,
        logger: logging.Logger | None = None,
    ) -> None:
        """Bind the service to an `AsyncSession` and a std-lib logger."""
        self.db = db
        self.logger = logger or logging.getLogger("database-logger")

    async def log(
        self,
        level: LogLevel,
        message: str,
        *,
        type: LogType = LogType.DEFAULT,
        action: Optional[LogAction] = None,
        context: Optional[dict[str, Any]] = None,
        user_id: int | None = None,
        organization_id: int | None = None,
        blueprint_id: int | None = None,
        persist: bool = False,
    ) -> LogResponse | None:
        """
        Emit *message* at *level* and optionally persist it.

        When *persist* is True the new row is flushed and returned as
        a `LogResponse`; otherwise the method returns ``None``.
        """
        if not self.logger.isEnabledFor(getattr(logging, level.value)):
            return None

        self.logger.log(getattr(logging, level.value), message, stacklevel=3)

        if not persist:
            return None

        # Persist the log entry in the database
        log = await self.db.scalar(
            insert(Log)
            .values(
                level=level,
                type=type,
                action=action,
                message=message,
                context=context,
                user_id=user_id,
                organization_id=organization_id,
                blueprint_id=blueprint_id,
            )
            .options(selectinload(Log.user), selectinload(Log.organization))
            .returning(Log)
        )

        if log is None:
            raise OptimapApiError("Failed to persist log entry")

        return LogResponse.model_validate(log.to_dict())

    async def debug(self, message: str, **kw: Any) -> LogResponse | None:
        """Shortcut for `log(LogLevel.DEBUG, …)`."""
        return await self.log(LogLevel.DEBUG, message, **kw)

    async def info(self, message: str, **kw: Any) -> LogResponse | None:
        """Shortcut for `log(LogLevel.INFO, …)`."""
        return await self.log(LogLevel.INFO, message, **kw)

    async def warning(self, message: str, **kw: Any) -> LogResponse | None:
        """Shortcut for `log(LogLevel.WARNING, …)`."""
        return await self.log(LogLevel.WARNING, message, **kw)

    async def error(self, message: str, **kw: Any) -> LogResponse | None:
        """Shortcut for `log(LogLevel.ERROR, …)`."""
        return await self.log(LogLevel.ERROR, message, **kw)

    async def critical(self, message: str, **kw: Any) -> LogResponse | None:
        """Shortcut for `log(LogLevel.CRITICAL, …)`."""
        return await self.log(LogLevel.CRITICAL, message, **kw)

    async def read_log(self, log_id: int) -> LogResponse:
        """Return a single log entry by its ID."""
        result = await self.db.scalar(
            select(Log)
            .where(Log.id == log_id)
            .options(selectinload(Log.user), selectinload(Log.organization))
        )

        if result is None:
            raise EntityNotPresent("Log entry not found")

        return LogResponse.model_validate(result.to_dict())

    async def get_logs(
        self,
        *,
        request: LogQueryRequest,
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
    ) -> list[LogResponse]:
        stmt = select(Log).order_by(Log.created_at.desc()).limit(request.limit)

        if user_id:
            stmt = stmt.where(Log.user_id == user_id)
        if organization_id:
            stmt = stmt.where(Log.organization_id == organization_id)
        if request.level:
            stmt = stmt.where(Log.level == request.level)
        if request.type:
            stmt = stmt.where(Log.type == request.type)
        if request.action:
            stmt = stmt.where(Log.action == request.action)

        stmt = stmt.options(selectinload(Log.user), selectinload(Log.organization))

        result = await self.db.scalars(stmt)
        logs = result.all()

        if request.context_keys or request.context_values:
            filtered_logs = []
            for log in logs:
                if not log.context:
                    continue

                key_match = not request.context_keys or any(
                    key in log.context for key in request.context_keys
                )
                value_match = not request.context_values or any(
                    str(v) in map(str, log.context.values())
                    for v in request.context_values
                )

                if key_match and value_match:
                    filtered_logs.append(log)
            logs = filtered_logs

        return [LogResponse.model_validate(log.to_dict()) for log in logs]

    # async def get_all_logs(self) -> list[LogResponse]:
    #     stmt = select(Log).order_by(Log.created_at.desc())
    #     result = await self.db.scalars(stmt)
    #     logs = result.all()
    #
    #     return [LogResponse.model_validate(log.to_dict()) for log in logs]
