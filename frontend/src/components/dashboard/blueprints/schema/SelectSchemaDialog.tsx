import { SchemaEditor } from '@/components/dashboard/blueprints/schema/editor/SchemaEditor';
import { useSchemaSelector } from '@/hooks/useSchemaSelector';
import { SourceMapping } from '@/types/models/Blueprint';
import { JSONSchema, SubSchemaSelection } from '@/types/Schema';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { ButtonGroup } from 'primereact/buttongroup';
import { Dialog, DialogProps } from 'primereact/dialog';
import { Divider } from 'primereact/divider';
import { JSX } from 'react';

import './SelectSchemaDialog.scss';

export type SelectSchemaDialogProps = DialogProps & {
    schema: JSONSchema;
    targetSchema: JSONSchema;
    initial: SourceMapping;
    onSelectionSave: (selection: SubSchemaSelection) => void;
};

/**
 * A React component that renders a dialog for selecting a schema.
 *
 * @param {SelectSchemaDialogProps} props - The props for the SelectSchemaDialog component.
 *
 * @returns {JSX.Element} The rendered SelectSchemaDialog component.
 */
export function SelectSchemaDialog({
    schema,
    children,
    targetSchema,
    initial,
    onSelectionSave,
    ...dialogProps
}: SelectSchemaDialogProps): JSX.Element {
    const [[selected, isDirty], selector] = useSchemaSelector(targetSchema, [], {
        jsonSchema: initial.outputJsonSchema,
        targetPath: initial.targetPath,
    });

    const handleSelectAll = () => {
        selector.selectAll();
    };

    const handleSelectionSave = () => {
        const selectionToSave = selector.getSelection();
        onSelectionSave(selectionToSave);
    };

    const handleSelectionClear = () => {
        selector.clear();
    };

    return (
        <Dialog {...dialogProps} pt={{ root: { className: 'select-schema-dialog' } }}>
            {children}
            <Divider />
            <SchemaEditor schema={schema} selected={selected} selector={selector} />
            <Divider />
            <div className="select-schema-dialog-buttons">
                <ButtonGroup>
                    <Button
                        icon={PrimeIcons.TIMES}
                        onClick={handleSelectionClear}
                        tooltip="Clear selection"
                        outlined
                    />
                    <Button
                        icon={PrimeIcons.SITEMAP}
                        onClick={handleSelectAll}
                        tooltip="Select all subschemas"
                        outlined
                    />
                    <Button
                        icon={PrimeIcons.CHECK}
                        label="Save subschema"
                        disabled={!selected.length || !isDirty}
                        onClick={handleSelectionSave}
                    />
                </ButtonGroup>
            </div>
        </Dialog>
    );
}
