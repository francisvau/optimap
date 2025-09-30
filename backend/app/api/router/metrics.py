from fastapi import APIRouter

from app.api.dependency.auth.admin import AuthAdminDep
from app.api.dependency.service import MetricsServiceDep
from app.schema.metric import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/system", response_model=MetricsResponse)
async def system_metrics(
    _: AuthAdminDep,
    service: MetricsServiceDep,
) -> MetricsResponse:
    return await service.get_system_metrics()
