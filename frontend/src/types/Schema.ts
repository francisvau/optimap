import { JSONSchema7, JSONSchema7TypeName } from 'json-schema';

// A schema path is a string or an array of strings
export type SchemaPathString = string;
export type SchemaPathSegments = string[];
export type SchemaPath = SchemaPathString | SchemaPathSegments;

// A schema property is a path
// to a schema in the JSON Schema object.
export type SchemaProperty = {
    path: SchemaPathSegments;
    key: string;
    schema: JSONSchema;
};

// A JSON Schema type name
export type JSONSchemaTypeName = JSONSchema7TypeName;

// A more strict and useful version of JSONSchema.
// Doesn't allow for heterogeneous arrays or boolean schemas.
export type JSONSchema = Omit<
    JSONSchema7,
    'items' | 'properties' | 'type' | 'additionalItems' | '$defs' | 'definitions'
> & {
    /**
     * Homogeneous arrays only: must be a single schema, not a tuple
     */
    items?: JSONSchema;

    /**
     * No boolean schemas
     */
    properties?: Record<string, JSONSchema>;

    /**
     * Homogeneous types only: must be a single type, not an array of types
     */
    type?: JSONSchemaTypeName;

    /**
     * Homogeneous arrays only: must be an array of schemas
     */
    additionalItems?: JSONSchema;

    /**
     * JSON Schema 2020-12: $defs is a map of schema definitions
     */
    $defs?: Record<string, JSONSchema>;
    definitions?: Record<string, JSONSchema>;
};

/**
 * Type used to pass path and optional join condition when selecting multiple subschemas.
 */
export type SubSchemaSelection = {
    jsonSchema: JSONSchema | null;
    targetPath: SchemaPathString | null;
};
