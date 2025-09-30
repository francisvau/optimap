from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependency.mail import MailerDep
from app.exceptions import EntityNotPresent
from app.model.notification_preference import (
    NotificationPreference,
    UsageReportFrequency,
)
from app.model.organization import OrganizationUser
from app.model.user import User
from app.schema.notifications import (
    NotificationPreferenceRequest,
    NotificationPreferenceResponse,
)
from app.schema.user import UserResponse
from app.service.organization import OrganizationService
from app.util.mail import send_combined_org_stats_mail


class NotificationService:
    def __init__(
        self,
        db: AsyncSession,
        mailer: MailerDep | None = None,
        organization_service: OrganizationService | None = None,
    ):
        self.db = db
        self.mailer = mailer
        self.organization_service = organization_service

    async def get_by_user_id(self, user_id: int) -> NotificationPreferenceResponse:
        result = await self.db.scalar(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        if result is None:
            result = await self.create_default_preferences(user_id)
        return NotificationPreferenceResponse.model_validate(result.to_dict())

    async def update_preferences(
        self, user_id: int, req: NotificationPreferenceRequest
    ) -> NotificationPreferenceResponse:
        stmt = (
            update(NotificationPreference)
            .where(NotificationPreference.user_id == user_id)
            .values(**req.dict())
            .returning(NotificationPreference)
        )
        result = await self.db.scalar(stmt)
        if result is None:
            raise EntityNotPresent("Notification preference not found")
        return NotificationPreferenceResponse.model_validate(result.to_dict())

    async def create_default_preferences(self, user_id: int) -> NotificationPreference:
        new_preference = NotificationPreference(user_id=user_id)
        self.db.add(new_preference)
        await self.db.commit()
        await self.db.refresh(new_preference)
        return new_preference

    async def send_scheduled_notifications(self) -> None:
        """
        Dispatch notifications to users based on their notification preferences.
        """
        if not self.mailer:
            raise ValueError("Mailer is not set up for sending emails.")

        if not self.organization_service:
            raise ValueError("Organization service is not set up for sending emails.")

        results = (
            await self.db.scalars(
                select(NotificationPreference).options(
                    selectinload(NotificationPreference.user)
                    .selectinload(User.organizations)
                    .selectinload(OrganizationUser.organization)
                )
            )
        ).all()

        now = datetime.now(timezone.utc)

        for pref in results:
            user = pref.user

            if not pref.email_notifications:
                continue

            should_send = False

            if pref.usage_report == UsageReportFrequency.DAILY:
                should_send = True
            elif pref.usage_report == UsageReportFrequency.WEEKLY:
                should_send = now.weekday() == 0
            elif pref.usage_report == UsageReportFrequency.MONTHLY:
                should_send = now.day == 1

            if should_send:
                org_stats = []

                for org_user in user.organizations:
                    stats = await self.organization_service.get_organization_stats(
                        org_user.organization_id
                    )

                    org_stats.append(
                        (org_user.organization.name, org_user.organization.id, stats)
                    )

                if org_stats:
                    await send_combined_org_stats_mail(
                        user=UserResponse.model_validate(user),
                        stats_by_org=org_stats,
                        mailer=self.mailer,
                    )
