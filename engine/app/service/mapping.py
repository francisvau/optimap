from typing import List

import jsonata  # type: ignore
from jsf import JSF  # type: ignore
from jsonschema import validate

from app.model.model import BaseModelType
from app.schema.mapping import JsonataGenerationResponse, PreviousMapping, Schema
from app.service.llm_api import get_model_output
from app.service.prompt_builder import (
    create_edit_prompt,
    create_explanation_prompt,
    create_mapping_prompt,
    create_mapping_retry_prompt,
)


class MappingError(Exception):
    """Custom exception for mapping errors."""

    pass


def validate_mapping(
    input_json_schema: Schema, output_json_schema: Schema, jsonata_mapping: str
) -> None:
    """Validates the JSONata mapping. Throws a MappingError if the mapping is invalid."""
    input_generator = JSF(input_json_schema, allow_none_optionals=0.0)
    example_input = input_generator.generate()

    try:
        expr = jsonata.Jsonata(jsonata_mapping)
    except Exception as e:
        raise MappingError(f"Error in JSONata expression:\n{e}")

    try:
        result = expr.evaluate(example_input)
    except Exception as e:
        raise MappingError(
            f"Error evaluating JSONata expression on JSON following the JSON input schema rules:\n{e}"
        )

    try:
        validate(instance=result, schema=output_json_schema)
    except Exception as e:
        raise MappingError(
            f"The JSON output does not conform to the JSON output schema. Here's the error:\n{e}"
        )


async def generate_mapping_from_schemas(
    input_json_schema: Schema,
    output_json_schema: Schema,
    base_model: BaseModelType,
    prompts: List[str],
    retries: int,
    previous_mappings: List[PreviousMapping] = [],
) -> JsonataGenerationResponse:
    """Generates a JSONata mapping."""
    system_prompt, user_prompt = create_mapping_prompt(
        input_json_schema, output_json_schema, prompts, previous_mappings
    )

    jsonata_mapping = await get_model_output(system_prompt, user_prompt, base_model)
    error_message, previous_error = "", ""
    retries_total = retries

    while retries > 0:
        try:
            validate_mapping(input_json_schema, output_json_schema, jsonata_mapping)
            error_message = ""
            break
        except MappingError as e:
            error_message = str(e)
            if error_message == previous_error:
                system_prompt, user_prompt = create_mapping_prompt(
                    input_json_schema, output_json_schema, prompts
                )
                jsonata_mapping = await get_model_output(
                    system_prompt, user_prompt, base_model
                )
            else:
                jsonata_mapping = await retry_generate_mapping(
                    input_json_schema,
                    output_json_schema,
                    jsonata_mapping,
                    base_model,
                    prompts,
                    error_message,
                )
            previous_error = error_message
            retries -= 1

    return JsonataGenerationResponse(
        mapping=jsonata_mapping,
        retries=retries_total - retries,
        corrupted=bool(error_message),
        error_message=error_message if error_message else None,
    )


async def retry_generate_mapping(
    input_json_schema: Schema,
    output_json_schema: Schema,
    jsonata_mapping: str,
    base_model: BaseModelType,
    prompts: List[str],
    error_message: str,
) -> str:
    """Retries generating a JSONata mapping if the first attempt fails."""
    system_prompt, user_prompt = create_mapping_retry_prompt(
        input_json_schema, output_json_schema, jsonata_mapping, prompts, error_message
    )
    jsonata_mapping = await get_model_output(system_prompt, user_prompt, base_model)
    return jsonata_mapping


async def generate_explanation(
    input_json_schema: Schema,
    output_json_schema: Schema,
    base_model: BaseModelType,
    prompts: List[str],
    jsonata_mapping: str,
) -> str:
    """Generates an explanation for a mapping created by AI."""
    system_prompt, user_prompt = create_explanation_prompt(
        input_json_schema, output_json_schema, prompts, jsonata_mapping
    )
    explanation = await get_model_output(system_prompt, user_prompt, base_model)
    return explanation


async def generate_edited_mapping(
    input_json_schema: Schema,
    output_json_schema: Schema,
    jsonata_mapping: str,
    context: str,
    base_model: BaseModelType,
    prompts: List[str],
) -> str:
    """Generates the edited JSONata mapping."""
    system_prompt, user_prompt = create_edit_prompt(
        input_json_schema, output_json_schema, jsonata_mapping, context, prompts
    )
    edit = await get_model_output(system_prompt, user_prompt, base_model)
    return edit
