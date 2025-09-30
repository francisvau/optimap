from fastapi import status
from httpx import AsyncClient


async def test_rose_endpoint(async_client: AsyncClient) -> None:
    """Test that the /rose endpoint returns a JPEG image"""
    response = await async_client.get("/rose")

    assert response.status_code == status.HTTP_200_OK

    assert response.headers["content-type"] == "image/jpeg"

    assert response.content is not None
    assert len(response.content) > 0
