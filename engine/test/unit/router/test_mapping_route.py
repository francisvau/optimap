from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.router import mapping
from app.schema.mapping import (
    JsonataEditingRequest,
    JsonataExplanationRequest,
    JsonataGenerationRequest,
    JsonataGenerationResponse,
)

# Dummy test app
app = FastAPI()
app.include_router(mapping.router)


@pytest.fixture
def fake_generation_request():
    return JsonataGenerationRequest(
        model_id="test-model-id",
        input_json_schema={"type": "object", "properties": {"a": {"type": "string"}}},
        output_json_schema={"type": "object", "properties": {"b": {"type": "string"}}},
    )


@pytest.fixture
def fake_editing_request():
    return JsonataEditingRequest(
        model_id="test-model-id",
        input_json_schema={"type": "object"},
        output_json_schema={"type": "object"},
        jsonata_mapping="$a",
        context="Make it map 'a' to 'b'",
    )


@pytest.fixture
def fake_explanation_request():
    return JsonataExplanationRequest(
        model_id="test-model-id",
        input_json_schema={"type": "object"},
        output_json_schema={"type": "object"},
        jsonata_mapping="$a",
    )


@pytest.mark.asyncio
@patch("app.router.mapping.determine_model_and_prompts", new_callable=AsyncMock)
@patch("app.router.mapping.generate_mapping_from_schemas", new_callable=AsyncMock)
async def test_generate_mapping(mock_generate, mock_determine, fake_generation_request):
    mock_determine.return_value = ("mock-model", {"prompt": "test"})
    mock_generate.return_value = JsonataGenerationResponse(
        mapping="$b", retries=0, corrupted=False
    )

    client = TestClient(app)
    res = client.post("/mappings/generate", json=fake_generation_request.dict())
    assert res.status_code == 200
    assert res.json() == {
        "mapping": "$b",
        "retries": 0,
        "corrupted": False,
        "error_message": None,
    }


@pytest.mark.asyncio
@patch("app.router.mapping.determine_model_and_prompts", new_callable=AsyncMock)
@patch("app.router.mapping.generate_edited_mapping", new_callable=AsyncMock)
async def test_edit_mapping(mock_edit, mock_determine, fake_editing_request):
    mock_determine.return_value = ("mock-model", {"prompt": "edit"})
    mock_edit.return_value = "$b"

    client = TestClient(app)
    res = client.post("/mappings/edit", json=fake_editing_request.model_dump())
    assert res.status_code == 200
    assert res.json() == "$b"


@pytest.mark.asyncio
@patch("app.router.mapping.determine_model_and_prompts", new_callable=AsyncMock)
@patch("app.router.mapping.generate_explanation", new_callable=AsyncMock)
async def test_explanation(mock_explain, mock_determine, fake_explanation_request):
    mock_determine.return_value = ("mock-model", {"prompt": "explain"})
    mock_explain.return_value = "This mapping maps $a to something"

    client = TestClient(app)
    res = client.post("/mappings/explanation", json=fake_explanation_request.dict())
    assert res.status_code == 200
    assert "maps $a" in res.text
