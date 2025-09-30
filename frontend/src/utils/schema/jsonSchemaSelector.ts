import { JSONSchema, SchemaPath, SchemaPathString, SubSchemaSelection } from '@/types/Schema';
import {
    getPathSegments,
    getPathString,
    getSchemaContainer,
    hasArrayAncestor,
    isEmptySchema,
    isExpandableType,
} from '@/utils/schema/schemaUtils';

export interface SchemaSelectorActions {
    select: (path: SchemaPath) => void;
    selectAll: () => void;
    deselect: (path: SchemaPath) => void;
    toggle: (path: SchemaPath) => void;
    clear: () => void;
    getSelection: () => SubSchemaSelection | undefined;
}

/**
 * SchemaSelector — builds a (sub)schema from interactive selections.
 *
 * • `basePrev`  – immutable selections from previous runs; used **only** for completeness check.
 * • `session`   – selections committed in *this* run.
 * • `current*`  – the pick most recently passed to `select()` and not yet committed.
 */
export class SchemaSelector implements SchemaSelectorActions {
    private target: JSONSchema;
    private targetPaths: SchemaPathString[] = [];

    public selectedPaths: SchemaPathString[] = [];
    public sessionPaths: SchemaPathString[] = [];

    /**
     * SchemaSelector constructor.
     *
     * @param target - The target JSON schema to be selected from.
     * @param selected - An array of previously selected subschemas.
     * @param initial - An optional initial selection to be used as a base for the session.
     */
    constructor(
        target: JSONSchema,
        selected: SubSchemaSelection[] = [],
        initial?: SubSchemaSelection | null,
    ) {
        this.target = structuredClone(target);
        this.targetPaths = this.getPaths(target);
        this.selectedPaths = selected.flatMap((s) => this.getPaths(s.jsonSchema, s.targetPath));

        if (!isEmptySchema(initial?.jsonSchema)) {
            this.sessionPaths = this.getPaths(initial.jsonSchema, initial.targetPath);
        }
    }

    /**
     * Select a schema path and return the corresponding JSON schema.
     * The selected schema is stored in the session and can be retrieved later.
     *
     * @param path - The path to the schema to be selected.
     */
    public select(path: SchemaPath): void {
        const string = getPathString(path);

        // Check if the path is valid.
        if (!this.targetPaths.includes(string)) {
            throw new Error(`Path ${path} does not exist in the target schema.`);
        }

        // Check if the path is already selected.
        if (this.selectedPaths.includes(string)) {
            throw new Error(`Path ${path} is already selected.`);
        }

        // Check if the path is descendant.
        const isDescendant = this.sessionPaths.some((parent) => string.startsWith(parent));
        const isCommonParent = this.sessionPaths.every((parent) => parent.startsWith(string));

        if (this.sessionPaths.length && !isDescendant && !isCommonParent) {
            throw new Error(
                `Subschema at ${path} is not a descendant of any of the selected subschemas.`,
            );
        }

        if (!this.sessionPaths.includes(string)) {
            this.sessionPaths.push(string);
        }
    }

    /**
     * Select all schema paths in the target schema.
     * This method is a convenience method that selects all paths at once.
     */
    public selectAll(): void {
        this.sessionPaths = this.targetPaths.filter((path) => !this.selectedPaths.includes(path));
    }

    /**
     * Deselect a schema path.
     * This method is currently a placeholder and does not perform any action.
     *
     * @param path - The path to the schema to be deselected.
     */
    public deselect(path: SchemaPath): void {
        const string = getPathString(path);

        if (!this.sessionPaths.includes(string)) {
            throw new Error(`Path ${path} is not selected.`);
        }

        const isCommonParent =
            this.sessionPaths.length > 2 &&
            this.sessionPaths.every((child) => child.startsWith(string));

        if (isCommonParent) {
            throw new Error(
                `${path ? 'Subschema at ' + path : 'The root'} is a common parent of other selected subschemas.`,
            );
        }

        this.sessionPaths = this.sessionPaths.filter((p) => p !== string);
    }

    /**
     * Toggle the selection state of a schema path.
     * If the path is already selected, it will be deselected; otherwise, it will be selected.
     *
     * @param path - The path to the schema to be toggled.
     */
    public toggle(path: SchemaPath): void {
        if (this.hasSelectedBefore(path)) return;

        if (!this.hasSelectedInSession(path)) {
            this.select(path);
        } else {
            this.deselect(path);
        }
    }

    /**
     * Clear the current selection process.
     */
    public clear(): void {
        this.sessionPaths = [];
    }

