from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from app.model.model import AIModel, BaseModelType
from app.service.db import (
    _fetch_model_and_prompts,
    determine_model_and_prompts,
    get_model_by_id,
)


@pytest.fixture
def mock_db():
    """Fixture for a mocked MongoDbDep."""
    db = MagicMock()
    db.ai_models = MagicMock()
    db.ai_models.find_one = AsyncMock()
    return db


@pytest.fixture
def valid_model_data():
    """Fixture for valid AIModel data, dynamically using DEFAULT_MODEL's base_model."""
    return {
        "_id": ObjectId("123456789012345678901234"),
        "name": "Test Model",
        "tailor_prompt": ["prompt1", "prompt2"],
        "base_model": "gemini",
    }


@pytest.fixture
def valid_model(valid_model_data):
    """Fixture for a valid AIModel instance."""
    return AIModel.model_validate(valid_model_data)


@pytest.mark.asyncio
async def test_get_model_by_id_success(mock_db, valid_model, valid_model_data):
    """Test get_model_by_id with a valid model ID."""
    mock_db.ai_models.find_one.return_value = valid_model_data
    result = await get_model_by_id("123456789012345678901234", mock_db)
    assert result == valid_model
    mock_db.ai_models.find_one.assert_awaited_once_with(
        {"_id": ObjectId("123456789012345678901234")}
    )


@pytest.mark.asyncio
async def test_get_model_by_id_not_found(mock_db):
    """Test get_model_by_id when model is not found."""
    mock_db.ai_models.find_one.return_value = None
    with pytest.raises(HTTPException) as exc:
        await get_model_by_id("123456789012345678901234", mock_db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Model not found"
    mock_db.ai_models.find_one.assert_awaited_once_with(
        {"_id": ObjectId("123456789012345678901234")}
    )


@pytest.mark.asyncio
async def test_get_model_by_id_invalid_id(mock_db):
    """Test get_model_by_id with an invalid ObjectId."""
    with pytest.raises(InvalidId, match="'invalid_id' is not a valid ObjectId"):
        await get_model_by_id("invalid_id", mock_db)
    mock_db.ai_models.find_one.assert_not_awaited()


@pytest.mark.asyncio
async def test_determine_model_and_prompts_with_model_id(mock_db, valid_model_data):
    """Test determine_model_and_prompts with a provided model ID."""
    mock_db.ai_models.find_one.return_value = valid_model_data
    base_model, prompts = await determine_model_and_prompts(
        mock_db, "123456789012345678901234"
    )
    assert base_model == BaseModelType.gemini
    assert prompts == ["prompt1", "prompt2"]
    mock_db.ai_models.find_one.assert_awaited_once_with(
        {"_id": ObjectId("123456789012345678901234")}
    )


@pytest.mark.asyncio
async def test_determine_model_and_prompts_default_model(mock_db):
    """Test determine_model_and_prompts with default model."""
    # Assume DEFAULT_MODEL is a BaseModelType like "gemini"
    base_model, prompts = await determine_model_and_prompts(mock_db, None)
    assert base_model == BaseModelType.gemini
    assert prompts == []
    mock_db.ai_models.find_one.assert_not_awaited()


@pytest.mark.asyncio
async def test_determine_model_and_prompts_model_not_found(mock_db):
    """Test determine_model_and_prompts when model is not found."""
    mock_db.ai_models.find_one.return_value = None
    with pytest.raises(HTTPException) as exc:
        await determine_model_and_prompts(mock_db, "123456789012345678901234")
    assert exc.value.status_code == 404
    assert exc.value.detail == "Model with id 123456789012345678901234 not found"
    mock_db.ai_models.find_one.assert_awaited_once_with(
        {"_id": ObjectId("123456789012345678901234")}
    )


@pytest.mark.asyncio
async def test_fetch_model_and_prompts_base_model_type(mock_db):
    """Test _fetch_model_and_prompts with a BaseModelType value."""
    base_model, prompts = await _fetch_model_and_prompts(mock_db, "groq")
    assert base_model == BaseModelType.groq
    assert prompts == []
    mock_db.ai_models.find_one.assert_not_awaited()


@pytest.mark.asyncio
async def test_fetch_model_and_prompts_model_id(mock_db, valid_model_data):
    """Test _fetch_model_and_prompts with a model ID."""
    mock_db.ai_models.find_one.return_value = valid_model_data
    base_model, prompts = await _fetch_model_and_prompts(
        mock_db, "123456789012345678901234"
    )
    assert base_model == BaseModelType.gemini
    assert prompts == ["prompt1", "prompt2"]
    mock_db.ai_models.find_one.assert_awaited_once_with(
        {"_id": ObjectId("123456789012345678901234")}
    )


@pytest.mark.asyncio
async def test_fetch_model_and_prompts_not_found(mock_db):
    """Test _fetch_model_and_prompts when model is not found."""
    mock_db.ai_models.find_one.return_value = None
    with pytest.raises(HTTPException) as exc:
        await _fetch_model_and_prompts(mock_db, "123456789012345678901234")
    assert exc.value.status_code == 404
    assert exc.value.detail == "Model with id 123456789012345678901234 not found"
    mock_db.ai_models.find_one.assert_awaited_once_with(
        {"_id": ObjectId("123456789012345678901234")}
    )


@pytest.mark.asyncio
async def test_fetch_model_and_prompts_invalid_base_model(mock_db):
    """Test _fetch_model_and_prompts with an invalid BaseModelType."""
    with patch.object(
        BaseModelType,
        "__new__",
        side_effect=ValueError("'invalid_id' is not a valid BaseModelType"),
    ):
        with pytest.raises(
            InvalidId,
            match="'invalid_id' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string",
        ):
            await _fetch_model_and_prompts(mock_db, "invalid_id")
    mock_db.ai_models.find_one.assert_not_awaited()


@pytest.mark.asyncio
async def test_fetch_model_and_prompts_invalid_object_id(mock_db):
    """Test _fetch_model_and_prompts with an invalid ObjectId (non-enum)."""
    invalid_id = "abcdef1234567890abcdef12"  # Valid hex but not in DB
    mock_db.ai_models.find_one.return_value = None
    with pytest.raises(HTTPException, match=f"Model with id {invalid_id} not found"):
        await _fetch_model_and_prompts(mock_db, invalid_id)
    mock_db.ai_models.find_one.assert_awaited_once_with({"_id": ObjectId(invalid_id)})
