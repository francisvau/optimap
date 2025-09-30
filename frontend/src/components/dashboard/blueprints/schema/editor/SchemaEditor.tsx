import { FocusEvent, FormEvent, JSX, useId, useMemo, useRef, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    getOrderedSchemaProperties,
    getPathString,
    isExpandableType,
    jsonTypeNames,
} from '@/utils/schema/schemaUtils';
import { TypeTooltip } from '@/components/dashboard/blueprints/schema/editor/TypeTooltip';
import {
    faEdit,
    faCaretRight,
    faCaretDown,
    faTrash,
    faPlusCircle,
} from '@fortawesome/free-solid-svg-icons';
import { SchemaBuilderActions } from '@/utils/schema/jsonSchemaBuilder';
import { Tooltip } from 'primereact/tooltip';
import { TypeConstraint } from '@/components/dashboard/blueprints/schema/editor/TypeConstraint';
import { Dropdown, DropdownChangeEvent } from 'primereact/dropdown';
import { JSONSchema, SchemaPathSegments, SchemaPathString, SchemaProperty } from '@/types/Schema';
import { Button } from 'primereact/button';
import { ConstraintEditorDialog } from '@/components/dashboard/blueprints/schema/editor/ConstraintEditorDialog';
import { clsx } from 'clsx';
import { SchemaSelectorActions } from '@/utils/schema/jsonSchemaSelector';
import { Transition } from 'react-transition-group';

import React from 'react';
import './SchemaEditor.scss';

export type AddSchemaPropertyProps = {
    parent: SchemaPathSegments;
    after?: SchemaPathSegments;
    builder?: SchemaBuilderActions;
    verbose?: boolean;
    onSchemaUpdate?: (schema: JSONSchema) => unknown;
};

/**
 * A functional component that renders a button-like UI element for adding a schema property.
 *
 * @param {AddSchemaPropertyProps} props - The props for the component.
 *
 * @returns {JSX.Element} The rendered component.
 */
function AddSchemaProperty({
    parent,
    after,
    builder,
    verbose = false,
}: AddSchemaPropertyProps): JSX.Element {
    const [newProperty, setNewProperty] = useState<Partial<SchemaProperty> | null>(null);

    const handleAddClick = (e: React.MouseEvent) => {
        e.stopPropagation();

        if (newProperty !== null) {
            handleSaveClick(e);
        }

        setNewProperty({
            key: 'newProperty' + Math.floor(Math.random() * 1000),
            schema: {
                type: 'string',
            },
        });
    };

    const handleSaveClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        const newKey = [...parent, newProperty.key?.trim()];
        builder.addProperty(newKey, newProperty.schema, after);
        setNewProperty(null);
    };

    const handleChangeKey = (e: FormEvent<HTMLSpanElement>) => {
        const newName = e.currentTarget.innerText.trim();

        if (newName) {
            newProperty.key = newName;
        }
    };

    const handleKeyEnter = (e: React.KeyboardEvent<HTMLSpanElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            e.currentTarget.blur();
        }
    };

    const handleChangeType = (e: DropdownChangeEvent) => {
        setNewProperty((prev) => ({
            ...prev,
            schema: {
                ...prev.schema,
                type: e.value,
            },
        }));
    };

    const handleCancelClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        setNewProperty(null);
    };

    return (
        <>
            <div className={clsx('schema-field-add', { verbose })}>
                <div className="schema-field-add-content" onClick={handleAddClick}>
                    <FontAwesomeIcon icon={faPlusCircle} />
                </div>
            </div>

            {newProperty !== null && (
                <div className={clsx('schema-field', 'add')}>
                    <div className="flex align-items-center gap-2">
                        <Dropdown
                            className="dropdown-compact p-0 bg-transparent"
                            pt={{ panel: { className: 'dropdown-compact' } }}
                            options={jsonTypeNames}
                            value={newProperty.schema.type}
                            onChange={handleChangeType}
                            itemTemplate={(type) => <TypeTooltip type={type} />}
                            valueTemplate={(type) => <TypeTooltip type={type} />}
                        />
                        <span
                            className="schema-field-name"
                            contentEditable={true}
                            suppressContentEditableWarning={true}
                            onInput={handleChangeKey}
                            onKeyDown={handleKeyEnter}
                        >
                            {newProperty.key}
                        </span>
                        <Button
                            label="Save"
                            className="text-xs p-0"
                            onClick={handleSaveClick}
                            link
                        />
                        <Button
                            label="Cancel"
                            severity="danger"
                            className="text-xs p-0 text-red"
                            onClick={handleCancelClick}
                            link
                        />
                    </div>
                </div>
            )}
        </>
    );
}

