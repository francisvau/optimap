from typing import Any, Union

from app.schema import BaseSchema

Schema = dict[str, Any]


class ApplyJSONAtaRequest(BaseSchema):
    input_jsons: list[
        Union[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]
    ]
    input_definition_id: int
    blueprint_id: int
    job_id: int


class OutputItem(BaseSchema):
    output: Schema


class ApplyJSONAtaResponse(BaseSchema):
    results: Union[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]


class ExtractSchemaResponse(BaseSchema):
    json_schema: Schema
