import json
import uuid

import aiofiles
import aiofiles.os

from app.config import UPLOAD_DIR
from app.schema.stream import FileHandleInfo
from app.service.mapping.schema import JSONSchemaGenerator


class StreamFileHandler:
    """Base class for handling file streams asynchronously."""

    def __init__(self, file_type: str, filename: str):
        self.filename = filename
        self.file_info: FileHandleInfo = FileHandleInfo(
            handle=None,
            path="",
            count=0,
            file_type=file_type,
            extracted_schema=None,
        )

    async def create_file(self, extension: str = "json") -> None:
        """Creates a file with a unique ID and the specified extension."""
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}.{extension}"

        # Open file asynchronously for writing
        handle = await aiofiles.open(file_path, "w", encoding="utf-8")
        self.file_info.handle = handle
        self.file_info.path = str(file_path)

    async def finalize(self) -> None:
        """Finalizes the file by closing the handle."""
        if self.file_info.handle:
            await self.file_info.handle.close()

    async def write_data(self, data: list[str]) -> None:
        """Writes data to the file asynchronously."""
        if (
            not self.file_info
            or not self.file_info.handle
            or getattr(self.file_info.handle, "closed", False)
        ):
            raise ValueError("File is not open or already closed.")

        # Write and flush data
        await self.file_info.handle.write("".join(data))
        self.file_info.count += 1

    async def get_schema(self) -> None:
        """Generates a JSON schema for the file content."""
        if not self.file_info.extracted_schema:
            # Read the entire file content asynchronously
            async with aiofiles.open(self.file_info.path, "r", encoding="utf-8") as f:
                content = await f.read()
                json_data = json.loads(content)

            generator = JSONSchemaGenerator()
            self.file_info.extracted_schema = generator.generate(json_data)

    async def delete_file(self) -> None:
        """Delete the saved JSON file asynchronously."""
        if self.file_info.path:
            try:
                await aiofiles.os.remove(self.file_info.path)
            except FileNotFoundError:
                pass  # File might already be deleted
