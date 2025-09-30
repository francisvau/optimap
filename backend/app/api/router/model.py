from typing import List

from fastapi import APIRouter, Query, status

from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import (
    ModelServiceDep,
)
from app.schema.model import (
    CreateModelRequest,
    ModelResponse,
    UpdateModelRequest,
)

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/base-models", response_model=List[str])
async def get_base_models(
    model_svc: ModelServiceDep,
    _: AuthUserDep,
) -> List[str]:
    """Get all base models."""
    models: List[str] = await model_svc.get_base_models()
    return models


@router.get("/{model_id}", response_model=ModelResponse)
async def read_model(
    model_id: str,
    model_svc: ModelServiceDep,
    _: AuthUserDep,
) -> ModelResponse:
    """Get a specific model by ID."""
    model = await model_svc.get_model(model_id)
    return ModelResponse.model_validate(model)


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    body: CreateModelRequest,
    model_svc: ModelServiceDep,
    _: AuthUserDep,
) -> ModelResponse:
    """Create a new model."""
    model = await model_svc.create_model(req=body)
    return ModelResponse.model_validate(model)


@router.patch("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    body: UpdateModelRequest,
    model_svc: ModelServiceDep,
    _: AuthUserDep,
) -> ModelResponse:
    """Update a specific model by ID."""
    model = await model_svc.update_model(model_id=model_id, req=body)
    return ModelResponse.model_validate(model)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    model_svc: ModelServiceDep,
    _: AuthUserDep,
) -> None:
    """Delete a specific model by ID."""
    await model_svc.delete_model(model_id=model_id)
    return None


@router.get("", response_model=List[ModelResponse])
async def get_models(
    model_svc: ModelServiceDep,
    _: AuthUserDep,
    ids: List[str] = Query(..., description="List of model IDs"),
) -> List[ModelResponse]:
    """Get models by a list of IDs."""
    models = await model_svc.get_models_by_ids(ids)
    return [ModelResponse.model_validate(model) for model in models]


@router.patch("/{model_id}/add-prompt")
async def add_prompt(
    model_id: str,
    prompt: str,
    model_svc: ModelServiceDep,
    _: AuthUserDep,
) -> None:
    """Add a prompt to a specific model by ID."""
    await model_svc.add_prompt(model_id=model_id, prompt=prompt)
    return None
