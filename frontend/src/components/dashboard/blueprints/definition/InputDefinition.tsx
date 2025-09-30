import { InputDefinition as Definition } from '@/types/models/Blueprint';
import { JSX, useMemo } from 'react';
import { TreeNode, TreeNodeComponent } from '@/components/shared/data/tree/Tree';
import { PrimeIcons } from 'primereact/api';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';
import { DialogProps, Dialog } from 'primereact/dialog';
import { clsx } from 'clsx';
import { Message } from 'primereact/message';
import { dataTypeIcons } from '@/utils/fileUtils';

import style from './InputDefinition.module.scss';
import { Dropdown } from 'primereact/dropdown';

export type InputDefinitionProps = {
    definition: Definition;
    selected: boolean;
    versions?: Definition[];
    onVersionClick?: (version: Definition) => void;
    onVersionCreateClick?: (version: Definition) => void;
    onClick?: (definition: Definition) => void;
    onDeleteClick?: (definition: Definition) => void;
};

/**
 * A React component that renders an input definition item.
 *
 * @param {InputDefinitionItemProps} props - The props for the component.
 * @param {Object} props.definition - The input definition object.
 * @param {string} props.definition.name - The name of the input definition.
 * @returns {JSX.Element} A JSX element displaying the input definition name.
 */
export function InputDefinition({
    definition,
    selected,
    versions,
    onVersionClick,
    onVersionCreateClick,
    onClick,
    onDeleteClick,
}: InputDefinitionProps): JSX.Element {
    // Memoize the tree structure for the input definition.
    const tree = useMemo<TreeNode>(
        () => ({
            icon: PrimeIcons.CLOUD_DOWNLOAD,
            children: definition.sourceMappings.map((mapping) => ({
                icon: dataTypeIcons[mapping.fileType ?? 'JSON'],
                tooltip: mapping.name,
            })),
        }),
        [definition],
    );

    const handleDeleteClick = (event: React.MouseEvent) => {
        event.stopPropagation();
        if (onDeleteClick) {
            onDeleteClick(definition);
        }
    };

    return (
        <div className={clsx(style['input-definition-wrapper'], { [style['selected']]: selected })}>
            <div className={style['input-definition']} onClick={() => onClick(definition)}>
                <div className="w-4">
                    <TreeNodeComponent node={tree} />
                </div>
                <div className="w-7 my-1">
                    <h4 className="my-0">{definition.name}</h4>
                    {definition.description && (
                        <p className="mt-3 mb-0">{definition.description}</p>
                    )}
                    {versions && (
                        <div className="flex mt-3" onClick={(e) => e.stopPropagation()}>
                            <Dropdown
                                options={versions}
                                value={versions.find((v) => v.id === definition.id)}
                                onChange={(e) => onVersionClick(e.value)}
                                valueTemplate={() => (
                                    <>
                                        <span>Version {definition.version}</span>
                                    </>
                                )}
                                itemTemplate={(option: Definition) => (
                                    <div className="flex align-items-center gap-2">
                                        <span>Version {option.version}</span>
                                        {definition.id === option.id && (
                                            <span className="text-xs">(Selected)</span>
                                        )}
                                    </div>
                                )}
                            />
                            <Button
                                icon={PrimeIcons.PLUS}
                                tooltip="Create a new version from this definition"
                                tooltipOptions={{ position: 'top' }}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (onVersionCreateClick) {
                                        onVersionCreateClick(definition);
                                    }
                                }}
                                text
                            />
                        </div>
                    )}
                </div>
                <div className="flex align-items-center gap-2">
                    {selected && <Tag severity="contrast" className="outlined" value="Selected" />}
                    {onDeleteClick && (
                        <Button
                            severity="danger"
                            icon={PrimeIcons.TRASH}
                            onClick={handleDeleteClick}
                            tooltip="Delete Input Definition"
                            text
                        />
                    )}
                </div>
            </div>
        </div>
    );
}

// Extend the Dialog's props by intersecting it with your custom props.
export type InputDefinitionDialogProps = {
    defs: Definition[];
    selected?: Definition | null;
    onSelectDefinition?: (group: Definition) => void;
    onCreateClick?: () => void;
} & DialogProps;

/**
 * A React component that renders a dialog for selecting an input definition.
 * This dialog is used to group multiple data sources, each with its own mapping,
 * and allows users to choose a specific input definition.
 *
 * @param {InputDefinitionDialogProps} props - The props for the component.
 *
 * @returns {JSX.Element} The rendered `InputDefinitionDialog` component.
 */
export function InputDefinitionDialog({
    defs,
    onSelectDefinition,
    onCreateClick,
    selected,
    ...dialogProps
}: InputDefinitionDialogProps): JSX.Element {
    return (
        <Dialog
            {...dialogProps}
            style={{
                maxWidth: '100%',
                width: '600px',
            }}
            draggable={false}
            resizable={false}
            header="Select Input Definition"
            modal
        >
            <p className="mt-0 text-muted font-bold text-sm">
                An input definition groups multiple data sources, each with its own mapping.
            </p>
            <p className="text-muted text-sm">
                These mappings define how different types of input data are transformed
                individually.
            </p>
            <div className="flex flex-column mt-5 gap-3">
                {defs.length ? (
                    defs.map((definition: Definition) => (
                        <InputDefinition
                            key={definition.id}
                            definition={definition}
                            selected={definition?.id === selected?.id}
                            onClick={onSelectDefinition}
                        />
                    ))
                ) : (
                    <Message content="No input definitions created yet." />
                )}
            </div>
            <Button
                className="mt-5"
                icon={PrimeIcons.PLUS}
                label="Create a new definition"
                onClick={onCreateClick}
                outlined
            ></Button>
        </Dialog>
    );
}
