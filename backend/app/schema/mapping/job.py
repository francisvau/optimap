from datetime import datetime
from typing import Any, Optional

from pydantic import model_validator

from app.model.job import MappingJobType, MappingStatus
from app.schema import BaseSchema
from app.schema.mapping.blueprint import InputDefinitionResponse, SourceMappingResponse
from app.schema.organization import OrganizationResponse
from app.schema.user import UserResponse


class MappingJobValidators(BaseSchema):
    pass


class CreateMappingJobRequest(BaseSchema):
    input_definition_id: int
    user_id: Optional[int] = None
    name: Optional[str] = None
    type: MappingJobType
    external_api_endpoint: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _ensure_endpoint_for_dynamic(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Require `external_api_endpoint` when the mapping job is dynamic."""
        job_type = values.get("type")
        endpoint = values.get("external_api_endpoint")
        if job_type == MappingJobType.DYNAMIC and not endpoint:
            raise ValueError(
                "external_api_endpoint must be provided when type is MappingJobType.DYNAMIC"
            )
        return values


class UpdateMappingJobRequest(BaseSchema):
    name: Optional[str] = None
    organization_id: Optional[int] = None
    status: Optional[MappingStatus] = None
    completed_at: Optional[datetime] = None
    external_api_endpoint: Optional[str] = None
    type: Optional[MappingJobType] = None


class MappingJobResponse(BaseSchema):
    id: int
    name: Optional[str]
    type: MappingJobType
    created_at: datetime
    status: MappingStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    user_id: int
    user: Optional["UserResponse"] = None

    organization_id: Optional[int] = None
    organization: Optional["OrganizationResponse"] = None

    input_definition_id: int
    input_definition: Optional["InputDefinitionResponse"] = None

    executions: Optional[list["MappingExecutionResponse"]] = None

    external_api_endpoint: Optional[str] = None
    uuid: Optional[str] = None


class MappingExecutionResponse(BaseSchema):
    id: int
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    data_size_bytes: int
    status: MappingStatus
    attempts: int
    error_message: Optional[str] = None

    original_file_name: Optional[str] = None
    output_file_name: Optional[str] = None

    mapping_job_id: int
    mapping_job: Optional[MappingJobResponse] = None

    source_mapping_id: int
    source_mapping: Optional[SourceMappingResponse] = None


class CreateMappingExecutionRequest(BaseSchema):
    mapping_job_id: int
    source_mapping_id: int
    data_size_bytes: int


class UpdateMappingExecutionRequest(BaseSchema):
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    status: Optional[MappingStatus] = None


class HandleDynamicMappingJobRequest(BaseSchema):
    forward: bool = True
    data: object
