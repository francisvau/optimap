from datetime import datetime

from fastapi import APIRouter, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.dependency.auth.admin import AuthAdminDep
from app.api.dependency.auth.user import AuthUserDep, UnverifiedUserDep
from app.api.dependency.mail import MailerDep
from app.api.dependency.service import (
    AuthSessionServiceDep,
    LogServiceDep,
    OrganizationServiceDep,
    UserServiceDep,
)
from app.config import AUTH_KEY
from app.exceptions import BadRequest, Unauthorized
from app.limiter import limiter
from app.model.log import LogAction
from app.schema.user import (
    ForgotEmailRequest,
    ForgotEmailResponse,
    RequestVerifyUserRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
    UserUpdateRequest,
    VerifyUserResponse,
)
from app.util.mail import send_forgot_password_email, send_verify_user_email

router = APIRouter(prefix="/auth", tags=["session"])


def _set_login_cookie(res: Response, session_id: str) -> None:
    """Set the login cookie in the response."""
    res.set_cookie(
        key=AUTH_KEY,
        value=session_id,
        secure=True,
        httponly=True,
    )


@router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login: UserLoginRequest,
    user_svc: UserServiceDep,
    sess_svc: AuthSessionServiceDep,
    logger: LogServiceDep,
) -> Response:
    """Login a user and return a session cookie."""
    user = await user_svc.read_user_by_email_and_password(login.email, login.password)
    if user.blocked_at is not None:
        raise Unauthorized(
            "Acount locked from application", status=status.HTTP_403_FORBIDDEN
        )
    session = await sess_svc.create_session(user_id=user.id)

    res = JSONResponse(content=jsonable_encoder(user))
    _set_login_cookie(res, session.session_id)

    await logger.info(
        f"User {user.id} logged in successfully",
        user_id=user.id,
        persist=True,
    )
    return res


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    request: Request,
    sess_svc: AuthSessionServiceDep,
    logger: LogServiceDep,
) -> None:
    """Logout the current user."""
    session_id = request.cookies.get(AUTH_KEY)

    if not session_id:
        raise Unauthorized("No session found")

    await logger.info(
        "User logged out successfully",
        persist=True,
        context={
            "session_id": session_id,
        },
    )
    await sess_svc.update_session_expire(session_id)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    body: UserCreateRequest,
    user_svc: UserServiceDep,
    sess_svc: AuthSessionServiceDep,
    org_svc: OrganizationServiceDep,
    mailer: MailerDep,
    logger: LogServiceDep,
) -> Response:
    """Register a new user."""
    token = body.token

    if token:
        # now user should also be added to the organization
        user = await user_svc.create_user(body)
        invite = await org_svc.read_organization_invite_by_token(token)
        await org_svc.accept_organization_invite(invite_id=invite.id)
    else:
        if body.email is None:
            raise BadRequest("Email is required")
        user = await user_svc.create_user(body)
    await send_verify_user_email(user, mailer)

    session = await sess_svc.create_session(user_id=user.id)

    res = JSONResponse(
        content=jsonable_encoder(user),
        status_code=status.HTTP_201_CREATED,
    )
    _set_login_cookie(res, session.session_id)

    await logger.info(
        f"User {user.id} registered successfully",
        user_id=user.id,
        persist=True,
        action=LogAction.CREATE,
        context={
            "session_id": session.session_id,
        },
    )
    return res


@router.get("/me", response_model=UserResponse)
async def read_me(user: UnverifiedUserDep) -> UserResponse:
    """Get the current user."""
    return user


@router.patch("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def update_user(
    request: Request,
    body: UserUpdateRequest,
    user: AuthUserDep,
    user_svc: UserServiceDep,
    logger: LogServiceDep,
) -> UserResponse:
    """Update the current user."""
    res = await user_svc.update_user(user.id, changes=body)
    await logger.info(
        f"User {user.id} updated successfully",
        user_id=user.id,
        persist=True,
        action=LogAction.UPDATE,
    )
    return res


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: ForgotEmailRequest,
    user_svc: UserServiceDep,
    mailer: MailerDep,
    logger: LogServiceDep,
) -> ForgotEmailResponse:
    """Send a password reset email to the user."""
    user = await user_svc.read_user_by_email(body.email)
    await send_forgot_password_email(user, mailer)

    await logger.info(
        f"Password reset e-mail sent to {user.id} with email {user.email}",
        user_id=user.id,
        persist=True,
        action=LogAction.UPDATE,
    )
    return ForgotEmailResponse(
        email=user.email,
        message="Reset password e-mail sent successfully",
    )


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    user_svc: UserServiceDep,
    logger: LogServiceDep,
) -> ResetPasswordResponse:
    """Reset password by token."""
    user = await user_svc.reset_password_by_token(body.token, body.new_password)

    await logger.info(
        f"Password reset successfully for user {user.id}",
        user_id=user.id,
        persist=True,
        action=LogAction.UPDATE,
    )
    return ResetPasswordResponse(email=user.email, msg="Password reset successfully")


@router.post("/verify/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def verify_user(
    token: str,
    user_svc: UserServiceDep,
    sess_svc: AuthSessionServiceDep,
) -> Response:
    """Verify a user by token."""
    user = await user_svc.verify_user_by_token(token)
    session = await sess_svc.create_session(user_id=user.id)

    res = Response(status_code=status.HTTP_204_NO_CONTENT)
    _set_login_cookie(res, session.session_id)
    return res


@router.post(
    "/verify", response_model=VerifyUserResponse, status_code=status.HTTP_200_OK
)
async def request_verify_user(
    body: RequestVerifyUserRequest,
    user_svc: UserServiceDep,
    mailer: MailerDep,
) -> VerifyUserResponse:
    """Send a verification email to the user."""
    user = await user_svc.read_user_by_email(body.email)
    await send_verify_user_email(user, mailer)

    return VerifyUserResponse(
        email=user.email,
        msg="Verification e-mail sent successfully",
    )


@router.post("/block/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def block_user(
    user_id: int,
    _: AuthAdminDep,
    user_svc: UserServiceDep,
    logger: LogServiceDep,
) -> None:
    await user_svc.update_user(
        user_id=user_id, changes=UserUpdateRequest(blocked_at=datetime.now())
    )
    await logger.info(
        f"User {user_id} blocked successfully",
        user_id=user_id,
        persist=True,
        action=LogAction.UPDATE,
    )


@router.post("/unblock/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unblock_user(
    user_id: int,
    _: AuthAdminDep,
    user_svc: UserServiceDep,
    logger: LogServiceDep,
) -> None:
    await user_svc.update_user(
        user_id=user_id, changes=UserUpdateRequest(blocked_at=None)
    )
    await logger.info(
        f"User {user_id} unblocked successfully",
        user_id=user_id,
        persist=True,
        action=LogAction.UPDATE,
    )
