import { SchemaPath, SchemaPathString, SchemaProperty } from '@/types/Schema';
import { JSONSchema } from '@/types/Schema';
import { getPathSegments, getSchemaContainer, getSchemaProperty } from '@/utils/schema/schemaUtils';

export interface SchemaBuilderActions {
    setSchema: (schema: JSONSchema) => void;
    addProperty: (path: SchemaPath, definition: JSONSchema, after?: SchemaPath) => void;
    updateProperty(property: SchemaProperty, newProperty: Partial<SchemaProperty>): void;
    removeProperty(path: SchemaPath): void;
}

/**
 * A builder for ISO‑compliant, single‑type JSON Schemas with support for nested objects
 * and homogeneous arrays.
 */
export class SchemaBuilder implements SchemaBuilderActions {
    /**
     * Constructs a new instance of the JSON schema builder.
     *
     * @param schema -  An optional existing schema to initialise the builder with.
     * @param rootType - The root type of the schema (defaults to `'object'`).
     */
    constructor(private schema: JSONSchema) {}

    /**
     * Sets the JSON schema to be used by the builder.
     *
     * @param schema - The JSON schema to set.
     * @returns The current instance of the class for method chaining.
     */
    public setSchema(schema: JSONSchema): this {
        this.schema = schema;
        return this;
    }

    /**
     * Retrieves the current JSON schema.
     *
     * @returns The JSON schema as a `JSONSchema` object.
     */
    public getSchema(): JSONSchema {
        return this.schema;
    }

    /**
     * Checks if a schema property exists at the specified path.
     *
     * @param path - The path to the schema property to check.
     * @returns `true` if the schema property exists, otherwise `false`.
     */
    public hasSchemaProperty(path: SchemaPath): boolean {
        return !!getSchemaProperty(this.schema, path);
    }

    /**
     * Adds a property to a JSON schema at the specified path.
     *
     * @param path - The path within the schema where the property should be added.
     * @param definition - The JSON schema definition for the property being added.
     * @param required - Whether the property should be marked as required. Defaults to `false`.
     * @param after - An optional path indicating the property after which the new property should be inserted
     *                in the `required` array, if applicable.
     * @returns The current instance for method chaining.
     */
    public addProperty(path: SchemaPath, definition: JSONSchema, after?: SchemaPath): this {
        const segs = getPathSegments(path);
        const key = segs.pop()!;
        const parent = getSchemaContainer(this.schema, segs);

        parent.properties ||= {};
        parent.properties[key] = definition;

        // For arrays, ensure the items schema is defined
        if (definition.type === 'array') {
            parent.properties[key]['items'] ||= { type: 'object', properties: {}, required: [] };
        }

        // Handle implicit `required` ordering
        // Insert after the specified key if it exists
        const afterKey = after ? getPathSegments(after).pop() : undefined;
        parent.required ||= [];
        parent.required = parent.required.filter((r) => r !== key);

        if (!afterKey) {
            parent.required.push(key);
        } else {
            const idx = parent.required.indexOf(afterKey);

            if (idx === -1) {
                parent.required.push(key);
            } else {
                parent.required.splice(idx + 1, 0, key);
            }
        }

        return this;
    }

