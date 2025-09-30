from builtins import anext
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app import limiter
from app.api.dependency.database import get_db_engine, get_db_sessionmaker, get_session
from app.api.dependency.engine import EngineClient
from app.api.dependency.mail import Mailer
from app.api.router import (
    auth,
    logs,
    metrics,
    model,
    notifications,
    organization,
    root,
    users,
)
from app.api.router.mapping import root as mappings_root
from app.exceptions import OptimapApiError
from app.scheduler import start_scheduler
from app.service.log import LogService
from app.service.model import ModelService
from app.service.notification import NotificationService
from app.service.organization import OrganizationService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    sessionmaker = get_db_sessionmaker(get_db_engine())
    async with sessionmaker() as session:
        app.state.db = sessionmaker

        mailer = Mailer()

        log_service = LogService(session)
        engine_client = EngineClient(logger=log_service)
        model_service = ModelService(
            session, engine_client=engine_client, logger=log_service
        )
        organization_service = OrganizationService(session, model_svc=model_service)
        notification_service = NotificationService(
            session, mailer=mailer, organization_service=organization_service
        )

        start_scheduler(notification_service)

        yield


app = FastAPI(root_path="/api", lifespan=lifespan)

app.state.limiter = limiter

app.include_router(auth.router)
app.include_router(organization.router)
# app.include_router(upload.router)
app.include_router(root.router)
# app.include_router(stream.router)
app.include_router(mappings_root.router)
app.include_router(users.router)
app.include_router(model.router)
app.include_router(logs.router)
app.include_router(notifications.router)
app.include_router(metrics.router)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Handle rate limit exceeded exceptions."""
    get_db = request.app.dependency_overrides.get(get_session, get_session)

    db_gen = get_db()
    session = await anext(db_gen)

    logger = LogService(session)
    await logger.warning(
        f"Rate limit exceeded for {request.client} on {request.url.path}",
    )

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded.",
            "status": "RATE_LIMIT_EXCEEDED",
        },
    )


@app.exception_handler(OptimapApiError)
async def api_error_handler(
    request: Request,
    exc: OptimapApiError,
) -> JSONResponse:
    """Handle OptimapApiError exceptions and return appropriate status codes."""
    content = {
        "detail": exc.message,
    }

    if exc.status:
        content["status"] = exc.status

    get_db = request.app.dependency_overrides.get(get_session, get_session)

    db_gen = get_db()
    session = await anext(db_gen)

    logger = LogService(session)

    await logger.error(
        f"{exc.message} for {request.client} on {request.url.path}",
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )
