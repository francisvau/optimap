from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.model.model import BaseModelType
from app.schema.mapping import JsonataGenerationResponse
from app.service.mapping import (
    MappingError,
    generate_edited_mapping,
    generate_explanation,
    generate_mapping_from_schemas,
    retry_generate_mapping,
    validate_mapping,
)


@pytest.fixture
def input_json_schema():
    """Fixture for a sample input JSON schema."""
    return {
        "type": "object",
        "properties": {"age": {"type": "integer"}, "name": {"type": "string"}},
        "required": ["age", "name"],
    }


@pytest.fixture
def output_json_schema():
    """Fixture for a sample output JSON schema."""
    return {
        "type": "object",
        "properties": {"age": {"type": "integer"}},
        "required": ["age"],
    }


@pytest.fixture
def jsonata_mapping():
    """Fixture for a sample JSONata mapping."""
    return "$filter($, function($v) { $v.age > 30 })"


@pytest.fixture
def prompts():
    """Fixture for a sample list of prompts."""
    return ["Ensure the mapping filters items where age > 30."]


@pytest.fixture
def prev_mappings():
    """Fixture for a sample list of previous mappings."""
    return [
        {
            "input_json_schema": {"x": 1},
            "output_json_schema": {"y": 2},
            "jsonata_mapping": "$a",
        },
        {
            "input_json_schema": {"a": "b"},
            "output_json_schema": {"c": "d"},
            "jsonata_mapping": "$b",
        },
    ]


@pytest.fixture
def mock_jsf():
    """Fixture for a mocked JSF instance."""
    jsf = MagicMock()
    jsf.generate.return_value = {"age": 35, "name": "John"}
    return jsf


@pytest.fixture
def mock_jsonata():
    """Fixture for a mocked Jsonata instance."""
    expr = MagicMock()
    expr.evaluate.return_value = {"age": 35}
    return MagicMock(return_value=expr)


def test_validate_mapping_success(
    input_json_schema, output_json_schema, jsonata_mapping, mock_jsf, mock_jsonata
):
    """Test validate_mapping with a valid mapping."""
    with (
        patch("app.service.mapping.JSF", return_value=mock_jsf),
        patch("app.service.mapping.jsonata.Jsonata", mock_jsonata),
        patch("app.service.mapping.validate") as mock_validate,
    ):
        validate_mapping(input_json_schema, output_json_schema, jsonata_mapping)
        mock_jsf.generate.assert_called_once()
        mock_jsonata.assert_called_once_with(jsonata_mapping)
        mock_jsonata().evaluate.assert_called_once_with({"age": 35, "name": "John"})
        mock_validate.assert_called_once_with(
            instance={"age": 35}, schema=output_json_schema
        )


def test_validate_mapping_invalid_jsonata(
    input_json_schema, output_json_schema, jsonata_mapping
):
    """Test validate_mapping with an invalid JSONata expression."""
    with (
        patch(
            "app.service.mapping.jsonata.Jsonata", side_effect=Exception("Syntax error")
        ),
    ):
        with pytest.raises(
            MappingError, match="Error in JSONata expression:\nSyntax error"
        ):
            validate_mapping(input_json_schema, output_json_schema, jsonata_mapping)


def test_validate_mapping_evaluation_error(
    input_json_schema, output_json_schema, jsonata_mapping, mock_jsf, mock_jsonata
):
    """Test validate_mapping with an evaluation error."""
    mock_jsonata().evaluate.side_effect = Exception("Evaluation failed")
    with (
        patch("app.service.mapping.JSF", return_value=mock_jsf),
        patch("app.service.mapping.jsonata.Jsonata", mock_jsonata),
    ):
        with pytest.raises(
            MappingError,
            match="Error evaluating JSONata expression on JSON following the JSON input schema rules:\nEvaluation failed",
        ):
            validate_mapping(input_json_schema, output_json_schema, jsonata_mapping)
        mock_jsf.generate.assert_called_once()


def test_validate_mapping_schema_validation_error(
    input_json_schema, output_json_schema, jsonata_mapping, mock_jsf, mock_jsonata
):
    """Test validate_mapping with an output schema validation error."""
    with (
        patch("app.service.mapping.JSF", return_value=mock_jsf),
        patch("app.service.mapping.jsonata.Jsonata", mock_jsonata),
        patch("app.service.mapping.validate", side_effect=Exception("Schema mismatch")),
    ):
        with pytest.raises(
            MappingError,
            match="The JSON output does not conform to the JSON output schema. Here's the error:\nSchema mismatch",
        ):
            validate_mapping(input_json_schema, output_json_schema, jsonata_mapping)
        mock_jsonata().evaluate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_mapping_from_schemas_success(
    input_json_schema, output_json_schema, jsonata_mapping, prompts, prev_mappings
):
    """Test generate_mapping_from_schemas with a valid mapping."""
    with (
        patch("app.service.mapping.create_mapping_prompt") as mock_prompt,
        patch(
            "app.service.mapping.get_model_output",
            AsyncMock(return_value=jsonata_mapping),
        ),
        patch("app.service.mapping.validate_mapping") as mock_validate,
    ):
        mock_prompt.return_value = ("system", "user")
        result = await generate_mapping_from_schemas(
            input_json_schema,
            output_json_schema,
            BaseModelType.groq,
            prompts,
            retries=2,
            previous_mappings=prev_mappings,
        )
        assert result == JsonataGenerationResponse(
            mapping=jsonata_mapping,
            retries=0,
            corrupted=False,
            error_message=None,
        )
        mock_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, prompts, prev_mappings
        )
        mock_validate.assert_called_once_with(
            input_json_schema, output_json_schema, jsonata_mapping
        )