    /**
     * Updates a property in the JSON schema at the specified path.
     *
     * @param property - The schema property to be updated, represented as a `SchemaProperty`.
     * @param newProperty - The new property definition to be applied.
     *
     * @param property.path - The path to the property to be updated.
     * @param newProperty.key - The new key for the property.
     * @param newProperty.schema - The new schema definition for the property.
     *
     * @returns The current instance of the class for method chaining.
     *
     * @throws {Error} If the property to be updated does not exist at the specified path.
     */
    public updateProperty(
        { path }: SchemaProperty,
        { key: newKey, schema: patch = {} }: Partial<SchemaProperty>,
    ): this {
        const segs = getPathSegments(path);
        const oldKey = segs.pop() ?? ''; // '' = root
        const parent = getSchemaContainer(this.schema, segs, false); // .items or .properties
        const container = getSchemaContainer(parent); // ensures .properties

        if (oldKey && !container.properties?.[oldKey]) {
            throw new Error(`Property '${oldKey}' does not exist at '${segs.join('.') || 'root'}'`);
        }

        const key = newKey ?? oldKey;

        // possibly rename the property
        if (oldKey && newKey && newKey !== oldKey) {
            container.properties![key] = container.properties![oldKey];
            delete container.properties![oldKey];

            // keep required[] in the same slot
            const req = container.required ?? [];
            const idx = req.indexOf(oldKey);
            if (idx > -1) req.splice(idx, 1, key);
        }

        // merge the schema path
        const target = oldKey ? container.properties![key] : parent;
        const prevType = target.type;
        Object.assign(target, patch);

        // keep subschema alive if the container type changes
        // between object and array
        if ('type' in patch && patch.type !== prevType) {
            if (patch.type === 'object') {
                // re-use `items` from array properties
                const items = target.items;
                target.properties = items?.properties ?? {};
                target.required = items?.required ?? target.required ?? [];
                delete target.items;
            }

            if (patch.type === 'array') {
                // re-use `properties` from object properties
                target.items = {
                    type: 'object',
                    properties: target.properties ?? {},
                    required: target.required ?? [],
                };
                delete target.properties;
                delete target.required;
            }
        }

        return this;
    }

    /**
     * Renames a property in the schema by replacing the old key with a new key.
     *
     * @param oldKey - The current key of the property to be renamed.
     * @param newKey - The new key to replace the old key.
     * @returns The current instance of the class for method chaining.
     */
    public renameProperty(oldKey: SchemaPathString, newKey: SchemaPathString): this {
        this.updateProperty(getSchemaProperty(this.schema, oldKey), {
            key: newKey,
        });
        return this;
    }

    /**
     * Removes a property from the JSON schema at the specified path.
     *
     * @param path - The path to the property to be removed, represented as a `SchemaPath`.
     *               This path is used to locate the property within the schema.
     *
     * @returns The current instance of the class (`this`) to allow method chaining.
     *
     * @remarks
     * - If the property exists in the `properties` object of its parent, it will be deleted.
     * - If the property is listed in the `required` array of its parent, it will be removed from the array.
     */
    public removeProperty(path: SchemaPath): this {
        const segs = getPathSegments(path);
        const key = segs.pop()!;
        const parent = getSchemaContainer(this.schema, segs);

        if (parent.properties) {
            delete parent.properties[key];
        }

        if (parent.required) {
            parent.required = parent.required.filter((r) => r !== key);
        }

        return this;
    }

    // /**
    //  * Validates the constraints of the JSON schema and returns a list of error messages.
    //  *
    //  * @returns {string[]} An array of error messages describing the validation issues.
    //  */
    // public validateConstraints(): string[] {
    //     const errors = [];

    //     const walk = (node: JSONSchema, path: string[]) => {
    //         // Union types are not allowed
    //         if (Array.isArray(node.type)) {
    //             errors.push(
    //                 `Multiple types [${node.type.join(', ')}] not allowed at '${path.join('.')}'`,
    //             );
    //         }

    //         // Arrays must define one schema in `items`
    //         if (node.type === 'array') {
    //             if (!node.items) {
    //                 errors.push(
    //                     `Array at '${path.join('.')}' must have a single schema in 'items'`,
    //                 );
    //             } else {
    //                 walk(node.items, [...path, '[]']);
    //             }
    //         }

    //         // Dive into object properties
    //         if (node.properties) {
    //             for (const [key, child] of Object.entries(node.properties)) {
    //                 if (child) {
    //                     walk(child, [...path, key]);
    //                 }
    //             }
    //         }
    //     };

    //     walk(this.schema, []);

    //     return errors;
    // }
}
