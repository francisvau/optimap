from typing import Optional

from app.schema import BaseSchema


class MetricsResponse(BaseSchema):
    total_users: Optional[int] = None
    total_organizations: Optional[int] = None
    active_mapping_jobs: Optional[int] = None
