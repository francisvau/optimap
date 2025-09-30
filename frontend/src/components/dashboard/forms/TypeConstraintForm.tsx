import {
    faBarsStaggered,
    faExpand,
    faFont,
    faTextWidth,
    IconDefinition,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { InputNumber, InputNumberChangeEvent } from 'primereact/inputnumber';
import { Tag } from 'primereact/tag';
import { Dropdown, DropdownChangeEvent } from 'primereact/dropdown';
import { JSX, useState } from 'react';
import { formatIcons, jsonTypeNames, stringFormats } from '@/utils/schema/schemaUtils';
import { Checkbox, CheckboxChangeEvent } from 'primereact/checkbox';
import { Chips, ChipsChangeEvent, ChipsPassThroughOptions } from 'primereact/chips';
import { TypeTooltip } from '@/components/dashboard/blueprints/schema/editor/TypeTooltip';

import './TypeConstraintForm.scss';
import { JSONSchema } from '@/types/Schema';

const inputPtOptions = {
    input: {
        root: { className: 'constraint-input' },
    },
};

const chipsPtOptions: ChipsPassThroughOptions = {
    container: {
        className: 'constraint-examples',
    },
    input: {
        className: 'text-xs m-0 p-0',
    },
    inputToken: {
        className: 'p-0 m-0',
    },
};

type BoundConstraintProps = {
    type: 'number' | 'string' | 'array';
    minValue?: number;
    maxValue?: number;
    valueTemplate?: string | JSX.Element;
    onEditConstraints: (newConstraints: JSONSchema) => void;
};

/**
 * A React functional component that represents a bound constraint UI element.
 * This component displays two input fields for numerical values, separated by
 * icons and a tag to indicate a constraint relationship (e.g., less than or equal).
 *
 * @param {BoundConstraintProps} props - The component props.
 *
 * @returns {JSX.Element} A JSX element representing the bound constraint UI.
 */
export function BoundConstraint({
    type,
    minValue,
    maxValue,
    valueTemplate = 'value',
    onEditConstraints,
}: BoundConstraintProps): JSX.Element {
    const allowExclusive = type === 'number';

    const operatorOptions = [
        { label: '≤', value: 'inclusive' },
        { label: '<', value: 'exclusive' },
    ];

    const [minOp, setMinOp] = useState<'inclusive' | 'exclusive'>('inclusive');
    const [maxOp, setMaxOp] = useState<'inclusive' | 'exclusive'>('inclusive');

    const handleMinOpChange = (e: DropdownChangeEvent) => {
        const op = e.value as 'inclusive' | 'exclusive';
        setMinOp(op);

        if (type === 'number') {
            onEditConstraints({
                minimum: op === 'inclusive' ? minValue : undefined,
                exclusiveMinimum: op === 'exclusive' ? minValue : undefined,
            });
        }
    };

    const handleMaxOpChange = (e: DropdownChangeEvent) => {
        const op = e.value as 'inclusive' | 'exclusive';
        setMaxOp(op);

        if (type === 'number') {
            onEditConstraints({
                maximum: op === 'inclusive' ? maxValue : undefined,
                exclusiveMaximum: op === 'exclusive' ? maxValue : undefined,
            });
        }
    };

    const handleMinValueChange = (e: InputNumberChangeEvent) => {
        const v = e.value;

        onEditConstraints({
            minimum: minOp === 'inclusive' ? v : undefined,
            exclusiveMinimum: minOp === 'exclusive' ? v : undefined,
            minLength: v,
            minItems: v,
        });
    };

    const handleMaxValueChange = (e: InputNumberChangeEvent) => {
        const v = e.value;

        onEditConstraints({
            maximum: maxOp === 'inclusive' ? v : undefined,
            exclusiveMaximum: maxOp === 'exclusive' ? v : undefined,
            maxLength: v,
            maxItems: v,
        });
    };

    return (
        <div className="flex gap-1">
            <InputNumber
                pt={inputPtOptions}
                placeholder="min value"
                value={minValue}
                max={maxValue}
                onChange={handleMinValueChange}
            />

            {allowExclusive ? (
                <Dropdown
                    value={minOp}
                    options={operatorOptions}
                    onChange={handleMinOpChange}
                    className="dropdown-compact"
                />
            ) : (
                <Tag className="constraint-tag" value="≤" severity="contrast" />
            )}

            <Tag className="constraint-tag" value={valueTemplate} severity="contrast" />

            {allowExclusive ? (
                <Dropdown
                    value={maxOp}
                    options={operatorOptions}
                    onChange={handleMaxOpChange}
                    className="dropdown-compact"
                />
            ) : (
                <Tag className="constraint-tag" value="≤" severity="contrast" />
            )}

            <InputNumber
                pt={inputPtOptions}
                placeholder="max value"
                value={maxValue}
                min={minValue}
                onChange={handleMaxValueChange}
            />
        </div>
    );
}

/**
 * A React component that renders a form for defining string constraints.
 * This form can be used to specify validation rules or restrictions
 * for string-based inputs in a blueprint or configuration.
 *
 * @param {ConstraintForm} props - The component props.
 *
 * @returns A JSX element representing the string constraint form.
 */
function StringConstraintForm({ constraints, onEditConstraints }: TypeConstraintForm): JSX.Element {
    /**
     * Handles the change event for a dropdown that updates the format constraint.
     *
     * @param e - The dropdown change event containing the selected value.
     */
    const handleFormatChange = (e: DropdownChangeEvent) => {
        onEditConstraints({
            format: e.value,
        });
    };

    // The dropdown options for the format field
    const formatOptions = stringFormats.map((option) => ({
        label: option,
        value: option,
        icon: formatIcons[option],
    }));

    // The item template for the dropdown options
    const itemTemplate = (option: { icon: IconDefinition; label: string }) => (
        <div className="flex align-items-center gap-2">
            <FontAwesomeIcon icon={option.icon} />
            <span>{option.label}</span>
        </div>
    );

    return (
        <>
            <div className="field col-12">
                <label className="constraint-label">
                    <FontAwesomeIcon icon={faTextWidth} />
                    <span>String length bounds</span>
                </label>
                <BoundConstraint
                    type="string"
                    minValue={constraints.minLength}
                    maxValue={constraints.maxLength}
                    onEditConstraints={onEditConstraints}
                    valueTemplate={
                        <>
                            <FontAwesomeIcon icon={faTextWidth} />
                            <span>value</span>
                        </>
                    }
                />
            </div>
            <div className="field col-12">
                <label className="constraint-label">
                    <FontAwesomeIcon icon={faFont} />
                    <span>String Format</span>
                </label>
                <Dropdown
                    className="dropdown-compact"
                    placeholder="Select a format"
                    onChange={handleFormatChange}
                    value={constraints.format}
                    options={formatOptions}
                    itemTemplate={itemTemplate}
                    showClear
                />
            </div>
        </>
    );
}

/**
 * A React component that renders a form for defining number constraints.
 * This form allows users to specify minimum and maximum bounds for a number schema.
 *
 * @param {TypeConstraintForm} props - The properties passed to the component.
 *
 * @returns {JSX.Element} The rendered form component for number constraints.
 */
function NumberConstraintForm({ constraints, onEditConstraints }: TypeConstraintForm): JSX.Element {
    return (
        <div className="field col-12">
            <label className="constraint-label">
                <FontAwesomeIcon icon={faTextWidth} />
                <span>Number bounds</span>
            </label>
            <BoundConstraint
                type="number"
                minValue={constraints.minimum ?? constraints.exclusiveMinimum}
                maxValue={constraints.maximum ?? constraints.exclusiveMaximum}
                onEditConstraints={onEditConstraints}
                valueTemplate={
                    <>
                        <FontAwesomeIcon icon={faTextWidth} />
                        <span>value</span>
                    </>
                }
            />
        </div>
    );
}

/**
 * A React component that renders a form for managing array constraints.
 *
 * @param {ConstraintForm} props - The properties for the ArrayConstraintForm component.
 *
 * @returns {JSX.Element} A JSX element representing the array constraint form.
 */
function ArrayConstraintForm({ constraints, onEditConstraints }: TypeConstraintForm): JSX.Element {
    const handleChangeUnique = (e: CheckboxChangeEvent) => {
        onEditConstraints({
            uniqueItems: e.checked,
        });
    };

    const handleChangeType = (e: DropdownChangeEvent) => {
        onEditConstraints({
            items: {
                ...(constraints.items ?? {}),
                type: e.value,
            },
        });
    };

    return (
        <form className="constraint-form">
            <div className="grid formgrid">
                <div className="field col-12">
                    <label className="constraint-label">
                        <FontAwesomeIcon icon={faExpand} />
                        <span>Array size</span>
                    </label>
                    <BoundConstraint
                        type="array"
                        minValue={constraints.minItems}
                        maxValue={constraints.maxItems}
                        onEditConstraints={onEditConstraints}
                        valueTemplate={
                            <>
                                <FontAwesomeIcon icon={faTextWidth} />
                                <span>value</span>
                            </>
                        }
                    />
                </div>
                <div className="field col-12">
                    <label className="constraint-label">
                        <FontAwesomeIcon icon={faExpand} />
                        <span>Array Item Type</span>
                    </label>

                    <Dropdown
                        className="dropdown-compact"
                        pt={{ panel: { className: 'dropdown-compact' } }}
                        options={jsonTypeNames}
                        value={constraints.items.type}
                        onChange={handleChangeType}
                        itemTemplate={(type) => <TypeTooltip type={type} />}
                        valueTemplate={(type) => <TypeTooltip type={type} />}
                    />
                </div>
                <div className="field col-12">
                    <div className="flex align-items-center gap-2">
                        <Checkbox
                            name="uniqueItems"
                            inputId="uniqueItems"
                            checked={constraints.uniqueItems}
                            onChange={handleChangeUnique}
                            pt={{
                                root: {
                                    className: 'w-auto',
                                },
                            }}
                        />
                        <label htmlFor="uniqueItems" className="constraint-label">
                            Ensure that all elements in the array are unique.
                        </label>
                    </div>
                </div>
            </div>
        </form>
    );
}

export type TypeConstraintForm = {
    constraints: JSONSchema;
    onEditConstraints: (newConstraints: JSONSchema) => void;
};

/**
 * A React component for managing and updating type constraints within a form.
 *
 * @param {ConstraintForm} props - The properties passed to the component.
 * @param {object} props.schema - The schema object defining the structure and rules for the constraints.
 * @param {Function} props.onUpdateConstraints - A callback function triggered when constraints are updated.
 * @returns {JSX.Element} The rendered TypeConstraintForm component.
 */
export function TypeConstraintForm({
    constraints,
    onEditConstraints,
}: TypeConstraintForm): JSX.Element {
    const isString = constraints.type === 'string';
    const isNumber = constraints.type === 'number' || constraints.type === 'integer';
    const isArray = constraints.type === 'array';
    const isObject = constraints.type === 'object';
    const isBoolean = constraints.type === 'boolean';
    const hasExamples = !isArray && !isObject && !isBoolean;

    const handleExamplesChange = (e: ChipsChangeEvent) => {
        onEditConstraints({
            examples: e.value,
        });
    };

    return (
        <form className="constraint-form">
            <div className="grid formgrid">
                {isString ? (
                    <StringConstraintForm
                        constraints={constraints}
                        onEditConstraints={onEditConstraints}
                    />
                ) : isNumber ? (
                    <NumberConstraintForm
                        constraints={constraints}
                        onEditConstraints={onEditConstraints}
                    />
                ) : isArray ? (
                    <ArrayConstraintForm
                        constraints={constraints}
                        onEditConstraints={onEditConstraints}
                    />
                ) : (
                    <div className="field col-12">
                        <span className="text-xs">No contraints to be configured</span>
                    </div>
                )}
                {hasExamples && (
                    <div className="field col-12">
                        <label className="constraint-label">
                            <FontAwesomeIcon icon={faBarsStaggered} />
                            <span>Examples</span>
                        </label>
                        <Chips
                            value={[constraints.examples ?? []].flat().map(String)}
                            onChange={handleExamplesChange}
                            allowDuplicate={false}
                            pt={chipsPtOptions}
                            placeholder="Start typing to add examples"
                            addOnBlur
                        />
                    </div>
                )}
            </div>
        </form>
    );
}
