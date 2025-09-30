import {
    JSONSchema,
    JSONSchemaTypeName,
    SchemaPath,
    SchemaPathSegments,
    SchemaPathString,
    SchemaProperty,
} from '@/types/Schema';
import {
    fa5,
    faArrowRight,
    faArrowsTurnToDots,
    faBars,
    faCalendar,
    faClock,
    faCode,
    faCog,
    faDatabase,
    faEnvelope,
    faFingerprint,
    faFont,
    faGhost,
    faGlobe,
    faHashtag,
    faLink,
    faListOl,
    faLock,
    faNetworkWired,
    faPercent,
    faSquareBinary,
    faToggleOn,
    faUpRightFromSquare,
    IconDefinition,
} from '@fortawesome/free-solid-svg-icons';

import { FormatName, formatNames } from 'ajv-formats/dist/formats';

// List of all JSON Schema format names
export const stringFormats = formatNames;

// List of all JSON Schema format names
export const formatIcons: Record<FormatName, IconDefinition> = {
    email: faEnvelope,
    date: faCalendar,
    time: faClock,
    duration: faClock,
    uri: faLink,
    url: faLink,
    hostname: faGlobe,
    ipv4: faNetworkWired,
    ipv6: faNetworkWired,
    regex: faHashtag,
    uuid: faFingerprint,
    byte: faSquareBinary,
    int32: faListOl,
    int64: faListOl,
    float: faArrowsTurnToDots,
    double: faArrowsTurnToDots,
    password: faLock,
    binary: faDatabase,
    'json-pointer': faArrowRight,
    'json-pointer-uri-fragment': faArrowRight,
    'relative-json-pointer': faArrowRight,
    'uri-reference': faUpRightFromSquare,
    'uri-template': faCode,
    'date-time': faCalendar,
    'iso-time': faClock,
    'iso-date-time': faCalendar,
};

// List of all JSON Schema type names
export const jsonTypeNames: JSONSchemaTypeName[] = [
    'string',
    'number',
    'integer',
    'boolean',
    'object',
    'array',
    'null',
];

// List of all JSON Schema type names
export const jsonTypeIcons: Record<JSONSchemaTypeName, IconDefinition> = {
    string: faFont,
    number: faPercent,
    integer: fa5,
    boolean: faToggleOn,
    object: faCog,
    array: faBars,
    null: faGhost,
};

// List of all JSON Schema type constraints
export const typeConstraints: Record<JSONSchemaTypeName, string[]> = {
    string: ['minLength', 'maxLength', 'pattern', 'format'],
    number: ['multipleOf', 'maximum', 'minimum', 'exclusiveMaximum', 'exclusiveMinimum'],
    integer: ['multipleOf', 'maximum', 'minimum', 'exclusiveMaximum', 'exclusiveMinimum'],
    array: ['minItems', 'maxItems', 'uniqueItems', 'contains'],
    object: [],
    boolean: [],
    null: [],
};

/**
 * Checks if the given JSON schema is an array.
 *
 * @param schema - The JSON schema to check.
 * @returns A boolean indicating whether the schema is an array.
 */
export function isExpandableType(schema?: JSONSchema | null): boolean {
    return schema && (schema.type === 'array' || schema.type === 'object');
}

/**
 * Checks if the given JSON schema is empty.
 *
 * @param schema - The JSON schema to check.
 * @returns A boolean indicating whether the schema is empty.
 */
export function isEmptySchema(schema?: JSONSchema | null): boolean {
    if (!schema) return true;
    return (
        (schema.type === 'object' && Object.keys(schema.properties || {}).length === 0) ||
        (schema.type === 'array' && schema.items && isEmptySchema(schema.items))
    );
}

/**
 * Splits a schema path into its individual segments.
 *
 * @param path - The schema path to be split. It can either be an array of strings
 *               representing the path segments or a dot-separated string.
 * @returns An array of strings representing the individual segments of the schema path.
 */
export function getPathSegments(path: SchemaPath): SchemaPathSegments {
    return Array.isArray(path) ? [...path] : path.split('.').filter(Boolean);
}

/**
 * Converts a schema path into a string representation.
 *
 * If the provided path is an array, it joins the elements with a dot (`.`) to form a string.
 * If the path is already a string, it returns the path as is.
 *
 * @param path - The schema path, which can be either a string or an array of strings.
 * @returns The string representation of the schema path.
 */
export function getPathString(path: SchemaPath): SchemaPathString {
    return Array.isArray(path) ? path.join('.') : path;
}

