import { clsx } from 'clsx';
import { Tooltip } from 'primereact/tooltip';
import { Fragment, JSX, useId } from 'react';
import { JSONSchemaTypeName } from '@/types/Schema';

import style from './TypeTooltip.module.scss';

export type TypeTooltipProps = {
    type?: JSONSchemaTypeName | JSONSchemaTypeName[];
    noobMode?: boolean;
};

/**
 * A React component that displays a tooltip with a description of a specific data type.
 * The tooltip provides contextual information about the type, such as its definition
 * and examples, and is triggered by hovering over a target element.
 *
 * @param {TypeTooltipProps} props - The props for the `TypeTooltip` component.
 *
 * @returns {JSX.Element} A JSX element containing the tooltip and the target element.
 */
export function TypeTooltip({ type, noobMode = true }: TypeTooltipProps): JSX.Element {
    const id = useId();

    return (
        <>
            {[type].flat().map((type) => (
                <Fragment key={`${id}-${type}`}>
                    {noobMode && (
                        <Tooltip target={`#${id}-${type}`} position="top" className="w-18rem">
                            {type === 'number' && (
                                <>
                                    A <span className="number">number</span> can be any kind of
                                    numeric value, such as an integer or a float.
                                </>
                            )}
                            {type === 'integer' && (
                                <>
                                    An <span className="integer">integer</span> is a whole number.
                                </>
                            )}
                            {type === 'string' && (
                                <>
                                    A <span className="string">string</span> is a sequence of
                                    characters, like a word or sentence.
                                </>
                            )}
                            {type === 'object' && (
                                <>
                                    An <span className="object">object</span> is a collection of
                                    key-value pairs, like a dictionary.
                                </>
                            )}
                            {type === 'array' && (
                                <>
                                    An <span className="array">array</span> is a list of items, like
                                    an order list.
                                </>
                            )}
                            {type === 'boolean' && (
                                <>
                                    A <span className="boolean">boolean</span> can only be true or
                                    false.
                                </>
                            )}
                            {type === 'null' && (
                                <>
                                    A <span className="null">null</span> value represents the
                                    absence of a value.
                                </>
                            )}
                            {type === undefined && (
                                <>
                                    The type is <span className="undefined">undefined</span>,
                                    meaning it is not specified or not known.
                                </>
                            )}
                        </Tooltip>
                    )}
                    <div id={`${id}-${type}`} className={clsx(type, style['type'])}>
                        {type?.substring(0, 3) ?? 'und'}
                    </div>
                </Fragment>
            ))}
        </>
    );
}
