from typing import Any

import httpx

from app.config import ENGINE_URL_PREFIX
from app.exceptions import EngineError
from app.service.log import LogService


class EngineClient:
    """Tiny wrapper around the engine’s mapping endpoints."""

    def __init__(
        self,
        logger: LogService,
        base_url: str = ENGINE_URL_PREFIX,
        timeout: float = 120,
    ) -> None:
        self.logger = logger
        self._c = httpx.AsyncClient(
            base_url=base_url, timeout=timeout, follow_redirects=True
        )

    async def aclose(self) -> None:
        """Close the HTTP client."""
        await self._c.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Generic HTTP request helper for the engine API."""
        try:
            resp = await self._c.request(method, path, params=params, json=json)
            resp.raise_for_status()
            return resp.json() if resp.content else None
        except httpx.HTTPStatusError as e:
            await self.logger.error("Engine request failed:")
            await self.logger.error(str(e))
            raise EngineError(
                f"Request failed: {e.response.json()}",
                status_code=e.response.status_code,
            ) from e
