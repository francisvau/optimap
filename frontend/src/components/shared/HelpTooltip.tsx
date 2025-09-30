import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { OverlayPanel } from 'primereact/overlaypanel';
import { Tooltip } from 'primereact/tooltip';
import { JSX, useId, useRef } from 'react';

export type HelpTooltipProps = {
    tooltip?: string;
    overlay?: string | JSX.Element;
};

/**
 * A reusable HelpTooltip component that displays an informational tooltip
 * when the user hovers over the associated icon.
 *
 * @param {HelpTooltipProps} props - The component props.
 *
 * @returns {JSX.Element} A tooltip component with an info icon.
 *
 */
export function HelpTooltip({ tooltip, overlay }: HelpTooltipProps): JSX.Element {
    const id = useId();
    const overlayPanelRef = useRef(null);

    return (
        <>
            {tooltip && <Tooltip target={`#${id}`} content={tooltip} position="top"></Tooltip>}

            <Button
                role="button"
                type="button"
                icon={PrimeIcons.INFO_CIRCLE}
                id={id}
                style={{
                    padding: '0',
                    width: '20px',
                    height: '20px',
                }}
                onClick={(e) => overlayPanelRef?.current.toggle(e)}
                aria-label="Type Info"
                size="small"
                rounded
                text
            />

            {overlay && (
                <OverlayPanel ref={overlayPanelRef} style={{ width: '400px' }}>
                    {overlay}
                </OverlayPanel>
            )}
        </>
    );
}
