from fastapi import APIRouter, Depends, status

from app.api.dependency.auth.admin import AuthAdminDep
from app.api.dependency.service import LogServiceDep
from app.model.log import LogLevel, LogType
from app.schema.log import LogQueryRequest, LogResponse

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_logs_by_user(
    user_id: int,
    _: AuthAdminDep,
    service: LogServiceDep,
    request: LogQueryRequest = Depends(),
) -> list[LogResponse]:
    return await service.get_logs(user_id=user_id, request=request)


@router.get("/organization/{organization_id}", status_code=status.HTTP_200_OK)
async def get_logs_by_organization(
    organization_id: int,
    _: AuthAdminDep,
    service: LogServiceDep,
    request: LogQueryRequest = Depends(),
) -> list[LogResponse]:
    return await service.get_logs(organization_id=organization_id, request=request)


@router.get("/level/{level}", status_code=status.HTTP_200_OK)
async def get_logs_by_level(
    level: LogLevel,
    _: AuthAdminDep,
    service: LogServiceDep,
    request: LogQueryRequest = Depends(),
) -> list[LogResponse]:
    request.level = level
    return await service.get_logs(request=request)


@router.get("/type/{log_type}", status_code=status.HTTP_200_OK)
async def get_logs_by_type(
    log_type: LogType,
    _: AuthAdminDep,
    service: LogServiceDep,
    request: LogQueryRequest = Depends(),
) -> list[LogResponse]:
    request.type = log_type
    return await service.get_logs(request=request)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_logs(
    _: AuthAdminDep,
    service: LogServiceDep,
    request: LogQueryRequest = Depends(),
) -> list[LogResponse]:
    return await service.get_logs(request=request)
