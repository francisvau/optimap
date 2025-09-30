from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Type

from fastapi import UploadFile
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import UPLOAD_DIR
from app.exceptions import EntityNotPresent, FileUploadFailed
from app.model.upload import Upload
from app.schema.upload import FileUploadResponse
from app.service.upload.handlers.csv import CSVStreamFileHandler
from app.service.upload.handlers.json import JSONStreamFileHandler
from app.service.upload.handlers.sql import SQLStreamFileHandler
from app.service.upload.handlers.utils import StreamFileHandler
from app.service.upload.handlers.xml import XMLStreamFileHandler


def get_handler(file_type: str) -> Type[StreamFileHandler] | None:
    try:
        return {
            "application/json": JSONStreamFileHandler,
            "text/csv": CSVStreamFileHandler,
            "application/xml": XMLStreamFileHandler,
            "text/xml": XMLStreamFileHandler,
            "application/sql": SQLStreamFileHandler,
            "text/sql": SQLStreamFileHandler,
        }.get(file_type)
    except KeyError:
        raise ValueError(f"Unsupported file type: {file_type}")


_HANDLER: Dict[str, type] = {
    "json": JSONStreamFileHandler,
    "csv": CSVStreamFileHandler,
    "xml": XMLStreamFileHandler,
}


class FileUploadService:
    """Save files, update rows and convert streamed data to disk."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._streams: Dict[str, Any] = {}

    async def read_upload(self, upload_id: int) -> FileUploadResponse:
        """Read an upload record from the database."""
        row = await self.db.scalar(select(Upload).where(Upload.id == upload_id))

        if not row:
            raise EntityNotPresent("upload not found")

        return FileUploadResponse.model_validate(
            row.to_dict() | {"upload_status": "success"}
        )

    async def create_upload(
        self,
        *,
        user_id: int,
        original_filename: str,
        generated_filename: str,
        file_extension: str,
        file_size: int,
    ) -> FileUploadResponse:
        """Create a new upload record in the database."""
        upload = await self.db.scalar(
            insert(Upload)
            .values(
                user_id=user_id,
                original_filename=original_filename,
                generated_filename=generated_filename,
                file_extension=file_extension,
                file_size=file_size,
            )
            .returning(Upload)
        )

        if not upload:
            raise FileUploadFailed("Upload record could not be created")

        return FileUploadResponse.model_validate(
            upload.to_dict() | {"upload_status": "success"}
        )

    async def update_upload(self, upload_id: int, **changes: Any) -> FileUploadResponse:
        """Update an existing upload record in the database."""
        row = await self.db.scalar(
            update(Upload)
            .where(Upload.id == upload_id)
            .values(changes)
            .returning(Upload)
        )

        if not row:
            raise EntityNotPresent("upload not found")

        return FileUploadResponse.model_validate(
            row.to_dict() | {"upload_status": "success"}
        )

    async def handle_file_upload(
        self,
        *,
        upload_file: UploadFile,
        user_id: int,
    ) -> FileUploadResponse:
        """Handle file upload and save it to disk."""
        if not upload_file.filename:
            raise FileUploadFailed("file name missing")

        ext = Path(upload_file.filename).suffix
        generated = f"{uuid.uuid4()}{ext}"
        path = UPLOAD_DIR / generated

        try:
            data = await upload_file.read()
            path.write_bytes(data)

            row = await self.create_upload(
                user_id=user_id,
                original_filename=upload_file.filename,
                generated_filename=generated,
                file_extension=ext,
                file_size=len(data),
            )

            return row
        except Exception as exc:
            path.unlink(missing_ok=True)
            raise FileUploadFailed(str(exc))

    async def convert_file_stream(
        self,
        *,
        file_type: str,
        filename: str,
        chunks: Iterable[Dict[str, Any]],
        user_id: int,
        complete: bool = False,
    ) -> Optional[FileUploadResponse]:
        """Convert streamed data to a file on disk."""
        if file_type not in _HANDLER:
            raise FileUploadFailed("unsupported type")

        if filename not in self._streams:
            handler_cls = _HANDLER[file_type]
            handler = handler_cls(filename)
            await handler.create_file()
            self._streams[filename] = handler

        handler = self._streams[filename]
        await handler.write_data(list(chunks))

        if not complete:
            return None

        await handler.finalize()

        path = Path(handler.file_info.path)

        return await self.create_upload(
            user_id=user_id,
            original_filename=filename,
            generated_filename=path.name,
            file_extension=path.suffix,
            file_size=path.stat().st_size,
        )
