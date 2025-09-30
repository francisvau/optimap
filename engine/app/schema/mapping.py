from typing import Any, List, Optional

from pydantic import BaseModel

from app.config import DEFAULT_MODEL

Schema = dict[str, Any]


class PreviousMapping(BaseModel):
    input_json_schema: Schema
    output_json_schema: Schema
    jsonata_mapping: str


class JsonataGenerationRequest(BaseModel):
    input_json_schema: Schema
    output_json_schema: Schema
    model_id: Optional[str] = DEFAULT_MODEL
    previous_mappings: Optional[List[PreviousMapping]] = []


class JsonataEditingRequest(BaseModel):
    input_json_schema: Schema
    output_json_schema: Schema
    jsonata_mapping: str
    context: str
    model_id: Optional[str] = DEFAULT_MODEL


class JsonataExplanationRequest(BaseModel):
    input_json_schema: Schema
    output_json_schema: Schema
    jsonata_mapping: str
    model_id: Optional[str] = DEFAULT_MODEL


class JsonataGenerationResponse(BaseModel):
    mapping: str
    retries: int
    corrupted: bool
    error_message: Optional[str] = None
