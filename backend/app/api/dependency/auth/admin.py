from typing import Annotated

from fastapi import Depends

from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import LogServiceDep
from app.exceptions import Unauthorized
from app.model.log import LogType
from app.schema.user import UserResponse


async def _ensure_admin(
    user: AuthUserDep,
    logger: LogServiceDep,
) -> UserResponse:
    """Return *user* if they are an admin, otherwise raise."""
    if not user.is_admin:
        await logger.warning(
            f"Unauthorized access attempt by user {user.id}",
            user_id=user.id,
            type=LogType.UNAUTHORIZED,
            persist=True,
        )
        raise Unauthorized("Admin privileges required")

    return user


AuthAdminDep = Annotated[UserResponse, Depends(_ensure_admin)]
