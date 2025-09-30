from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Any

import jwt

from app.exceptions import ExpiredEntity, Unauthorized

# 32 bytes token for the JWT secret decoding
JWT_SECRET = token_urlsafe(nbytes=32)


def create_jwt_token(sub: str, data: dict[str, Any] = {}, ttl_minutes: int = 20) -> str:
    """
    Generate a JSON Web Token (JWT) with the specified subject, data, and time-to-live.

    Args:
        sub (str): The subject of the token, typically representing the user or entity.
        data (dict[str, Any]): A dictionary containing additional claims to include in the token.
        ttl_minutes (int, optional): The time-to-live for the token in minutes. Defaults to 20.

    Returns:
        str: The encoded JWT token as a string.
    """
    # Update the data dictionary with the subject and expiration time
    data |= {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
    }

    # Generate a JWT token with the provided data and secret
    token = jwt.encode(data, JWT_SECRET, algorithm="HS256")

    return token


def decode_jwt_token(token: str) -> dict[str, str]:
    """
    Decodes a JWT token and returns its payload as a dictionary.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict[str, str]: The decoded payload of the token.
    Raises:
        Unauthorized: If the token is invalid or the payload is not a dictionary.
        ExpiredEntity: If the token has expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        if not isinstance(payload, dict):
            raise Unauthorized("Invalid token payload")

        return {str(k): str(v) for k, v in payload.items()}

    except jwt.ExpiredSignatureError as _:
        raise ExpiredEntity("The JWT token has expired. Please issue a new one.")

    except jwt.InvalidTokenError as _:
        raise Unauthorized("The JWT token is invalid. Please issue a new one.")
