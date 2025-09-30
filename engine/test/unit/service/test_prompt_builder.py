from typing import List

import pytest

from app.schema.mapping import Schema
from app.service.prompt_builder import (
    create_edit_prompt,
    create_explanation_prompt,
    create_mapping_prompt,
    create_mapping_retry_prompt,
)


@pytest.fixture
def input_json_schema() -> Schema:
    """Fixture for a sample input JSON schema."""
    return {
        "type": "object",
        "properties": {"age": {"type": "integer"}, "name": {"type": "string"}},
        "required": ["age", "name"],
    }


@pytest.fixture
def output_json_schema() -> Schema:
    """Fixture for a sample output JSON schema."""
    return {
        "type": "object",
        "properties": {"age": {"type": "integer"}},
        "required": ["age"],
    }


@pytest.fixture
def prompts() -> List[str]:
    """Fixture for a sample list of prompts."""
    return ["Ensure the mapping filters items where age > 30."]


@pytest.fixture
def jsonata_mapping() -> str:
    """Fixture for a sample JSONata mapping."""
    return "$filter($, function($v) { $v.age > 30 })"


@pytest.fixture
def context() -> str:
    """Fixture for a sample context."""
    return "Change the filter to age > 40."


@pytest.fixture
def error_message() -> str:
    """Fixture for a sample error message."""
    return "Error evaluating JSONata expression: Invalid filter."


def test_create_mapping_prompt(
    input_json_schema: Schema, output_json_schema: Schema, prompts: List[str]
):
    """Test create_mapping_prompt constructs prompts correctly."""
    system_prompt, user_prompt = create_mapping_prompt(
        input_json_schema, output_json_schema, prompts
    )

    assert system_prompt.startswith("You are an")
    assert "Write a JSONata expression" in user_prompt
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert prompts[0] in user_prompt
    assert "Here is additional context information that may help:" in user_prompt


def test_create_mapping_prompt_no_prompts(
    input_json_schema: Schema, output_json_schema: Schema
):
    """Test create_mapping_prompt with empty prompts."""
    system_prompt, user_prompt = create_mapping_prompt(
        input_json_schema, output_json_schema, []
    )

    assert system_prompt.startswith("You are an")
    assert "Write a JSONata expression" in user_prompt
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert "Here is additional context information that may help:" not in user_prompt


def test_create_explanation_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    prompts: List[str],
    jsonata_mapping: str,
):
    """Test create_explanation_prompt constructs prompts correctly."""
    system_prompt, user_prompt = create_explanation_prompt(
        input_json_schema, output_json_schema, prompts, jsonata_mapping
    )

    assert system_prompt == (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Given a JSONata expression that maps an input JSON schema to an output JSON schema, your task is to explain the mapping field by field. "
        "For each output field, clearly describe:\n"
        "- Where the data comes from in the input schema (input path).\n"
        "- What transformations, if any, are applied (e.g., renaming, formatting, calculations, conditions).\n"
        "The output should be in the following format:\n"
        "[output field]: [explanation]\n[output field]: [explanation]\n...\n"
        "Don't use any markdown formatting, just plain text."
    )
    assert (
        "Explain how the following JSONata expression transforms the input JSON schema"
        in user_prompt
    )
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert jsonata_mapping in user_prompt
    assert prompts[0] in user_prompt
    assert "Here is additional context information that may help:" in user_prompt


def test_create_explanation_prompt_no_prompts(
    input_json_schema: Schema, output_json_schema: Schema, jsonata_mapping: str
):
    """Test create_explanation_prompt with empty prompts."""
    system_prompt, user_prompt = create_explanation_prompt(
        input_json_schema, output_json_schema, [], jsonata_mapping
    )

    assert system_prompt == (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Given a JSONata expression that maps an input JSON schema to an output JSON schema, your task is to explain the mapping field by field. "
        "For each output field, clearly describe:\n"
        "- Where the data comes from in the input schema (input path).\n"
        "- What transformations, if any, are applied (e.g., renaming, formatting, calculations, conditions).\n"
        "The output should be in the following format:\n"
        "[output field]: [explanation]\n[output field]: [explanation]\n...\n"
        "Don't use any markdown formatting, just plain text."
    )
    assert (
        "Explain how the following JSONata expression transforms the input JSON schema"
        in user_prompt
    )
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert jsonata_mapping in user_prompt
    assert "Here is additional context information that may help:" not in user_prompt


