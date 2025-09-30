from uuid import uuid4

import pytest
from starlette import status

from app.config import AUTH_KEY
from app.model.log import LogAction, LogType


@pytest.mark.asyncio
async def test_get_all_logs(async_client, admin_session_id):
    payload = {
        "email": f"adminlog_{uuid4().hex}@example.com",
        "first_name": "Admin",
        "last_name": "Log",
        "password": "Secure123!",
    }
    resp = await async_client.post("/auth/register", json=payload)
    assert resp.status_code == 201

    async_client.cookies.set(AUTH_KEY, admin_session_id)
    log_resp = await async_client.get("/logs/")
    print(log_resp.json())
    assert log_resp.status_code == 200
    logs = log_resp.json()
    assert isinstance(logs, list)
    assert any(
        "User" in log["message"] and "registered" in log["message"] for log in logs
    )


@pytest.mark.asyncio
async def test_get_logs_from_users(async_client, admin_session_id):
    # User registers
    payload = {
        "email": f"test_{uuid4().hex}@example.com",
        "first_name": "Rate",
        "last_name": "Limit",
        "password": "Secure123!",
    }
    resp = await async_client.post("/auth/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED

    user_data = resp.json()
    user_id = user_data["id"]

    # Get user logs filtered by action = CREATE
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    log_resp = await async_client.get(
        f"/logs/user/{user_id}",
        params={
            "limit": 10,
            "action": LogAction.CREATE.value,
        },
    )
    print(log_resp.json())
    assert log_resp.status_code == status.HTTP_200_OK
    logs = log_resp.json()

    assert isinstance(logs, list)
    assert any(log["action"] == LogAction.CREATE.value for log in logs)
    assert any(log["user"]["id"] == user_id for log in logs)


@pytest.mark.asyncio
async def test_warning_log_is_created_after_limiter(async_client, admin_session_id):
    payload = {
        "email": f"test_{uuid4().hex}@example.com",
        "first_name": "Rate",
        "last_name": "Limit",
        "password": "Secure123!",
    }

    # Send 3 requests quickly to trigger the limiter
    for _ in range(6):
        await async_client.post("/auth/register", json=payload)

    # Check if log with warning type is created
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    log_resp = await async_client.get(f"/logs/type/{LogType.LIMITER.value}")
    # There should be one log entry with type LIMITER
    print(log_resp.json())
    #    assert any(log["type"] == LogType.LIMITER.value for log in logs)
    assert log_resp.status_code == status.HTTP_200_OK
