from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from starlette import status

from app.deps.database import MongoDbDep
from app.model.model import AIModel, BaseModelType
from app.schema.model import UpdateModelRequest
from app.service.db import get_model_by_id

router = APIRouter(prefix="/ai-models", tags=["ai-models"])


@router.get("/", response_model=list[AIModel], response_model_by_alias=False)
async def get_all_models(
    db: MongoDbDep,
    ids: list[str] = Query(default=[]),
    skip: int = 0,
    limit: int = 10,
) -> list[AIModel]:
    """Endpoint to retrieve all models with pagination or a list of models given their IDs."""
    # If IDs are provided, fetch models by their IDs
    object_ids = [ObjectId(id) for id in ids]
    models_cursor = (
        db.ai_models.find({"_id": {"$in": object_ids}}).skip(skip).limit(limit)
    )

    models = await models_cursor.to_list(length=limit)
    return [AIModel.model_validate(model) for model in models]


@router.get("/base-models", response_model=list[str])
async def get_all_basemodels() -> list[str]:
    """Get all basemodels."""
    return [model.value for model in BaseModelType]


@router.get(
    "/{model_id}",
    response_model=AIModel,
    response_model_by_alias=False,
)
async def get_model(model_id: str, db: MongoDbDep) -> AIModel:
    """Get a model by its ID."""
    model = await get_model_by_id(model_id, db)
    return model


@router.post(
    "/",
    response_model=AIModel,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_model(model: AIModel, db: MongoDbDep) -> AIModel:
    """Create a new model."""
    result = await db.ai_models.insert_one(
        model.model_dump(by_alias=True, exclude={"id"})
    )
    created_model = await db["ai_models"].find_one({"_id": result.inserted_id})
    return AIModel.model_validate(created_model)


@router.delete("/{model_id}")
async def delete_model(model_id: str, db: MongoDbDep) -> None:
    """Endpoint to delete a tailored model by its ID."""
    await db.ai_models.delete_one({"_id": ObjectId(model_id)})


@router.patch(
    "/{model_id}",
    response_model=AIModel,
    response_model_by_alias=False,
)
async def update_model(
    model_id: str, model: UpdateModelRequest, db: MongoDbDep
) -> AIModel:
    """Update a model by its ID."""
    changes = {
        key: value
        for key, value in model.model_dump(by_alias=True, exclude_unset=True).items()
        if value is not None
    }
    result = await db.ai_models.update_one(
        {"_id": ObjectId(model_id)}, {"$set": changes}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")
    model_obj = await get_model_by_id(model_id, db)
    return model_obj


@router.patch("/{model_id}/add-prompt")
async def add_tailor_prompt(
    model_id: str,
    prompt: str,
    db: MongoDbDep,
) -> None:
    """Add a single prompt to tailor prompt list from a model."""
    result = await db.ai_models.update_one(
        {"_id": ObjectId(model_id)}, {"$push": {"tailor_prompt": prompt}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Model not found or not modified")