def test_create_edit_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    prompts: List[str],
    jsonata_mapping: str,
    context: str,
):
    """Test create_edit_prompt constructs prompts correctly."""
    system_prompt, user_prompt = create_edit_prompt(
        input_json_schema, output_json_schema, jsonata_mapping, context, prompts
    )

    assert system_prompt == (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Your task is to edit a JSONata expression that transforms an input JSON schema into a fixed output schema. "
        "You are not allowed to define your own JSONata functions, use function chaining or regular expressions. "
        "Try to keep the JSONata expression as simple as possible. "
        "Make sure the JSONata expression handles each field specifiied in the output JSON schema. "
        "Return only the JSONata expression in your response, without any explanations or formatting."
    )
    assert (
        "Edit the following JSONata expression to better fit the specified context"
        in user_prompt
    )
    assert context in user_prompt
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert jsonata_mapping in user_prompt
    assert prompts[0] in user_prompt
    assert "Here is additional context information that may help:" in user_prompt


def test_create_edit_prompt_no_prompts(
    input_json_schema: Schema,
    output_json_schema: Schema,
    jsonata_mapping: str,
    context: str,
):
    """Test create_edit_prompt with empty prompts."""
    system_prompt, user_prompt = create_edit_prompt(
        input_json_schema, output_json_schema, jsonata_mapping, context, []
    )

    assert system_prompt == (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Your task is to edit a JSONata expression that transforms an input JSON schema into a fixed output schema. "
        "You are not allowed to define your own JSONata functions, use function chaining or regular expressions. "
        "Try to keep the JSONata expression as simple as possible. "
        "Make sure the JSONata expression handles each field specifiied in the output JSON schema. "
        "Return only the JSONata expression in your response, without any explanations or formatting."
    )
    assert (
        "Edit the following JSONata expression to better fit the specified context"
        in user_prompt
    )
    assert context in user_prompt
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert jsonata_mapping in user_prompt
    assert "Here is additional context information that may help:" not in user_prompt


def test_create_mapping_retry_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    prompts: List[str],
    jsonata_mapping: str,
    error_message: str,
):
    """Test create_mapping_retry_prompt constructs prompts correctly."""
    system_prompt, user_prompt = create_mapping_retry_prompt(
        input_json_schema, output_json_schema, jsonata_mapping, prompts, error_message
    )

    assert system_prompt == (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Your task is to generate precise JSONata expressions that transform an input JSON schema into a fixed output JSON schema. "
        "You are not allowed to define your own JSONata functions, use function chaining or regular expressions. "
        "Return only the raw JSONata expression as text your response, without any explanations or formatting."
    )
    assert (
        "You previously wrote a JSONata expression that maps a JSON that follows the JSON input schema restrictions"
        in user_prompt
    )
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert jsonata_mapping in user_prompt
    assert error_message in user_prompt
    assert prompts[0] in user_prompt
    assert "Here is additional context information that may help:" in user_prompt


def test_create_mapping_retry_prompt_no_prompts(
    input_json_schema: Schema,
    output_json_schema: Schema,
    jsonata_mapping: str,
    error_message: str,
):
    """Test create_mapping_retry_prompt with empty prompts."""
    system_prompt, user_prompt = create_mapping_retry_prompt(
        input_json_schema, output_json_schema, jsonata_mapping, [], error_message
    )

    assert system_prompt == (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Your task is to generate precise JSONata expressions that transform an input JSON schema into a fixed output JSON schema. "
        "You are not allowed to define your own JSONata functions, use function chaining or regular expressions. "
        "Return only the raw JSONata expression as text your response, without any explanations or formatting."
    )
    assert (
        "You previously wrote a JSONata expression that maps a JSON that follows the JSON input schema restrictions"
        in user_prompt
    )
    assert str(input_json_schema) in user_prompt
    assert str(output_json_schema) in user_prompt
    assert jsonata_mapping in user_prompt
    assert error_message in user_prompt
    assert "Here is additional context information that may help:" not in user_prompt
