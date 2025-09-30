import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { JSONSchema, SchemaPathString, SubSchemaSelection } from '@/types/Schema';
import { SchemaSelector, SchemaSelectorActions } from '@/utils/schema/jsonSchemaSelector';
import { useCallback, useRef, useState } from 'react';

type DirtySelectionTuple = [SchemaPathString[], boolean];

/**
 * React hook for interactively selecting subschemas within a JSON schema.
 *
 * @param target      The target JSON schema to select from.
 * @param selections  Previously committed selections (immutable).
 * @param initial     Initial selection for this session.
 *
 * @returns [[selection, isDirty], actions]
 */
export function useSchemaSelector(
    target: JSONSchema,
    selections: SubSchemaSelection[] = [],
    initial?: SubSchemaSelection,
): [DirtySelectionTuple, SchemaSelectorActions] {
    // Mutable selector instance
    const selector = useRef<SchemaSelector>(new SchemaSelector(target, selections, initial));
    const toast = useToast();

    // Local state for current selection and dirty flag
    const [selection, setSelection] = useState(selector.current.sessionPaths);
    const [isDirty, setIsDirty] = useState(false);

    // Helper to perform an action, mark dirty, and update selection
    const update = useCallback(
        (fn: () => void) => {
            try {
                fn();
                setSelection([...selector.current.sessionPaths]);
                setIsDirty(true);
            } catch (e) {
                toast({ severity: 'error', summary: 'Error', detail: e.message });
            }
        },
        [toast],
    );

    // Public actions
    const actions: SchemaSelectorActions = {
        select: (path) => update(() => selector.current.select(path)),
        selectAll: () => update(() => selector.current.selectAll()),
        deselect: (path) => update(() => selector.current.deselect(path)),
        toggle: (path) => update(() => selector.current.toggle(path)),
        clear: () => update(() => selector.current.clear()),
        getSelection: () => selector.current.getSelection(),
    };

    return [[selection, isDirty], actions];
}
