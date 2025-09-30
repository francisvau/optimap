import pytest
from pydantic import ValidationError

from app.model.model import AIModel, BaseModelType


def test_valid_aimodel_creation():
    """Test creating a valid AIModel instance."""
    model_data = {
        "_id": "123456789012345678901234",
        "name": "Test Model",
        "tailor_prompt": ["prompt1", "prompt2"],
        "base_model": "groq",
    }
    model = AIModel(**model_data)
    assert model.id == "123456789012345678901234"
    assert model.name == "Test Model"
    assert model.tailor_prompt == ["prompt1", "prompt2"]
    assert model.base_model == BaseModelType.groq
    assert model.model_dump(by_alias=True) == model_data


def test_valid_aimodel_without_id():
    """Test creating an AIModel without an id."""
    model_data = {
        "name": "Test Model",
        "tailor_prompt": ["prompt1"],
        "base_model": "deepseek",
    }
    model = AIModel(**model_data)
    assert model.id is None
    assert model.name == "Test Model"
    assert model.tailor_prompt == ["prompt1"]
    assert model.base_model == BaseModelType.deepseek


def test_invalid_base_model():
    """Test validation error for invalid base_model."""
    model_data = {
        "name": "Test Model",
        "tailor_prompt": ["prompt1"],
        "base_model": "invalid",
    }
    with pytest.raises(
        ValidationError,
        match="Input should be 'groq', 'gemini', 'deepseek' or 'openai'",
    ):
        AIModel(**model_data)


def test_missing_required_fields():
    """Test validation error for missing required fields."""
    model_data = {
        "_id": "123456789012345678901234",
        "base_model": "gemini",
        # Missing name and tailor_prompt
    }
    with pytest.raises(ValidationError, match="Field required"):
        AIModel(**model_data)


def test_populate_by_name():
    """Test populate_by_name config allows using 'id' instead of '_id'."""
    model_data = {
        "id": "123456789012345678901234",
        "name": "Test Model",
        "tailor_prompt": ["prompt1"],
        "base_model": "gemini",
    }
    model = AIModel(**model_data)
    assert model.id == "123456789012345678901234"
    assert model.model_dump(by_alias=True)["_id"] == "123456789012345678901234"


def test_empty_tailor_prompt():
    """Test that an empty tailor_prompt list is valid."""
    model_data = {"name": "Test Model", "tailor_prompt": [], "base_model": "deepseek"}
    model = AIModel(**model_data)
    assert model.tailor_prompt == []


def test_json_serialization():
    """Test JSON serialization and deserialization."""
    model_data = {
        "_id": "123456789012345678901234",
        "name": "Test Model",
        "tailor_prompt": ["prompt1", "prompt2"],
        "base_model": "groq",
    }
    model = AIModel(**model_data)
    json_str = model.model_dump_json(by_alias=True)
    deserialized_model = AIModel.model_validate_json(json_str)
    assert deserialized_model == model
