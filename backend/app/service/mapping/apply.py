from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Sequence
from typing import Any, Literal, Mapping, cast

import jsonata  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.blueprint import InputDefinition, MappingBlueprint, OutputDefinition
from app.service.mapping.blueprint import MappingBlueprintService
from app.service.mapping.schema import SchemaValidator

JsonStruct = Literal["single", "list", "dict_of_objects"]


class MappingApplyService:
    """Stream-apply all mappings configured on one *InputDefinition*."""

    def __init__(
        self,
        db: AsyncSession,
        bp_svc: MappingBlueprintService,
    ) -> None:
        self.db = db
        self.bp_svc = bp_svc

    async def apply_stream(
        self,
        *,
        blueprint_id: int,
        input_definition_id: int,
        input_jsons: Sequence[Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Yield per-item results (`success` / `failed`)."""

        # Query the InputDefinition with blueprint and its output definition eagerly loaded
        input_result = await self.db.execute(
            select(InputDefinition)
            .options(
                selectinload(InputDefinition.blueprint).selectinload(
                    MappingBlueprint.output_definition
                )
            )
            .filter(InputDefinition.id == input_definition_id)
        )
        inp = input_result.scalars().first()

        if inp is None or inp.blueprint_id != blueprint_id:
            raise ValueError("input definition not found for this blueprint")

        if not inp.blueprint or not inp.blueprint.output_definition:
            raise ValueError("blueprint has no output definition")

        # Fetch the output definition
        output_result = await self.db.execute(
            select(OutputDefinition)
            .options(selectinload(OutputDefinition.blueprint))
            .filter(OutputDefinition.id == inp.blueprint.output_definition.id)
        )
        out_def = output_result.scalars().first()

        if out_def is None:
            raise ValueError("output definition not found")

        mapping_cache: dict[int, dict[str, str]] = {}

        for idx, raw in enumerate(input_jsons):
            yield await self._apply_one(
                idx, raw, inp, out_def.json_schema, mapping_cache
            )

    async def _apply_one(
        self,
        idx: int,
        raw: Any,
        inp: InputDefinition,
        schema: Mapping[str, Any],
        cache: dict[int, dict[str, str]],
    ) -> dict[str, Any]:
        """Apply all mappings to one input item."""
        res = {"index": idx, "status": "success", "result": None, "error": None}

        try:
            validator = SchemaValidator(instance=raw, schema=schema)
            validator.validate()

            per_mapping_out: list[Any] = []
            for mapping in inp.source_mappings:
                mapping_body = cache.get(int(mapping.id)) or await self._fetch_mapping(
                    mapping.id, cache
                )
                per_mapping_out.append(self._transform(raw, mapping_body))

            res["result"] = per_mapping_out

        except Exception as exc:
            res.update(status="failed", error=str(exc))

        return res

    async def _fetch_mapping(
        self, mapping_id: int, cache: dict[int, dict[str, str]]
    ) -> dict[str, str]:
        body = (await self.bp_svc.read_source_mapping(mapping_id)).jsonata_mapping or ""
        mapping_dict = cast(dict[str, str], json.loads(body))
        cache[int(mapping_id)] = mapping_dict
        return mapping_dict

    @staticmethod
    def _transform(data: Any, mapping: dict[str, str]) -> Any:
        """Transform data using JSONata mapping."""
        match MappingApplyService._kind(data):
            case "list":
                return [MappingApplyService._transform_single(d, mapping) for d in data]
            case "dict_of_objects":
                return {
                    k: MappingApplyService._transform_single(v, mapping)
                    for k, v in data.items()
                }
            case "single":
                return MappingApplyService._transform_single(data, mapping)

    @staticmethod
    def _transform_single(
        src: dict[str, Any], mapping: dict[str, str]
    ) -> dict[str, Any]:
        """Transform a single JSON object using JSONata mapping."""
        return {
            out: jsonata.Jsonata(expr).evaluate(src) for out, expr in mapping.items()
        }

    @staticmethod
    def _kind(obj: Any) -> JsonStruct:
        """Determine the structure of the JSON object."""
        if isinstance(obj, list) and all(isinstance(i, dict) for i in obj):
            return "list"
        if isinstance(obj, dict):
            return (
                "dict_of_objects"
                if all(isinstance(v, dict) for v in obj.values())
                else "single"
            )

        raise ValueError("unsupported JSON structure")
