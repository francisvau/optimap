import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { SplitButton } from 'primereact/splitbutton';
import { JSX, useRef, useState } from 'react';
import { JSONSchema } from '@/types/Schema';
import { Dialog } from 'primereact/dialog';
import { ImportSchemaDialog } from '@/components/dashboard/blueprints/schema/ImportSchemaDialog';

import './SchemaActions.scss';
import { ExportSchemaDialog } from '@/components/dashboard/blueprints/schema/ExportSchemaDialog.tsx';

export type SchemaActionsProps = {
    isDirty?: boolean;
    schema: JSONSchema;
    onResetClick: () => void;
    onSchemaUpload: (schema: JSONSchema) => void;
};

/**
 * A React component that provides actions for managing a schema, including importing, exporting,
 * and resetting changes. It uses a split button for export/import actions and a button for undoing changes.
 *
 * @param {SchemaActionsProps} props - The props for the `SchemaActions` component.
 *
 * @returns {JSX.Element} A JSX element containing the schema action buttons.
 */
export function SchemaActions({
    isDirty,
    schema,
    onResetClick,
    onSchemaUpload,
}: SchemaActionsProps): JSX.Element {
    const splitBtnRef = useRef(null);

    const [importDialogVisible, setImportDialogVisible] = useState(false);
    const [exportDialogVisible, setExportDialogVisible] = useState(false);

    const fileActions = [
        {
            label: 'Import schema',
            icon: PrimeIcons.UPLOAD,
            command: () => {
                setImportDialogVisible(true);
            },
        },
        {
            label: 'Export schema',
            icon: PrimeIcons.DOWNLOAD,
            command: () => {
                setExportDialogVisible(true);
            },
        },
    ];

    return (
        <>
            <Dialog
                onHide={() => setImportDialogVisible(false)}
                visible={importDialogVisible}
                header="Import Schema"
            >
                <ImportSchemaDialog
                    onSchemaUpload={onSchemaUpload}
                    setImportDialogVisible={setImportDialogVisible}
                />
            </Dialog>
            <Dialog
                onHide={() => setExportDialogVisible(false)}
                visible={exportDialogVisible}
                header="Export JSON Schema"
            >
                <ExportSchemaDialog
                    setExportDialogVisible={setExportDialogVisible}
                    schema={schema}
                />
            </Dialog>
            <div className="flex gap-2">
                {isDirty && (
                    <Button
                        severity="contrast"
                        icon={PrimeIcons.REPLAY}
                        label="Undo"
                        onClick={() => onResetClick()}
                    ></Button>
                )}
                <SplitButton
                    severity="contrast"
                    ref={splitBtnRef}
                    onClick={(e) => splitBtnRef.current?.show(e)}
                    model={fileActions}
                    icon={PrimeIcons.FILE}
                    label="Export / Import"
                ></SplitButton>
            </div>
        </>
    );
}
