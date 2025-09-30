from typing import Annotated, List, Optional

from pydantic import ConfigDict, Field

from app.schema import BaseSchema


class FileUploadRequest(BaseSchema):
    file_name: str
    file_type: str
    file_size: int


class FileUploadResponse(BaseSchema):
    file_id: Annotated[int, Field(alias="id")]
    file_name: Annotated[str, Field(alias="original_filename")]
    upload_status: str
    message: Optional[str] = None
    file_size: Annotated[int, Field(alias="file_size")]
    generated_filename: Annotated[str, Field(alias="generated_filename")]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class BulkFileUploadRequest(BaseSchema):
    files: List[FileUploadRequest]


class BulkFileUploadResponse(BaseSchema):
    successful_uploads: List[FileUploadResponse]
    failed_uploads: List[FileUploadResponse]
