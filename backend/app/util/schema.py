from typing import Optional

from jsonschema import Draft7Validator, SchemaError

from app.schema.mapping.schema import Schema

JSON_SCHEMA_DRAFT7_URI = "http://json-schema.org/draft-07/schema#"

DEFAULT_JSON_SCHEMA = {
    "$schema": JSON_SCHEMA_DRAFT7_URI,
    "type": "object",
    "properties": {},
    "required": [],
}


def validate_draft7_schema(v: Optional[Schema]) -> Optional[Schema]:
    """Validate a JSON Schema against the Draft 7 specification."""
    if v is None:
        return v

    # Set the default schema version.
    v["$schema"] = JSON_SCHEMA_DRAFT7_URI

    if "type" in v:
        # Objects must have a "properties" key.
        if v["type"] == "object" and "properties" not in v:
            v["properties"] = {}

        # Arrays must have an "items" key.
        if v["type"] == "array":
            # Add the "items" key if it doesn't exist.
            if "items" not in v:
                v["items"] = {"type": "object", "properties": {}}

            # If "items" is a list, convert it to an object with "type" and "properties".
            if isinstance(v["items"], list):
                v["items"] = {"type": "object", "properties": {}}

    try:
        Draft7Validator.check_schema(v)
    except SchemaError as e:
        raise ValueError(f"Invalid JSON Schema: {e.message}") from e

    return v


def align_schema(
    draft_schema: Optional[Schema], target_schema: Optional[Schema]
) -> Optional[Schema]:
    """
    Align the input JSON schema to the output JSON schema.
    This is done by checking the type of the input and output schemas.
    If they are different, we adjust the input schema to match the output schema.
    """
    return draft_schema
    # if not draft_schema or not target_schema:
    #     return draft_schema

    # in_t = draft_schema.get("type")
    # out_t = target_schema.get("type")

    # if in_t != out_t:
    #     # Drive from the output: reshape input to match output type
    #     if out_t == "array":
    #         # wrap the entire input schema under an array
    #         draft_schema = {
    #             "type": "array",
    #             "items": draft_schema,
    #         }

    #     elif out_t == "object":
    #         # if output is object but input is array, unwrap input.items
    #         items = draft_schema.get("items") or {}

    #         # items might itself be an object schema with properties/required
    #         draft_schema = {
    #             "type": "object",
    #             "properties": items.get("properties", {}),
    #             "required": items.get("required", []),
    #         }

    # return draft_schema
