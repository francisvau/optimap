from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BeforeValidator, field_validator

from app.schema import BaseSchema
from app.schema.mapping.schema import Schema
from app.schema.organization import OrganizationResponse
from app.schema.user import UserResponse
from app.util.schema import DEFAULT_JSON_SCHEMA, validate_draft7_schema

"""Output Definitions"""


class OutputDefinitionValidators(BaseSchema):
    """Mixin to share your validators without sharing the fields."""

    @field_validator("name", check_fields=False)
    def validate_name(cls, value: str) -> str:
        """
        Validate the name of the blueprint.
        The name must be unique and not empty.
        """
        return value.title()


class CreateOutputDefinitionRequest(OutputDefinitionValidators):
    """Create Output Definition Request"""

    name: Optional[str] = None
    description: Optional[str] = None
    json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)] = (
        DEFAULT_JSON_SCHEMA
    )


class UpdateOutputDefinitionRequest(OutputDefinitionValidators):
    """Update Output Definition Request"""

    name: Optional[str] = None
    description: Optional[str] = None
    json_schema: Annotated[
        Optional[Schema], BeforeValidator(validate_draft7_schema)
    ] = None


class OutputDefinitionResponse(BaseSchema):
    """Output Definition Response"""

    id: int
    name: Optional[str]
    description: Optional[str]
    json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]


"""Mappings"""


class MappingValidators(BaseSchema):
    """Mixin to share your validators without sharing the fields."""

    pass


class CreateMappingRequest(MappingValidators):
    """Create Mapping Request"""

    name: Optional[str] = None
    model_id: Optional[str] = None
    jsonata_mapping: Optional[str] = None
    input_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)] = (
        DEFAULT_JSON_SCHEMA
    )
    output_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)] = (
        DEFAULT_JSON_SCHEMA
    )


class UpdateMappingRequest(MappingValidators):
    """Update Mapping Request"""

    name: Optional[str] = None
    model_id: Optional[str] = None
    jsonata_mapping: Optional[str] = None
    input_json_schema: Annotated[
        Optional[Schema], BeforeValidator(validate_draft7_schema)
    ] = None
    output_json_schema: Annotated[
        Optional[Schema], BeforeValidator(validate_draft7_schema)
    ] = None

    target_path: Optional[str] = None


class SourceMappingResponse(BaseSchema):
    """Source Mapping Response"""

    id: int
    name: Optional[str] = None
    file_type: Optional[str] = "JSON"
    input_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]
    jsonata_mapping: Optional[str]
    output_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]
    model_id: Optional[str] = None
    target_path: str


class PreviousMapping(BaseSchema):
    """Previous Mapping for fine-tuning"""

    input_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]
    output_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]
    jsonata_mapping: str


class JsonataGenerationRequest(BaseSchema):
    """Jsonata Generation Request"""

    input_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]
    output_json_schema: Annotated[Schema, BeforeValidator(validate_draft7_schema)]
    model_id: Optional[str] = None
    previous_mappings: List[PreviousMapping] = []


class GenerateMappingRequest(BaseSchema):
    """Request body for generating a mapping"""

    model: Optional[str] = None
    organization_id: Optional[int] = None
    finetuning: Optional[bool] = None


class JsonataGenerationResponse(BaseSchema):
    """Jsonata Generation Response"""

    mapping: str
    retries: int
    corrupted: bool
    error_message: Optional[str] = None


"""Input Definitions"""


class InputDefinitionValidators(BaseSchema):
    """Mixin to share your validators without sharing the fields."""

    @field_validator("name", check_fields=False)
    def title_name(cls, v: str) -> str:
        return v.title()

    @field_validator("description", check_fields=False)
    def capitalize_description(cls, v: str) -> str:
        return v.capitalize()


class CreateInputDefinitionRequest(InputDefinitionValidators):
    """Create Input Definition Request"""

    name: str
    description: Optional[str] = None


class UpdateInputDefinitionRequest(InputDefinitionValidators):
    """Update Input Definition Request"""

    name: Optional[str] = None
    description: Optional[str] = None


class InputDefinitionResponse(BaseSchema):
    """Input Definition Response"""

    id: int
    name: str
    description: Optional[str]
    source_mappings: list[SourceMappingResponse] = []
    blueprint: Optional["BlueprintResponse"] = None
    version_group_id: str
    version: int
    is_selected: bool


"""Blueprints"""


class BlueprintValidators(BaseSchema):
    """Mixin to share your validators without sharing the fields."""

    @field_validator("name", check_fields=False)
    def _title_name(cls, v: str) -> str:
        return v.title()

    @field_validator("description", check_fields=False)
    def _capitalize_description(cls, v: str) -> str:
        return v.capitalize()


class CreateBlueprintRequest(BlueprintValidators):
    """Create Mapping Blueprint Request"""

    name: str
    description: str
    model_prompt: Optional[str] = None
    user_id: Optional[int] = None
    organization_id: Optional[int] = None


class UpdateBlueprintRequest(BlueprintValidators):
    """Update Mapping Blueprint Request"""

    name: Optional[str] = None
    description: Optional[str] = None
    model_prompt: Optional[str] = None
    user_id: Optional[int] = None
    organization_id: Optional[int] = None


class BlueprintResponse(BaseSchema):
    """Mapping Blueprint Response"""

    id: int
    name: str
    description: str
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    input_definitions: Optional[List[InputDefinitionResponse]] = None
    output_definition: Optional[OutputDefinitionResponse] = None

    organization_id: Optional[int]
    organization: Optional[OrganizationResponse] = None

    user_id: int
    user: Optional[UserResponse] = None
