from fastapi import APIRouter

from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import NotificationServiceDep
from app.schema.notifications import (
    NotificationPreferenceRequest,
    NotificationPreferenceResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    user: AuthUserDep, svc: NotificationServiceDep
) -> NotificationPreferenceResponse:
    """
    Get the notification preferences for the user.
    """
    return await svc.get_by_user_id(user.id)


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    req: NotificationPreferenceRequest, user: AuthUserDep, svc: NotificationServiceDep
) -> NotificationPreferenceResponse:
    """
    Update the notification preferences for the user.
    """
    return await svc.update_preferences(user.id, req)
