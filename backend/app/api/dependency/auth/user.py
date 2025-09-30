import base64
from datetime import datetime
from typing import Annotated

from fastapi import Depends, Request, status

from app.api.dependency.service import AuthSessionServiceDep, UserServiceDep
from app.config import AUTH_KEY
from app.exceptions import Unauthorized
from app.schema.user import UserResponse


async def _get_user_from_basic_auth(
    req: Request, svc: AuthSessionServiceDep, user_svc: UserServiceDep
) -> UserResponse | None:
    """Get user from Basic Auth header if present."""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return None

    try:
        # Remove 'Basic ' prefix and decode base64
        encoded = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        email, password = decoded.split(":")

        # Here you would validate the credentials
        user = await user_svc.read_user_by_email_and_password(email, password)

        if user.blocked_at is not None:
            raise Unauthorized(
                "Acount locked from application", status=status.HTTP_403_FORBIDDEN
            )
    except Exception:
        return None

    return None


async def _get_unverified_user(
    req: Request, svc: AuthSessionServiceDep
) -> UserResponse:
    """Retrieve an unverified user based on the session ID from the request cookies."""
    session_id = req.cookies.get(AUTH_KEY)
    if session_id is None:
        raise Unauthorized("Missing session ID in cookie")

    session = await svc.read_session(session_id)
    if session.expires_at <= datetime.now():
        raise Unauthorized("Session expired")

    user = await svc.read_session_user(session_id)
    if user is None:
        raise Unauthorized("Invalid session ID")

    return user


async def _get_auth_user(req: Request, svc: AuthSessionServiceDep) -> UserResponse:
    """Retrieve an authenticated user based on the session ID from the request cookies."""
    user: UserResponse = await _get_unverified_user(req, svc)

    if not user.is_verified:
        raise Unauthorized("Please verify your account", status=status.HTTP_423_LOCKED)

    if user.blocked_at is not None:
        raise Unauthorized(
            "Account locked from application", status=status.HTTP_403_FORBIDDEN
        )

    return user


AuthUserDep = Annotated[UserResponse, Depends(_get_auth_user)]
UnverifiedUserDep = Annotated[UserResponse, Depends(_get_unverified_user)]


async def _visible_users_guard(
    user: AuthUserDep,
    svc: UserServiceDep,
) -> list[UserResponse]:
    """Return all users if admin; otherwise just the requesting user."""
    if user.is_admin:
        users = await svc.read_all_users()
        return users
    return [user]


VisibleUsersDep = Annotated[list[UserResponse], Depends(_visible_users_guard)]


async def _user_self_or_admin_guard(
    user_id: int,
    current_user: AuthUserDep,
) -> int:
    """Allow access if current user is admin or requesting own organizations."""

    if current_user.is_admin or current_user.id == user_id:
        return user_id

    raise Unauthorized("Access denied")


UserSelfOrAdminDep = Annotated[int, Depends(_user_self_or_admin_guard)]
