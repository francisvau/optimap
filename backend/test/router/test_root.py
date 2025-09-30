from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.router.root import health
from app.config import ASSETS_PATH


@pytest.mark.asyncio
async def test_root_redirect(async_client: AsyncClient):
    response = await async_client.get("/", follow_redirects=False)
    assert response.status_code in (
        status.HTTP_307_TEMPORARY_REDIRECT,
        status.HTTP_302_FOUND,
    )
    assert response.headers["location"] == "/api/openapi.json"


@pytest.mark.asyncio
async def test_health_ok(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_direct_response():
    # Mock DB session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = None

    response = await health(mock_session)

    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_200_OK
    assert response.body == b'{"status":"ok"}'


@pytest.mark.asyncio
async def test_health_error(monkeypatch, async_client: AsyncClient, session):
    async def broken_query(*args, **kwargs):
        raise Exception("Database failure")

    monkeypatch.setattr(session, "execute", broken_query)

    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"status": "error"}


@pytest.mark.asyncio
async def test_rose_file_response(async_client: AsyncClient):
    file_path = ASSETS_PATH / "img/rose.jpg"
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"dummy image content")

    response = await async_client.get("/rose")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("image/")
    assert response.content == file_path.read_bytes()
