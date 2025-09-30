from collections import defaultdict
from typing import Any, Dict, List, Mapping, Tuple, Union, cast

from genson import SchemaBuilder  # type: ignore
from jsonschema import validate

from app.exceptions import ValueError
from app.util.schema import JSON_SCHEMA_DRAFT7_URI

ARRAY_SENTINEL = "__array__"  # distinguishes “through an array” in a path
MAX_EXAMPLES = 3  # avoid blowing-up the schema with thousands of values


class EnhancedSchemaBuilder(SchemaBuilder):  # type: ignore
    """
    A SchemaBuilder that also adds examples to every atomic
    (non-object, non-array) property it encounters.
    """

    def __init__(self) -> None:
        super().__init__()
        self._examples: Dict[Tuple[str, ...], List[Any]] = defaultdict(list)

    def add_object(self, obj: Dict[str, Any]) -> None:
        """
        Feed an object to genson **and** harvest example values recursively.
        """
        super().add_object(obj)
        self._collect_examples(obj, ())

    def to_schema(self) -> Dict[str, Any]:
        """
        Generate a JSON-Schema that includes “examples”
        on every atomic leaf.
        """
        schema: Dict[str, Any] = cast(Dict[str, Any], super().to_schema())
        self._inject_examples(schema, ())
        return schema

    def _collect_examples(self, node: Any, path: Tuple[str, ...]) -> None:
        """
        Walk *node* (the original JSON data) and keep up to
        ``MAX_EXAMPLES`` distinct examples for every **atomic** property.
        """
        if isinstance(node, dict):
            for key, value in node.items():
                self._collect_examples(value, path + (key,))
        elif isinstance(node, list):
            for item in node:
                self._collect_examples(item, path + (ARRAY_SENTINEL,))
        else:  # atomic value: str, int, float, bool, null
            bucket = self._examples[path]
            if node not in bucket and len(bucket) < MAX_EXAMPLES:
                bucket.append(node)

    def _inject_examples(
        self, schema_fragment: Dict[str, Any], path: Tuple[str, ...]
    ) -> None:
        """
        Walk the generated schema and graft ``examples`` where appropriate.
        *Object* and *array* types are skipped by design.
        """
        typ = schema_fragment.get("type")

        if typ == "object":
            for prop, prop_schema in schema_fragment.get("properties", {}).items():
                self._inject_examples(prop_schema, path + (prop,))
        elif typ == "array":
            if "items" in schema_fragment:
                self._inject_examples(
                    schema_fragment["items"], path + (ARRAY_SENTINEL,)
                )
        else:  # non-container - place the examples here, if we have any
            examples = self._examples.get(path)
            if examples:
                schema_fragment["examples"] = examples


class JSONSchemaGenerator:
    def __init__(self) -> None:
        self.builder = EnhancedSchemaBuilder()

    def generate(
        self, data: Union[dict[str, Any], List[dict[str, Any]]]
    ) -> dict[str, Any]:
        """
        Generate JSON Schema from a JSON object or a list of JSON objects.
        """
        if isinstance(data, list):
            for obj in data:
                if not isinstance(obj, dict):
                    raise ValueError(
                        "All elements in the list must be JSON objects (dicts)."
                    )
                self.builder.add_object(obj)

        elif isinstance(data, dict):
            # just return the data itself if it already looks
            # like a JSON schema
            if data.get("$schema", None) is not None:
                return data

            self.builder.add_object(data)
        else:
            raise ValueError(
                "Input must be a JSON object (dict) or a list of JSON objects (list of dicts)."
            )

        base_schema = self.builder.to_schema()

        if isinstance(data, list):
            base_schema.pop("$schema", None)
            return {
                "type": "array",
                "$schema": JSON_SCHEMA_DRAFT7_URI,
                "items": base_schema,
            }

        return base_schema


class SchemaValidator:
    def __init__(self, instance: Any, schema: Mapping[str, Any]) -> None:
        self.instance = instance
        self.schema = schema

    def validate(self) -> None:
        validate(self.instance, self.schema)
