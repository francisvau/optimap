from bson import ObjectId
from fastapi import HTTPException

from app.config import DEFAULT_MODEL
from app.deps.database import MongoDbDep
from app.model.model import AIModel, BaseModelType


async def get_model_by_id(model_id: str, db: MongoDbDep) -> AIModel:
    """Fetch a model by its ID from the database."""
    model = await db.ai_models.find_one({"_id": ObjectId(model_id)})

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return AIModel.model_validate(model, by_name=True)


async def determine_model_and_prompts(
    db: MongoDbDep, model: str | None
) -> tuple[BaseModelType, list[str]]:
    """Determine the base model and prompts based on the provided model ID or mapping."""
    if model:
        base_model, prompts = await _fetch_model_and_prompts(db, model)
    else:
        base_model, prompts = await _fetch_model_and_prompts(db, DEFAULT_MODEL)

    return base_model, prompts


async def _fetch_model_and_prompts(
    db: MongoDbDep, model_id: str
) -> tuple[BaseModelType, list[str]]:
    """Fetch the base model and prompts from the database using the model ID."""
    try:
        base_model = BaseModelType(model_id)
        return base_model, []
    except ValueError:
        model_obj = await db.ai_models.find_one({"_id": ObjectId(model_id)})
        if not model_obj:
            raise HTTPException(
                status_code=404, detail=f"Model with id {model_id} not found"
            )
        return model_obj["base_model"], model_obj["tailor_prompt"]
