from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from app.service.notification import NotificationService

scheduler = AsyncIOScheduler()


def start_scheduler(notification_service: NotificationService) -> None:
    """
    Start the scheduler to send notifications at regular intervals.
    """
    scheduler.add_job(
        func=notification_service.send_scheduled_notifications,
        trigger=IntervalTrigger(days=1),
        id="send_notifications",
        replace_existing=True,
    )
    scheduler.start()
