import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faWandMagicSparkles, faCheck } from '@fortawesome/free-solid-svg-icons';
import { useEffect, useMemo, useState } from 'react';
import { SplitButton, SplitButtonProps } from 'primereact/splitbutton';
import { Model } from '@/types/models/Model';
import { Button, ButtonProps } from 'primereact/button';
import { baseModelMeta, baseModelOptions, BaseModelType } from '@/utils/modelUtils';
import { MenuItem } from 'primereact/menuitem';
import { capitalize } from '@/utils/stringUtils';

export type GenerateRulesButtonProps = {
    disabled?: boolean;
    onClick?: (modelId?: string) => void;
    loading?: boolean;
    success?: boolean;
    style?: React.CSSProperties;
    models?: Model[];
};

/**
 * A button component that triggers the generation of mapping rules.
 *
 * @param {GenerateRulesButtonProps} props - The properties for the button.
 *
 * @returns JSX.Element
 */
export function GenerateRulesButton({
    disabled,
    onClick,
    loading,
    success,
    style,
    models,
}: GenerateRulesButtonProps) {
    const [showSuccess, setShowSuccess] = useState(false);

    const dropdownItems = useMemo(() => {
        const template = (model: Model) => {
            return (
                <>
                    <div
                        className="p-2 flex gap-2 align-items-center text-sm cursor-pointer"
                        onClick={() => onClick?.(model.id)}
                    >
                        <img
                            src={baseModelMeta[model.baseModel].logo}
                            alt={model.baseModel}
                            style={{ height: '1.5rem', width: '1.5rem', objectFit: 'contain' }}
                        />
                        <span className="font-bold">{capitalize(model.name)}</span>
                    </div>
                </>
            );
        };

        const items: MenuItem[] = baseModelOptions.map((model: BaseModelType) => ({
            template: template({
                id: model,
                name: model,
                baseModel: model,
                tailorPrompt: [],
            }),
        }));

        if (models) {
            items.push({
                label: 'Tailored Models',
                disabled: true,
            });
            items.push(
                ...models.map((model: Model) => ({
                    template: template(model),
                })),
            );
        }

        return items;
    }, [models, onClick]);

    useEffect(() => {
        if (success) {
            setShowSuccess(true);
            const timer = setTimeout(() => {
                setShowSuccess(false);
            }, 2000);
            return () => clearTimeout(timer);
        }
    }, [success]);

    const tooltipMessage = showSuccess
        ? 'Rules generated successfully'
        : 'Attempt to automatically generate the mapping rules';

    const buttonProps: ButtonProps & SplitButtonProps = {
        severity: showSuccess ? 'success' : 'help',
        icon: <FontAwesomeIcon icon={showSuccess ? faCheck : faWandMagicSparkles} />,
        tooltip: tooltipMessage,
        tooltipOptions: { position: 'top' },
        disabled: disabled,
        onClick: () => onClick(),
        loading: loading,
        style: style,
    };

    return models ? (
        <SplitButton {...buttonProps} model={dropdownItems} />
    ) : (
        <Button {...buttonProps} />
    );
}
