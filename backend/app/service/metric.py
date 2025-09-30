from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.job import MappingJob, MappingStatus
from app.model.organization import Organization
from app.model.user import User
from app.schema.metric import MetricsResponse


class MetricsService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_system_metrics(self) -> MetricsResponse:
        users = await self.db.scalar(select(func.count(User.id)))
        orgs = await self.db.scalar(select(func.count(Organization.id)))
        active_jobs = await self.db.scalar(
            select(func.count(MappingJob.id)).where(
                MappingJob.status == MappingStatus.RUNNING
            )
        )

        return MetricsResponse(
            total_users=users,
            total_organizations=orgs,
            active_mapping_jobs=active_jobs,
        )
