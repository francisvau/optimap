from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.model.upload import Upload
from test.fixture.config import UPLOAD_DIR


@pytest.mark.asyncio
async def test_create_and_read_upload(upload_svc, user):
    row = await upload_svc.create_upload(
        user_id=user.id,
        original_filename="a.txt",
        generated_filename="gen.txt",
        file_extension=".txt",
        file_size=1,
    )
    fetched = await upload_svc.read_upload(row.file_id)

    assert fetched.file_name == "a.txt"


@pytest.mark.asyncio
async def test_update_upload(upload_svc, user):
    row = await upload_svc.create_upload(
        user_id=user.id,
        original_filename="a.txt",
        generated_filename="gen.txt",
        file_extension=".txt",
        file_size=1,
    )

    updated = await upload_svc.update_upload(row.file_id, original_filename="b.txt")
    assert updated.file_name == "b.txt"


@pytest.mark.asyncio
async def test_handle_file_upload(tmp_path, monkeypatch, upload_svc, user):
    data = b"hello world"
    file = UploadFile(filename="hello.txt", file=BytesIO(data))

    resp = await upload_svc.handle_file_upload(upload_file=file, user_id=user.id)
    saved: Upload = await upload_svc.read_upload(resp.file_id)

    assert saved.file_size == len(data)
    assert Path(UPLOAD_DIR / saved.generated_filename).exists()


@pytest.mark.asyncio
async def test_handle_file_upload_error(tmp_path, monkeypatch, upload_svc, user):
    file = UploadFile(filename="", file=BytesIO())

    with pytest.raises(Exception):
        await upload_svc.handle_file_upload(upload_file=file, user_id=user.id)


@pytest.mark.asyncio
async def test_convert_file_stream_json(tmp_path, monkeypatch, upload_svc, user):
    await upload_svc.convert_file_stream(
        file_type="json",
        filename="data.json",
        chunks=['{"x": 1}', '{"x": 2}'],
        user_id=user.id,
    )

    resp = await upload_svc.convert_file_stream(
        file_type="json",
        filename="data.json",
        chunks=['{"x": 3}'],
        user_id=user.id,
        complete=True,
    )

    saved = await upload_svc.read_upload(resp.file_id)

    assert saved.file_name == "data.json"
    assert Path(UPLOAD_DIR / saved.generated_filename).stat().st_size > 0


@pytest.mark.asyncio
async def test_convert_file_stream_unsupported(upload_svc, user):
    with pytest.raises(Exception):
        await upload_svc.convert_file_stream(
            file_type="unknown",
            filename="bad.ext",
            chunks=[],
            user_id=user.id,
        )