    /**
     * Get the current selection object.
     * This selection consists of a subschema of the target schema,
     * and an optional join condition.
     *
     * @returns The current selection.
     */
    public getSelection(): SubSchemaSelection | undefined {
        if (!this.sessionPaths.length) return;

        // determine base (shortest) path
        const sortedSessionPaths = [...this.sessionPaths].sort(
            (a, b) => getPathSegments(a).length - getPathSegments(b).length,
        );
        const basePath = sortedSessionPaths[0];
        const baseSegs = getPathSegments(basePath);

        // grab and prune the base node
        const baseNode = getSchemaContainer(this.target, baseSegs, false);
        const rootSchema = this.prune(baseNode);
        const selSchema = structuredClone(rootSchema);

        // process deeper selections
        for (const p of sortedSessionPaths.slice(1)) {
            const fullSegs = getPathSegments(p);
            const relSegs = fullSegs.slice(baseSegs.length);

            // get the selected node to insert
            const orig = getSchemaContainer(this.target, fullSegs, false);
            const picked = this.prune(orig);

            // walk to the insertion point
            let parent = selSchema;

            for (let i = 0; i < relSegs.length - 1; i++) {
                const seg = relSegs[i];
                if (parent.type === 'array') {
                    parent = parent.items as JSONSchema;
                }

                if (!parent.properties[seg] || !isExpandableType(parent.properties[seg]!)) {
                    parent.properties[seg] = { type: 'object', properties: {}, required: [] };
                }

                parent = parent.properties[seg]!;
            }

            // final segment
            const seg = relSegs[relSegs.length - 1];

            if (parent.type === 'array') {
                parent = parent.items;
            }

            parent.properties[seg] = picked;

            if (parent.required && !parent.required.includes(seg)) {
                parent.required.push(seg);
            }
        }

        // if a parent is an array, the selected node must be also an array
        if (hasArrayAncestor(this.target, basePath) && selSchema.type === 'object') {
            selSchema.type = 'array';
            selSchema.items = structuredClone(selSchema);
            delete selSchema['properties'];
        }

        // return selection

        return { jsonSchema: selSchema, targetPath: basePath };
    }

    /**
     * Checks if a given schema path has been selected in the current session.
     *
     * @param path - The schema path to check, represented as a `SchemaPath` object.
     * @returns `true` if the path is included in the session's selected paths, otherwise `false`.
     */
    public hasSelectedInSession(path: SchemaPath): boolean {
        const string = getPathString(path);
        return this.sessionPaths.includes(string);
    }

    /**
     * Checks if the given schema path is included in the list of selected paths.
     *
     * @param path - The schema path to check.
     * @returns `true` if the path is included in the selected paths, otherwise `false`.
     */
    public hasSelectedBefore(path: SchemaPath): boolean {
        const string = getPathString(path);
        return this.selectedPaths.includes(string);
    }

    /**
     * Check if the combination of current and previous selections
     * buil the target schema entirely.
     *
     * @returns Whether nothing is left to be selected from the target.
     */
    public isComplete(): boolean {
        return this.targetPaths.every((path: SchemaPathString) =>
            [...this.selectedPaths, ...this.sessionPaths].includes(path),
        );
    }

    /**
     * Prune a JSON schema by omitting its expandable child properties (array and obect types).
     *
     * @param schema - The JSON schema to prune expandable properties from.
     * @returns The pruned JSON schema, where each expandable property was omitted from its properties or items.
     */
    private prune(schema: JSONSchema): JSONSchema {
        const c = structuredClone(schema);

        if (c.type === 'object') {
            c.properties = Object.fromEntries(
                Object.entries(c.properties ?? {}).filter(
                    ([, v]) => !isExpandableType(v as JSONSchema),
                ),
            );

            if (c.required) {
                c.required = c.required.filter((k) => k in (c.properties ?? {}));
            }
        }

        if (c.type === 'array' && isExpandableType(c.items)) {
            c.items = this.prune(c.items);
        }

        return c;
    }

    /**
     * Recursively retrieves all possible paths within a JSON schema.
     *
     * @param schema - The JSON schema to extract paths from.
     * @param prefix - An optional array of schema path segments representing the current path prefix. Defaults to an empty array.
     * @returns An array of schema path segments, where each segment represents a path within the schema.
     *
     * The function handles schemas of type `array` and `object`:
     * - For `array` schemas, it recursively processes the `items` property.
     * - For `object` schemas, it iterates over the `properties` and recursively processes expandable types.
     */
    private getPaths(schema: JSONSchema, prefix?: SchemaPath): string[] {
        const prefixString = getPathString(prefix ?? '');
        const seen = new Set<string>();
        const result = [];

        const stack = [{ node: schema, path: prefixString }];

        while (stack.length) {
            const { node, path } = stack.pop()!;

            if (!seen.has(path)) {
                seen.add(path);
                result.push(path);
            }

            if (node && node.type === 'array') {
                stack.push({ node: node.items, path });
            }

            if (node && node.type === 'object') {
                for (const [key, value] of Object.entries(node.properties ?? {})) {
                    if (isExpandableType(value)) {
                        const nextPath = path ? `${path}.${key}` : key;
                        stack.push({ node: value, path: nextPath });
                    }
                }
            }
        }

        return result;
    }
}
