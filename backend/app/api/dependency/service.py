from __future__ import annotations

from typing import Annotated, AsyncGenerator

from fastapi import Depends

from app.api.dependency.database import DbSessionDep
from app.api.dependency.engine import EngineClient
from app.service.log import LogService
from app.service.mapping.apply import MappingApplyService
from app.service.mapping.blueprint import MappingBlueprintService
from app.service.mapping.job import MappingJobService
from app.service.metric import MetricsService
from app.service.model import ModelService
from app.service.notification import NotificationService
from app.service.organization import OrganizationService
from app.service.session import AuthSessionService
from app.service.upload.upload import FileUploadService
from app.service.user import UserService


def _provide_org_service(db: DbSessionDep, svc: ModelServiceDep) -> OrganizationService:
    return OrganizationService(db, svc)


def _provide_notification_service(db: DbSessionDep) -> NotificationService:
    return NotificationService(db)


def _provide_auth_session_service(db: DbSessionDep) -> AuthSessionService:
    return AuthSessionService(db)


def _provide_user_service(db: DbSessionDep) -> UserService:
    return UserService(db)


def _provide_log_service(db: DbSessionDep) -> LogService:
    return LogService(db)


def _provide_blueprint_service(
    db: DbSessionDep,
    ec: EngineClientDep,
    logger: LogServiceDep,
) -> MappingBlueprintService:
    return MappingBlueprintService(db=db, logger=logger, engine_client=ec)


def _provide_mapping_apply_service(
    db: DbSessionDep,
    bp_svc: MappingBlueprintService = Depends(_provide_blueprint_service),
) -> MappingApplyService:
    return MappingApplyService(db=db, bp_svc=bp_svc)


def _provide_upload_service(
    db: DbSessionDep,
) -> FileUploadService:
    return FileUploadService(db=db)


def _provide_mapping_job_service(
    db: DbSessionDep,
) -> MappingJobService:
    return MappingJobService(db=db)


def _provide_mapping_model_service(
    db: DbSessionDep,
    ec: EngineClientDep,
    logger: LogServiceDep,
) -> ModelService:
    return ModelService(db=db, logger=logger, engine_client=ec)


def _provide_metrics_service(
    db: DbSessionDep,
) -> MetricsService:
    return MetricsService(db=db)


async def _provide_engine_client(
    logger: LogServiceDep,
) -> AsyncGenerator[EngineClient, None]:
    """
    Dependency to get the engine client.
    """
    client = EngineClient(logger)
    try:
        yield client
    finally:
        await client.aclose()


EngineClientDep = Annotated[EngineClient, Depends(_provide_engine_client)]


MappingJobServiceDep = Annotated[
    MappingJobService, Depends(_provide_mapping_job_service)
]

OrganizationServiceDep = Annotated[
    OrganizationService,
    Depends(_provide_org_service),
]

NotificationServiceDep = Annotated[
    NotificationService,
    Depends(_provide_notification_service),
]

AuthSessionServiceDep = Annotated[
    AuthSessionService,
    Depends(_provide_auth_session_service),
]

UserServiceDep = Annotated[
    UserService,
    Depends(_provide_user_service),
]

LogServiceDep = Annotated[
    LogService,
    Depends(_provide_log_service),
]

MappingBlueprintServiceDep = Annotated[
    MappingBlueprintService,
    Depends(_provide_blueprint_service),
]

MappingApplyServiceDep = Annotated[
    MappingApplyService,
    Depends(_provide_mapping_apply_service),
]

UploadServiceDep = Annotated[
    FileUploadService,
    Depends(_provide_upload_service),
]

ModelServiceDep = Annotated[
    ModelService,
    Depends(_provide_mapping_model_service),
]

MetricsServiceDep = Annotated[
    MetricsService,
    Depends(_provide_metrics_service),
]
