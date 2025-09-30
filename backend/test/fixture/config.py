from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.api.dependency.database import get_session
from app.api.dependency.engine import EngineClient
from app.api.dependency.mail import get_mailer
from app.main import app
from app.model.base import Base
from app.service.log import LogService
from app.service.mapping.blueprint import MappingBlueprintService
from app.service.mapping.job import MappingJobService
from app.service.model import ModelService
from app.service.organization import OrganizationService
from app.service.session import AuthSessionService
from app.service.upload.upload import FileUploadService
from app.service.user import UserService

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
UPLOAD_DIR = Path("uploads")

"""Database"""


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    return create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(autouse=True)
async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        await session.execute(text("PRAGMA foreign_keys=ON"))
        yield session
        await session.rollback()


"""Dependency Overrides"""


@pytest.fixture(autouse=True)
def override_dependencies(session: AsyncSession, mock_mailer):
    async def _get_test_session():
        yield session

    app.dependency_overrides[get_session] = _get_test_session
    app.dependency_overrides[get_mailer] = lambda: mock_mailer


"""Test Client"""


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as ac:
        yield ac


@pytest.fixture
def websocket_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


"""Helper Function for WebSocket File Upload"""


@pytest.fixture
async def send_file_entities(async_client: AsyncClient):
    """Helper fixture for sending file entities over WebSocket."""

    async def _send_file_entities(
        websocket, filename: str, file_type: str, entities: str
    ):
        data = {
            "action": "send_entities",
            "filename": filename,
            "file_type": file_type,
            "entities": entities,
        }
        await websocket.send_json(data)

    return _send_file_entities


"""Services"""


@pytest.fixture
def engine_client(session, logger) -> EngineClient:
    """A fixture that provides an EngineClient instance."""
    return EngineClient(logger)


@pytest.fixture
def logger(session) -> LogService:
    """A fixture that provides a LogService instance."""
    return LogService(session)


@pytest.fixture()
def bp_svc(session, logger, engine_client) -> MappingBlueprintService:
    """A fixture that provides a MappingBlueprintService instance."""
    return MappingBlueprintService(
        session,
        engine_client=engine_client,
        logger=logger,
    )


@pytest.fixture()
def mapjob_svc(session) -> MappingJobService:
    """A fixture that provides a OrganizationService instance."""
    return MappingJobService(session)


@pytest.fixture()
def user_svc(session) -> UserService:
    """A fixture that provides a UserService instance."""
    return UserService(session)


@pytest.fixture
def session_svc(session):
    return AuthSessionService(session)


@pytest.fixture
def log_svc(session):
    return LogService(session)


@pytest.fixture
def upload_svc(session):
    return FileUploadService(session)


@pytest.fixture
def mapping_job_svc(session):
    return MappingJobService(session)


@pytest.fixture
def model_svc(session, engine_client, logger):
    return ModelService(
        db=session,
        engine_client=engine_client,
        logger=logger,
    )


@pytest.fixture()
def org_svc(session, model_svc) -> OrganizationService:
    """A fixture that provides a OrganizationService instance."""
    return OrganizationService(session, model_svc)
