from datetime import datetime
from typing import Optional

from pydantic import field_validator

from app.schema import BaseSchema


class UserValidators(BaseSchema):
    @field_validator("first_name", "last_name", check_fields=False)
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return value.strip().title()
        return value


class UserCreateRequest(UserValidators):
    """
    UserCreateRequest schema for creating a new user.

    Attributes:
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        password (str): The password for the user account.
    """

    email: Optional[str] = None
    first_name: str
    last_name: str
    password: str
    token: Optional[str] = None


class UserUpdateRequest(UserValidators):
    """
    UserUpdateRequest schema for updating user information.

    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        password (str): The new password for the user account.
    """

    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    blocked_at: datetime | None = None


class UserLoginRequest(BaseSchema):
    """
    UserLoginRequest schema for user login requests.

    Attributes:
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    email: str
    password: str


class UserResponse(BaseSchema):
    """
    UserResponse schema for user data.

    Attributes:
        id (int): The unique identifier of the user.
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        is_verified (bool): Indicates whether the user's email is verified.
        is_admin (bool): Indicates whether the user has admin privileges.
    """

    id: int
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    is_admin: bool
    blocked_at: datetime | None = None


class UserLoginResponse(BaseSchema):
    """
    UserLoginResponse schema for user login response.

    Attributes:
        email (str): The email address of the user.
        token (str): The authentication token for the user session.
        msg (str): A message related to the login response.
    """

    email: str
    token: str
    msg: str


class UserLogoutResponse(BaseSchema):
    """
    Response schema for user logout.

    This schema is used to define the structure of the response returned
    when a user successfully logs out of the system.

    Attributes:
        None
    """

    pass


class UserLogoutRequest(BaseSchema):
    """
    Schema for user logout request.

    This schema is used to validate the data for a user logout request.
    Currently, it does not have any fields, but it can be extended in the future
    if additional data is required for the logout process.
    """

    pass


class ForgotEmailRequest(BaseSchema):
    """
    ForgotEmailRequest schema for handling email requests in the forgot password functionality.

    Attributes:
        email (str): The email address of the user requesting a password reset.
    """

    email: str


class ForgotEmailResponse(BaseSchema):
    """
    ForgotEmailResponse represents the response schema for a forgot email request.

    Attributes:
        email (str): The email address associated with the user.
        message (str): A message indicating the status or result of the request.
    """

    email: str
    message: str


class ResetPasswordRequest(BaseSchema):
    """
    Schema for a reset password request.

    Attributes:
        token (str): The token used to authorize the password reset.
        new_password (str): The new password to be set.
    """

    token: str
    new_password: str


class ResetPasswordResponse(BaseSchema):
    """
    Response schema for password reset.

    Attributes:
        email (str): The email address of the user who requested the password reset.
        msg (str): A message indicating the status or result of the password reset request.
    """

    email: str
    msg: str


class RequestVerifyUserRequest(BaseSchema):
    """
    Schema for verifying a user's email address.

    Attributes:
        email (str): The email address of the user to verify.
    """

    email: str


class VerifyUserRequest(BaseSchema):
    """
    Schema for verifying a user's email address.

    Attributes:
        email (str): The email address of the user to verify.
    """

    token: str


class VerifyUserResponse(BaseSchema):
    """
    Response schema for verifying a user's email address.

    Attributes:
        email (str): The email address of the user whose email was verified.
        msg (str): A message indicating the status or result of the email verification.
    """

    email: str
    msg: str


class UserStatsResponse(BaseSchema):
    user_id: int
    job_count: int
    bytes: int
