from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependency.engine import EngineClient
from app.schema.model import (
    CreateModelRequest,
    ModelResponse,
    UpdateModelRequest,
)
from app.service.log import LogService


class ModelService:
    """Business logic for models."""

    def __init__(
        self,
        db: AsyncSession,
        engine_client: EngineClient,
        logger: LogService,
    ) -> None:
        self.db = db
        self.client = engine_client
        self.logger = logger

    async def get_model(self, model_id: str) -> ModelResponse:
        """Get a model from the engine."""
        model = await self.client.request(
            "GET",
            f"/ai-models/{model_id}",
        )
        return ModelResponse.model_validate(model)

    async def create_model(self, *, req: CreateModelRequest) -> ModelResponse:
        """Create a new model in the engine."""
        model: ModelResponse = await self.client.request(
            "POST",
            "/ai-models",
            json={
                "name": req.name,
                "tailor_prompt": req.tailor_prompt,
                "base_model": req.base_model,
            },
        )
        return ModelResponse.model_validate(model)

    async def get_base_models(self) -> list[str]:
        """Get all base models from the engine."""
        models: list[str] = await self.client.request(
            "GET",
            "/ai-models/base-models",
        )
        return models

    async def update_model(
        self, model_id: str, req: UpdateModelRequest
    ) -> ModelResponse:
        """Update a model in the engine."""
        model = await self.client.request(
            "PATCH",
            f"/ai-models/{model_id}",
            json={
                "name": req.name,
                "tailor_prompt": req.tailor_prompt,
                "base_model": req.base_model,
            },
        )
        return ModelResponse.model_validate(model)

    async def delete_model(self, model_id: str) -> None:
        """Delete a model in the engine."""
        await self.client.request(
            "DELETE",
            f"/ai-models/{model_id}",
        )
        return None

    async def get_models_by_ids(self, model_ids: list[str]) -> list[ModelResponse]:
        """Get models by IDs from the engine."""
        models = await self.client.request(
            "GET",
            "/ai-models/",
            params={"ids": model_ids},
        )

        return [ModelResponse.model_validate(model) for model in models]

    async def add_prompt(self, model_id: str, prompt: str) -> None:
        """Add a prompt to a model in the engine."""
        await self.client.request(
            "PATCH",
            f"/ai-models/{model_id}/add-prompt",
            params={"prompt": prompt},
        )
        return None
