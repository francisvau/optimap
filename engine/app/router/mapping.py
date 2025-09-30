from fastapi import APIRouter, Query

from app.deps.database import MongoDbDep
from app.schema.mapping import (
    JsonataEditingRequest,
    JsonataExplanationRequest,
    JsonataGenerationRequest,
    JsonataGenerationResponse,
)
from app.service.db import determine_model_and_prompts
from app.service.mapping import (
    generate_edited_mapping,
    generate_explanation,
    generate_mapping_from_schemas,
)

router = APIRouter(prefix="/mappings", tags=["mappings"])


@router.post(
    "/generate",
    response_model=JsonataGenerationResponse,
)
async def generate_mapping(
    db: MongoDbDep, body: JsonataGenerationRequest, retries: int = Query(3, ge=0, le=10)
) -> JsonataGenerationResponse:
    """Endpoint to get a generated JSONata mapping. This does not automatically save the mapping to the corresponding Mapping object."""
    # Determine the model and prompts
    base_model, prompts = await determine_model_and_prompts(db, body.model_id)

    # Generate mapping
    mapping_response = await generate_mapping_from_schemas(
        body.input_json_schema,
        body.output_json_schema,
        base_model,
        prompts,
        retries,
        body.previous_mappings or [],
    )

    return mapping_response


@router.post("/edit", response_model=str)
async def edit_mapping(db: MongoDbDep, body: JsonataEditingRequest) -> str:
    """Endpoint to request changes to a mapping using the basemodel."""
    # Determine the model and prompts
    base_model, prompts = await determine_model_and_prompts(db, body.model_id)

    # Generate mapping
    edited_mapping: str = await generate_edited_mapping(
        body.input_json_schema,
        body.output_json_schema,
        body.jsonata_mapping,
        body.context,
        base_model,
        prompts,
    )

    return edited_mapping


@router.post("/explanation", response_model=str)
async def get_explanation(db: MongoDbDep, body: JsonataExplanationRequest) -> str:
    """Endpoint to get an explanation for a generated mapping by the basemodel."""  # Determine the model and prompts
    base_model, prompts = await determine_model_and_prompts(db, body.model_id)

    # Generate explanation
    explanation: str = await generate_explanation(
        body.input_json_schema,
        body.output_json_schema,
        base_model,
        prompts,
        body.jsonata_mapping,
    )

    return explanation
