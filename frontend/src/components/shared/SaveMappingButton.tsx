import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSave, faCheck } from '@fortawesome/free-solid-svg-icons';
import { Button } from 'primereact/button';
import { useEffect, useState } from 'react';

export type SaveMappingButtonProps = {
    disabled?: boolean;
    onClick?: () => void;
    loading?: boolean;
    success?: boolean;
    style?: React.CSSProperties;
};

/**
 * A button component that triggers the saving of mapping rules.
 * @param root0
 * @param root0.disabled
 * @param root0.onClick
 * @param root0.loading
 * @param root0.success
 * @param root0.style
 * @returns JSX.Element
 */
export function SaveMappingButton({
    disabled,
    onClick,
    loading,
    success,
    style,
}: SaveMappingButtonProps) {
    const [showSuccess, setShowSuccess] = useState(false);

    useEffect(() => {
        if (success) {
            setShowSuccess(true);
            const timer = setTimeout(() => {
                setShowSuccess(false);
            }, 2000);
            return () => clearTimeout(timer);
        }
    }, [success]);

    return (
        <Button
            severity={showSuccess ? 'success' : 'info'}
            icon={<FontAwesomeIcon icon={showSuccess ? faCheck : faSave} />}
            tooltip={showSuccess ? 'Mapping rules saved successfully' : 'Save mapping rules'}
            tooltipOptions={{ position: 'top' }}
            disabled={disabled}
            onClick={onClick}
            loading={loading}
            style={style}
        />
    );
}