@pytest.mark.asyncio
async def test_generate_mapping_from_schemas_retry_different_error(
    input_json_schema, output_json_schema, jsonata_mapping, prompts, prev_mappings
):
    """Test generate_mapping_from_schemas with retries on different errors."""
    with (
        patch("app.service.mapping.create_mapping_prompt") as mock_prompt,
        patch("app.service.mapping.create_mapping_retry_prompt") as mock_retry_prompt,
        patch(
            "app.service.mapping.get_model_output",
            AsyncMock(side_effect=[jsonata_mapping, "new_mapping"]),
        ),
        patch(
            "app.service.mapping.validate_mapping",
            side_effect=[MappingError("Error1"), MappingError("Error2")],
        ),
    ):
        mock_prompt.return_value = ("system", "user")
        mock_retry_prompt.return_value = ("retry_system", "retry_user")
        result = await generate_mapping_from_schemas(
            input_json_schema,
            output_json_schema,
            BaseModelType.groq,
            prompts,
            retries=1,
            previous_mappings=prev_mappings,
        )
        assert result == JsonataGenerationResponse(
            mapping="new_mapping",
            retries=1,
            corrupted=True,
            error_message="Error1",
        )
        mock_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, prompts, prev_mappings
        )
        mock_retry_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, jsonata_mapping, prompts, "Error1"
        )


@pytest.mark.asyncio
async def test_generate_mapping_from_schemas_no_retries(
    input_json_schema, output_json_schema, jsonata_mapping, prompts, prev_mappings
):
    """Test generate_mapping_from_schemas with zero retries."""
    with (
        patch("app.service.mapping.create_mapping_prompt") as mock_prompt,
        patch(
            "app.service.mapping.get_model_output",
            AsyncMock(return_value=jsonata_mapping),
        ),
        patch(
            "app.service.mapping.validate_mapping", side_effect=MappingError("Error")
        ),
    ):
        mock_prompt.return_value = ("system", "user")
        result = await generate_mapping_from_schemas(
            input_json_schema,
            output_json_schema,
            BaseModelType.groq,
            prompts,
            retries=0,
            previous_mappings=prev_mappings,
        )
        assert result == JsonataGenerationResponse(
            mapping=jsonata_mapping,
            retries=0,
            corrupted=False,
            error_message=None,
        )
        mock_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, prompts, prev_mappings
        )


@pytest.mark.asyncio
async def test_retry_generate_mapping(
    input_json_schema, output_json_schema, jsonata_mapping, prompts
):
    """Test retry_generate_mapping."""
    with (
        patch("app.service.mapping.create_mapping_retry_prompt") as mock_prompt,
        patch(
            "app.service.mapping.get_model_output",
            AsyncMock(return_value="new_mapping"),
        ),
    ):
        mock_prompt.return_value = ("retry_system", "retry_user")
        result = await retry_generate_mapping(
            input_json_schema,
            output_json_schema,
            jsonata_mapping,
            BaseModelType.groq,
            prompts,
            "Error",
        )
        assert result == "new_mapping"
        mock_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, jsonata_mapping, prompts, "Error"
        )


@pytest.mark.asyncio
async def test_generate_explanation(
    input_json_schema, output_json_schema, jsonata_mapping, prompts
):
    """Test generate_explanation."""
    with (
        patch("app.service.mapping.create_explanation_prompt") as mock_prompt,
        patch(
            "app.service.mapping.get_model_output",
            AsyncMock(return_value="This mapping filters items where age > 30."),
        ),
    ):
        mock_prompt.return_value = ("system", "user")
        result = await generate_explanation(
            input_json_schema,
            output_json_schema,
            BaseModelType.groq,
            prompts,
            jsonata_mapping,
        )
        assert result == "This mapping filters items where age > 30."
        mock_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, prompts, jsonata_mapping
        )


@pytest.mark.asyncio
async def test_generate_edited_mapping(
    input_json_schema, output_json_schema, jsonata_mapping, prompts
):
    """Test generate_edited_mapping."""
    context = "Change the filter to age > 40."
    with (
        patch("app.service.mapping.create_edit_prompt") as mock_prompt,
        patch(
            "app.service.mapping.get_model_output",
            AsyncMock(return_value="new_mapping"),
        ),
    ):
        mock_prompt.return_value = ("system", "user")
        result = await generate_edited_mapping(
            input_json_schema,
            output_json_schema,
            jsonata_mapping,
            context,
            BaseModelType.groq,
            prompts,
        )
        assert result == "new_mapping"
        mock_prompt.assert_called_once_with(
            input_json_schema, output_json_schema, jsonata_mapping, context, prompts
        )
