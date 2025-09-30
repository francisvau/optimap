import {
    faLessThan,
    faLessThanEqual,
    faDivide,
    faHashtag,
    faListCheck,
    faEquals,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { JSX } from 'react';
import { Tag } from 'primereact/tag';
import { formatIcons } from '@/utils/schema/schemaUtils';

import style from './TypeConstraint.module.scss';
import { JSONSchema } from '@/types/Schema';
import { TypeTooltip } from '@/components/dashboard/blueprints/schema/editor/TypeTooltip';

export type ConstraintProps = {
    value: JSONSchema;
};

/**
 * A React component that renders a set of constraint tags for numeric values.
 * This component displays various constraints such as minimum, maximum, and divisibility
 * based on the provided `value` prop.
 *
 * @param {ConstraintProps} props - The props for the component.
 *
 * @returns {JSX.Element} A JSX element containing the rendered constraint tags.
 */
export function NumberConstraints({ value }: ConstraintProps): JSX.Element {
    const { minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf } = value;

    const hasMinimum = minimum !== undefined || exclusiveMinimum !== undefined;
    const hasMaximum = maximum !== undefined || exclusiveMaximum !== undefined;
    const exactValue = minimum !== undefined && minimum === maximum;

    return (
        <div className={style['constraint-wrapper']}>
            {exactValue ? (
                <Tag
                    className={style['constraint-tag']}
                    severity="contrast"
                    value={
                        <>
                            <span className="font-medium">value</span>
                            <FontAwesomeIcon icon={faEquals} />
                            {exclusiveMinimum ?? minimum}
                        </>
                    }
                />
            ) : (
                <>
                    {(hasMinimum || hasMaximum) && (
                        <Tag
                            className={style['constraint-tag']}
                            severity="contrast"
                            value={
                                <>
                                    {hasMinimum && (
                                        <>
                                            {exclusiveMinimum ?? minimum}
                                            <FontAwesomeIcon
                                                icon={
                                                    exclusiveMinimum ? faLessThan : faLessThanEqual
                                                }
                                            />
                                        </>
                                    )}

                                    <span>value</span>

                                    {hasMaximum && (
                                        <>
                                            <FontAwesomeIcon
                                                icon={
                                                    exclusiveMaximum ? faLessThan : faLessThanEqual
                                                }
                                            />
                                            {exclusiveMaximum ?? maximum}
                                        </>
                                    )}
                                </>
                            }
                        />
                    )}
                </>
            )}

            {multipleOf !== undefined && (
                <Tag
                    className={style['constraint-tag']}
                    severity="contrast"
                    value={
                        <>
                            <FontAwesomeIcon icon={faDivide} />
                            {multipleOf}
                        </>
                    }
                />
            )}
        </div>
    );
}

/**
 * A React component that renders a set of constraints for a string type.
 *
 * @param {ConstraintProps} props - The properties for the component.
 *
 * @returns {JSX.Element} A JSX element displaying the string constraints as tags.
 */
export function StringConstraints({ value }: ConstraintProps): JSX.Element {
    const { minLength, maxLength, format } = value;
    const hasLength = minLength !== undefined || maxLength !== undefined;
    const hasExactLength = hasLength && minLength === maxLength;

    return (
        <div className={style['constraint-wrapper']}>
            {hasExactLength ? (
                <Tag
                    className={style['constraint-tag']}
                    severity="contrast"
                    value=<>
                        <FontAwesomeIcon icon={faHashtag} /> chars
                        <FontAwesomeIcon icon={faEquals} />
                        {minLength}
                    </>
                />
            ) : (
                hasLength && (
                    <Tag
                        className={style['constraint-tag']}
                        severity="contrast"
                        value={
                            <>
                                {minLength !== undefined && (
                                    <>
                                        {minLength}
                                        <FontAwesomeIcon icon={faLessThanEqual} />
                                    </>
                                )}
                                <FontAwesomeIcon icon={faHashtag} /> chars
                                {maxLength !== undefined && (
                                    <>
                                        <FontAwesomeIcon icon={faLessThanEqual} />
                                        {maxLength}
                                    </>
                                )}
                            </>
                        }
                    />
                )
            )}

            {format && (
                <Tag
                    className={style['constraint-tag']}
                    severity="contrast"
                    value={
                        <>
                            <FontAwesomeIcon icon={formatIcons[format] || faHashtag} />
                            <span className="format">{format}</span>
                        </>
                    }
                />
            )}
        </div>
    );
}

/**
 * A React component that renders constraints for an array type.
 *
 * @param {ConstraintProps} props - The properties for the component.
 *
 * @returns {JSX.Element} A JSX element displaying the array constraints, including item count and uniqueness.
 */
export function ArrayConstraints({ value }: ConstraintProps): JSX.Element {
    const hasLength = value.minItems !== undefined || value.maxItems !== undefined;

    return (
        <div className={style['constraint-wrapper']}>
            {hasLength && (
                <Tag
                    className={style['constraint-tag']}
                    severity="contrast"
                    value={
                        <>
                            {value.minItems !== undefined && (
                                <>
                                    {value.minItems}
                                    <FontAwesomeIcon icon={faLessThanEqual} />
                                </>
                            )}
                            <FontAwesomeIcon icon={faHashtag} /> items
                            {value.maxItems !== undefined && (
                                <>
                                    <FontAwesomeIcon icon={faLessThanEqual} />
                                    {value.maxItems}
                                </>
                            )}
                        </>
                    }
                />
            )}

            {value.uniqueItems && (
                <Tag
                    className={style['constraint-tag']}
                    severity="contrast"
                    value={
                        <span>
                            <FontAwesomeIcon icon={faListCheck} /> Unique items
                        </span>
                    }
                />
            )}

            <Tag
                className={style['constraint-tag']}
                severity="contrast"
                value={
                    <>
                        <FontAwesomeIcon icon={faHashtag} />
                        <TypeTooltip type={value.items.type} />
                    </>
                }
            />
        </div>
    );
}

/**
 * A React component that renders specific constraint components based on the type of the provided value.
 *
 * @param {ConstraintProps} props - The props for the component.
 * @param {any} props.value - The value whose type determines which constraint component to render.
 *
 * @returns {JSX.Element} A JSX element containing the appropriate constraint component(s) for the given value type.
 *
 */
export function TypeConstraint({ value }: ConstraintProps): JSX.Element {
    return (
        <>
            {(value.type === 'number' || value.type === 'integer') && (
                <NumberConstraints value={value}></NumberConstraints>
            )}
            {value.type === 'string' && <StringConstraints value={value}></StringConstraints>}
            {value.type === 'array' && <ArrayConstraints value={value}></ArrayConstraints>}
        </>
    );
}