export type MappingSchemaProps = {
    property: SchemaProperty;
    selected?: SchemaPathString[];
    builder?: SchemaBuilderActions;
    selector?: SchemaSelectorActions;
    isRoot?: boolean;
    onConstraintClick?: (property: SchemaProperty) => unknown;
};

/**
 * A React component that renders a field within a mapping schema.
 *
 * @param {MappingSchemaFieldProps} props - The props for the component.
 *
 * @returns {JSX.Element} The rendered schema field component.
 */
const SchemaField = React.memo(
    function SchemaField({
        property,
        builder,
        selector,
        selected = [],
        isRoot,
        onConstraintClick,
    }: MappingSchemaProps): JSX.Element {
        // Aliases
        const { path, schema, key } = property;

        // Template refs
        const nameRef = useRef<HTMLSpanElement>(null);
        const nestRef = useRef<HTMLDivElement>(null);

        // State
        const id = useId();
        const [isExpanded, setIsExpanded] = useState(
            isRoot || Object.keys(schema.properties ?? schema.items ?? {}).length < 5,
        );

        const isExpandable = useMemo(() => isExpandableType(schema), [schema]);

        const isSelected = useMemo(
            () => isExpandable && selected.includes(getPathString(property.path)),
            [isExpandable, selected, property.path],
        );

        // const isDisabled = useMemo(
        //     () => isExpandable && !!selector?.hasSelectedBefore(property.path),
        //     [selector, isExpandable, property.path],
        // );

        const handleToggleExpand = (e: React.MouseEvent) => {
            e.stopPropagation();
            setIsExpanded((prev) => !prev);
        };

        const handleChangeKey = (e: FocusEvent<HTMLSpanElement>) => {
            const newKey = e.currentTarget.innerText.trim();
            if (key === newKey) return;
            builder.updateProperty(property, { key: newKey });
        };

        const handleKeyEnter = (e: React.KeyboardEvent<HTMLSpanElement>) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.currentTarget.blur();
            }
        };

        const handleChangeType = (e: DropdownChangeEvent) => {
            builder.updateProperty?.(property, {
                schema: { type: e.value },
            });
        };

        const handleSelectionUpdate = (e: React.MouseEvent) => {
            if (selector && isExpandable) {
                e.stopPropagation();
                selector?.toggle(property.path);
            }
        };

        const handleDoubleClickSelectionUpdate = (e: React.MouseEvent) => {
            if (selector && isExpandable) {
                e.stopPropagation();
                selector?.clear();
                selector?.select(property.path);
            }
        };

        const handleDeleteClick = (e: React.MouseEvent) => {
            e.stopPropagation();
            builder.removeProperty(property.path);
        };

        const handleEditClick = (e: React.MouseEvent) => {
            e.stopPropagation();
            onConstraintClick?.(property);
        };

        return (
            <div
                onClick={handleSelectionUpdate}
                onDoubleClick={handleDoubleClickSelectionUpdate}
                className={clsx('schema-field-wrapper', {
                    expandable: isExpandable,
                    selectable: !!selector,
                    selected: isSelected,
                    // disabled: isDisabled,
                })}
            >
                <div className="schema-field">
                    <div className="flex align-items-center gap-2">
                        {builder ? (
                            <Dropdown
                                className="dropdown-compact p-0 bg-transparent"
                                pt={{ panel: { className: 'dropdown-compact' } }}
                                options={jsonTypeNames}
                                value={schema.type}
                                onChange={handleChangeType}
                                itemTemplate={(type) => <TypeTooltip type={type} />}
                                valueTemplate={(type) => <TypeTooltip type={type} />}
                            />
                        ) : (
                            <TypeTooltip type={schema.type} />
                        )}

                        {!!builder && !isRoot && (
                            <Tooltip target={`#${id}-name`} content="Edit key" position="top" />
                        )}

                        <span
                            className="schema-field-name"
                            contentEditable={!!builder}
                            suppressContentEditableWarning={true}
                            ref={nameRef}
                            onBlur={handleChangeKey}
                            onKeyDown={handleKeyEnter}
                            id={`${id}-name`}
                        >
                            {key}
                        </span>

                        {isExpandable && (
                            <FontAwesomeIcon
                                onClick={handleToggleExpand}
                                icon={isExpanded ? faCaretDown : faCaretRight}
                                className="schema-field-expander"
                            />
                        )}
                    </div>

                    <div className="schema-field-meta">
                        <TypeConstraint value={schema} />
                        {!!builder && !isRoot && (
                            <div className="flex gap-2">
                                <Tooltip
                                    target={`#${id}-edit-icon`}
                                    content="Edit constraints"
                                    position="top"
                                />
                                <FontAwesomeIcon
                                    id={`${id}-edit-icon`}
                                    icon={faEdit}
                                    className="schema-field-meta-action"
                                    onClick={handleEditClick}
                                />
                                <Tooltip
                                    target={`#${id}-delete-icon`}
                                    content="Delete property"
                                    position="top"
                                />
                                <FontAwesomeIcon
                                    id={`${id}-delete-icon`}
                                    icon={faTrash}
                                    className={clsx('schema-field-meta-delete')}
                                    onClick={handleDeleteClick}
                                />
                            </div>
                        )}
                    </div>
                </div>

                {isExpandable && (
                    <Transition
                        in={isExpanded}
                        timeout={0}
                        mountOnEnter
                        unmountOnExit
                        nodeRef={nestRef}
                    >
                        <div className="schema-field-nest" ref={nestRef}>
                            <span className="schema-field-nest-separator" />
                            <Schema
                                property={property}
                                builder={builder}
                                selector={selector}
                                selected={selected}
                                onConstraintClick={onConstraintClick}
                            />
                        </div>
                    </Transition>
                )}

                {builder && !isRoot && (
                    <AddSchemaProperty builder={builder} parent={path.slice(0, -1)} after={path} />
                )}
            </div>
        );
    },
    (prevProps, nextProps) => {
        return (
            prevProps.property.schema === nextProps.property.schema &&
            (!prevProps.selector || prevProps.selected === nextProps.selected)
        );
    },
);

