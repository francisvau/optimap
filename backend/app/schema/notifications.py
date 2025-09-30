from app.model.notification_preference import UsageReportFrequency
from app.schema import BaseSchema


class NotificationPreferenceRequest(BaseSchema):
    usage_report: UsageReportFrequency
    email_notifications: bool


class NotificationPreferenceResponse(NotificationPreferenceRequest):
    id: int
    user_id: int
