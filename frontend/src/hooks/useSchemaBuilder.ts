import { JSONSchema } from '@/types/Schema';
import { SchemaBuilder, SchemaBuilderActions } from '@/utils/schema/jsonSchemaBuilder';
import { useRef, useState, useCallback, useEffect } from 'react';
import { useImmer } from 'use-immer';

type DirtySchemaTuple = [JSONSchema, boolean];
type ExtendedActions = SchemaBuilderActions & { reset: (schema?: JSONSchema) => void };

/**
 * React hook for building and mutating a JSON-Schema.
 *
 * @param initial Optional initial schema.
 * @returns {[[schema, isDirty], actions]}
 */
export function useSchemaBuilder(initial?: JSONSchema | null): [DirtySchemaTuple, ExtendedActions] {
    const [schema, setSchema] = useImmer<JSONSchema>(initial ?? {});
    const [isDirty, setIsDirty] = useState(false);
    const builder = useRef(new SchemaBuilder(schema));

    const update = useCallback(
        (op: (b: SchemaBuilder) => void, markDirty = true) => {
            return setSchema((draft) => {
                if (markDirty) setIsDirty(true);
                builder.current.setSchema(draft);
                op(builder.current);
                return builder.current.getSchema();
            });
        },
        [setSchema],
    );

    const reset = useCallback(
        (schema?: JSONSchema | null) => {
            setIsDirty(false);
            setSchema(() => {
                return builder.current.setSchema(schema ?? initial ?? {}).getSchema();
            });
        },
        [setSchema, initial],
    );

    // Reset the builder when the initial schema changes
    // This is important to ensure that the builder is always in sync with the schema
    useEffect(() => reset(initial), [initial, reset]);

    const actions: ExtendedActions = {
        setSchema: (next) => update((b) => b.setSchema(next)),
        addProperty: (path, def, after) => update((b) => b.addProperty(path, def, after)),
        updateProperty: (prop, next) => update((b) => b.updateProperty(prop, next)),
        removeProperty: (path) => update((b) => b.removeProperty(path)),
        reset,
    };

    return [[schema, isDirty], actions];
}