/**
 * A React component that renders a complete JSON schema structure
 *
 * @param {MappingSchemaProps} props - Component props
 *
 * @returns JSX element representing the schema hierarchy
 */
const Schema = React.memo(
    function Schema({
        property,
        builder,
        selector,
        selected = [],
        onConstraintClick,
    }: MappingSchemaProps): JSX.Element {
        // Destructure the property object
        const { schema, path } = property;

        // This is used to determine the order of properties in the schema
        // and to map keys to their corresponding values
        const properties = useMemo(() => getOrderedSchemaProperties(schema, path), [schema, path]);

        return (
            <div className={clsx('schema-object', { editable: !!builder })}>
                {properties.length === 0 ? (
                    <AddSchemaProperty parent={path} builder={builder} verbose />
                ) : (
                    properties.map((property: SchemaProperty) => (
                        <SchemaField
                            key={property.key}
                            property={property}
                            builder={builder}
                            selector={selector}
                            selected={selected}
                            onConstraintClick={onConstraintClick}
                        />
                    ))
                )}
            </div>
        );
    },
    (prevProps, nextProps) => {
        return (
            prevProps.property.schema === nextProps.property.schema &&
            (!prevProps.selector || prevProps.selected === nextProps.selected)
        );
    },
);

export type SchemaEditorProps = {
    schema: JSONSchema;
    selected?: SchemaPathString[];
    builder?: SchemaBuilderActions;
    selector?: SchemaSelectorActions;
    target?: string;
};

/**
 * A React component for editing a schema. This component allows users to view
 * and optionally edit the provided schema based on the `isEditable` flag.
 *
 * @param {SchemaEditorProps} props - The props for the SchemaEditor component.
 *
 * @returns {JSX.Element} The rendered SchemaEditor component.
 */
export function SchemaEditor({
    schema,
    selected = [],
    builder,
    selector,
    target = '',
}: SchemaEditorProps): JSX.Element {
    const [showDialog, setShowDialog] = useState(false);
    const [selectedProperty, setSelectedProperty] = useState<SchemaProperty | undefined>();

    // Memoized values
    const property = useMemo(() => ({ key: target, path: [], schema }), [target, schema]);

    const handleShowConstraints = (property: SchemaProperty) => {
        setSelectedProperty(property);
        setShowDialog(true);
    };

    const handleHideConstraints = () => {
        setShowDialog(false);
        setSelectedProperty(undefined);
    };

    return (
        <>
            {selectedProperty && (
                <ConstraintEditorDialog
                    property={selectedProperty}
                    builder={builder}
                    show={showDialog}
                    onHide={handleHideConstraints}
                />
            )}
            <SchemaField
                property={property}
                builder={builder}
                selector={selector}
                selected={selected}
                onConstraintClick={handleShowConstraints}
                isRoot
            />
        </>
    );
}
