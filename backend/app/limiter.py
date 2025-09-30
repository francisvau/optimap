from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.logger import logger

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/second", "50/minute"],
)


def error_message_with_logger(request: Request) -> str:
    """
    Overrides error_message of the Limiter.limit so the local logger can log when the limit gets exceeded.
    """
    user_id = getattr(request.state, "user", None)
    ip = get_remote_address(request)

    logger.warning(
        f"Rate limit exceeded for IP: {ip} - User: {user_id}",
        extra={"ip": ip, "user_id": user_id},
    )
    return "Rate limit exceeded. Please try again later."