/**
 * Traverses and ensures the existence of a nested structure within a JSON schema
 * based on the provided path segments. This method modifies the schema in place
 * to create any missing objects or arrays along the path.
 *
 * @param cursor - The starting JSON schema object to traverse.
 * @param path - The full path to the schema property, represented as a `SchemaPath`.
 * @param flattenArray - Whether to return the `items` schema of an array, instead of the array itself.
 *
 * @returns The final `JSONSchema` object at the end of the traversal path.
 *
 * @throws {Error} If the traversal encounters a non-object schema where an object
 * is expected.
 */
export function getSchemaContainer(
    cursor: JSONSchema,
    path: SchemaPath = '',
    flattenArray: boolean = true,
): JSONSchema {
    const segments = getPathSegments(path);

    for (const segment of segments) {
        // If we are on an array, always drop into its items schema
        if (cursor.type === 'array') {
            cursor.items ||= { type: 'object', properties: {}, required: [] };
            cursor = cursor.items;
        }

        if (cursor.type !== 'object') {
            throw new Error(
                `Expected object while traversing, but found '${cursor.type}' at segment '${segment}'`,
            );
        }

        // Make sure a properties map exists
        cursor.properties ||= {};

        // If property already exists and is *not* expandable → error
        const existing = cursor.properties[segment];

        if (!existing || !isExpandableType(existing)) {
            throw new Error(
                `Path '${segments.join('.')}' is invalid - '${segment}' is not expandable`,
            );
        }

        // Ensure the next segment exists and is an object
        cursor.properties[segment] ||= {
            type: 'object',
            properties: {},
            required: [],
        };

        // Create placeholder container if absent
        cursor.properties[segment] ||= { type: 'object', properties: {}, required: [] };
        cursor = cursor.properties[segment];
    }

    // Final descent: if we ended on an array, return its items schema
    if (cursor?.type === 'array') {
        cursor.items ||= { type: 'object', properties: {}, required: [] };

        if (flattenArray) {
            cursor = cursor.items;
        }
    }

    return cursor;
}

/**
 * Determines whether a given JSON schema has an array type ancestor
 * along the specified schema path.
 *
 * @param cursor - The current JSON schema node to evaluate.
 * @param path - The schema path to traverse, represented as a string.
 *                Defaults to an empty string if not provided.
 * @returns `true` if an ancestor with type 'array' is found along the path,
 *          otherwise `false`.
 */
export function hasArrayAncestor(cursor: JSONSchema, path: SchemaPath = ''): boolean {
    const segments = getPathSegments(path);

    for (const segment of segments) {
        if (!cursor) return false;

        if (cursor.type === 'array') {
            return true;
        }

        if (cursor.type !== 'object') {
            return false;
        }

        cursor = cursor.properties?.[segment];
    }

    return false;
}

/**
 * Retrieves a schema property from a JSON schema based on the provided path.
 *
 * @param cursor - The JSON schema object to search within.
 * @param path - The path to the desired schema property, represented as a `SchemaPath`.
 * @returns The schema property as a `SchemaProperty` object if found, or `undefined` if the property does not exist.
 *
 * The method resolves the path into segments, identifies the parent container,
 * and retrieves the property from the parent's `properties` object.
 */
export function getSchemaProperty(
    cursor: JSONSchema,
    path: SchemaPath = '',
): SchemaProperty | undefined {
    const segs = getPathSegments(path);
    const key = segs.pop()!;
    const parent = getSchemaContainer(cursor, segs);

    if (parent.properties?.[key]) {
        return { key, path: segs.concat(key), schema: structuredClone(parent.properties[key]) };
    }
}

/**
 * Retrieves the properties of a JSON schema in a specific order.
 *
 * The function first includes all required properties of the schema, followed by
 * the optional properties. The order of the required and optional properties is
 * preserved as defined in the schema.
 *
 * @param schema - The JSON schema object to extract and order properties from.
 * @param prefix - An optional prefix for the schema path, used to traverse nested schemas.
 *
 * @returns An array of `SchemaProperty` objects representing the ordered properties.
 */
export function getOrderedSchemaProperties(
    schema: JSONSchema,
    prefix: SchemaPath = '',
): SchemaProperty[] {
    const target = getSchemaContainer(schema);
    const required = target.required || [];
    const optional = Object.keys(target.properties || {}).filter((key) => !required.includes(key));

    return [...required, ...optional].map((key) => {
        return {
            key,
            path: [...getPathSegments(prefix), key],
            schema: target.properties?.[key],
        };
    });
}
