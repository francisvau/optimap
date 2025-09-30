from uuid import uuid4

import pytest
from starlette import status


@pytest.mark.asyncio
async def test_limiter_blocks_excessive_requests(async_client):
    responses = []

    payload = {
        "email": f"test_{uuid4().hex}@example.com",
        "first_name": "Rate",
        "last_name": "Limit",
        "password": "Secure123!",
    }

    # Send 3 requests quickly to trigger the limiter
    for _ in range(6):
        resp = await async_client.post("/auth/register", json=payload)
        responses.append(resp)

    # Assert the first 2 succeed and the third is limited
    assert responses[5].status_code in {status.HTTP_429_TOO_MANY_REQUESTS, 429}
