from typing import Any, Optional

from app.schema import BaseSchema


class FileHandleInfo(BaseSchema):
    handle: Any
    path: str
    count: int
    file_type: str
    extracted_schema: Optional[dict[str, Any]]
