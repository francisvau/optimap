from typing import List, Tuple

from app.prompt_assets.jsonata_reference import JSONATA_REFERENCE
from app.schema.mapping import PreviousMapping, Schema


def create_mapping_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    prompts: List[str],
    previous_mappings: List[PreviousMapping] = [],
) -> Tuple[str, str]:
    """Creates prompt for generating a JSONata mapping."""
    system_prompt = (
        "You are an expert in automatic JSON-schema (version 7) mappings using JSONata V2.0.0. "
        "Your task is to generate a single, precise JSONata expression that transforms an input JSON "
        "(conforming to a given input JSON schema) into an output JSON (conforming to a given output JSON schema)."
    )

    user_prompt = ""

    # Inject JSONata reference
    user_prompt += (
        "\n\nJSONata Reference Guide (for your reference, do not include in your output). Use only this for generating the rules:\n"
        + JSONATA_REFERENCE
    )

    if previous_mappings:
        user_prompt += (
            "\n\nHere are some previous mappings that may help:\n"
            + "\n".join(
                [
                    f"Input JSON schema: {str(mapping.input_json_schema)}.\n"
                    f"Output JSON schema: {str(mapping.output_json_schema)}.\n"
                    f"JSONata expression: {mapping.jsonata_mapping}.\n\n"
                    for mapping in previous_mappings
                ]
            )
        )

    user_prompt += (
        "\n\nHere are some rules you must follow when generating the JSONata expression:\n"
        "- Use only built-in JSONata functions (always prefixed with `$`). \n"
        "- Do not define custom functions, use regular expressions, or chain functions unnecessarily.\n"
        "- Start each mapping from the current context using path operators.\n"
        "- For any array field `X`, always iterate with `X[]` and output via `[X[].{...}]`. Never use `X.{...}` or `X.*.{...}` for this.\n"
        "- Cast types explicitly with `$number()`, `$string()`, etc., and compute aggregates only on the `X[]` path with `$sum(X[].(...))`.\n"
        "- Begin mapping at the root using `$$.` for objects or `$$[].` for arrays. \n"
        "- Be careful with array path operations. \n"
        "    - There are precedence rules: $sum(items[].(qty * amt)) works (multiplying numbers), `$sum(items.qty * items.amt)` doesn't (because you would be multiplying arrays).\n"
        "    - `items[]`.$number(qty * amt) also works.\n"
        "- Return only the raw JSONata expression—no explanations or formatting. Omit metadata fields from the output."
    )

    if prompts:
        user_prompt += (
            "\n\nHere is additional context information that may help:\n"
            + "\n".join(prompts)
        )

    user_prompt += (
        "\n\nWrite a JSONata expression that maps an input JSON (conforming to the input schema) "
        "into an output JSON (conforming to the output schema).\n"
        f"Input JSON schema: {input_json_schema}\n"
        f"Output JSON schema: {output_json_schema}\n\n"
    )

    return system_prompt, user_prompt


def create_explanation_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    prompts: List[str],
    jsonata_mapping: str,
) -> tuple[str, str]:
    """Creates a prompt for generating an explanation for a JSONata mapping."""
    system_prompt = (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Given a JSONata expression that maps an input JSON schema to an output JSON schema, your task is to explain the mapping field by field. "
        "For each output field, clearly describe:\n"
        "- Where the data comes from in the input schema (input path).\n"
        "- What transformations, if any, are applied (e.g., renaming, formatting, calculations, conditions).\n"
        "The output should be in the following format:\n"
        "[output field]: [explanation]\n[output field]: [explanation]\n...\n"
        "Don't use any markdown formatting, just plain text."
    )

    user_prompt = (
        f"Explain how the following JSONata expression transforms the input JSON schema into the specified output JSON schema.\n\n"
        f"Input JSON schema: {input_json_schema}.\n"
        f"Output JSON schema: {output_json_schema}.\n"
        f"JSONata expression: {jsonata_mapping}."
    )

    if prompts:
        user_prompt += (
            "\n\nHere is additional context information that may help:\n"
            + "\n".join(prompts)
        )

    return system_prompt, user_prompt


def create_edit_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    jsonata_mapping: str,
    context: str,
    prompts: List[str],
) -> Tuple[str, str]:
    """Creates a prompt for generating an edited JSONata mapping."""
    system_prompt = (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Your task is to edit a JSONata expression that transforms an input JSON schema into a fixed output schema. "
        "You are not allowed to define your own JSONata functions, use function chaining or regular expressions. "
        "Try to keep the JSONata expression as simple as possible. "
        "Make sure the JSONata expression handles each field specifiied in the output JSON schema. "
        "Return only the JSONata expression in your response, without any explanations or formatting."
    )

    user_prompt = (
        f"Edit the following JSONata expression to better fit the specified context while ensuring it still maps the input JSON schema to the output JSON schema.\n\n"
        f"Context for editing: {context}.\n"
        f"Input JSON schema: {input_json_schema}.\n"
        f"Output JSON schema: {output_json_schema}.\n"
        f"Current JSONata expression: {jsonata_mapping}."
    )

    if prompts:
        user_prompt += (
            "\n\nHere is additional context information that may help:\n"
            + "\n".join(prompts)
        )

    return system_prompt, user_prompt


def create_mapping_retry_prompt(
    input_json_schema: Schema,
    output_json_schema: Schema,
    jsonata_mapping: str,
    prompts: List[str],
    error_message: str,
) -> Tuple[str, str]:
    """Creates prompt for generating a JSONata mapping."""
    system_propmt = (
        "You are an expert in automatic data schema mappings using JSONata. "
        "Your task is to generate precise JSONata expressions that transform an input JSON schema into a fixed output JSON schema. "
        "You are not allowed to define your own JSONata functions, use function chaining or regular expressions. "
        "Return only the raw JSONata expression as text your response, without any explanations or formatting."
    )

    user_prompt = (
        f"You previously wrote a JSONata expression that maps a JSON that follows the JSON input schema restrictions to another JSON that follows the JSON output schema restrictions. This contained an error and you need to fix this error.\n\n"
        f"Input JSON schema: {input_json_schema}.\n"
        f"Output JSON schema: {output_json_schema}.\n"
        f"JSONata expression: {jsonata_mapping}.\n"
        f"Error message: {error_message}.\n"
        f"Fix the JSONata expression to ensure it correctly maps the input JSON schema to the output JSON schema.\n"
        f"Make sure the JSONata expression handles each datafield specified in the output JSON schema, do not include the metadata fields. "
    )

    if prompts:
        user_prompt += (
            "\n\nHere is additional context information that may help:\n"
            + "\n".join(prompts)
        )

    return system_propmt, user_prompt
