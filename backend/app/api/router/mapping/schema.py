from fastapi import APIRouter, File, UploadFile

from app.config import MAX_UPLOAD_SIZE_BYTES
from app.exceptions import BadRequest
from app.schema.mapping.schema import (
    ExtractSchemaResponse,
)
from app.service.upload.upload import get_handler

router = APIRouter(prefix="/schema", tags=["schema_extraction"])


@router.post("/schema-extraction")
async def schema_extraction(file: UploadFile = File(...)) -> ExtractSchemaResponse:
    """Extract schema from uploaded file.

    Args:
        file: The file to extract schema from (max 30MB)
    """
    try:
        if not file.size or not file.content_type or not file.filename:
            raise BadRequest("Filename, size and type are required")

        if file.size > MAX_UPLOAD_SIZE_BYTES:
            raise BadRequest("File size exceeds 30MB limit")

        Handler = get_handler(file.content_type)
        if not Handler:
            raise BadRequest(f"Unsupported file type: {file.content_type}")

        handler = Handler(filename=file.filename, file_type=file.content_type)
        await handler.create_file()

        # Read the file and convert it to json
        content = await file.read()
        await handler.write_data(content.decode("utf-8").splitlines())
        await handler.finalize()

        # Get the schema
        await handler.get_schema()
        await handler.delete_file()

        return ExtractSchemaResponse(json_schema=handler.file_info.extracted_schema)
    except ValueError as e:
        raise BadRequest(str(e))
    finally:
        await file.close()
