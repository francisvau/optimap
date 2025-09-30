import React, { JSX, useRef } from 'react';
import { exampleDataIcons, uploadJSON } from '@/utils/fileUtils.ts';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { JSONSchema7 } from 'json-schema';
import { clsx } from 'clsx';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileLines, faFileZipper } from '@fortawesome/free-solid-svg-icons';

import Ajv from 'ajv';
import './ImportSchemaDialog.scss';
import { Tooltip } from 'primereact/tooltip';
import { extractSchemaFromExampleData } from '@/services/mapping/blueprintService';

export type ImportSchemaDialogProps = {
    onSchemaUpload: (schema: JSONSchema7) => void;
    setImportDialogVisible: (visible: boolean) => void;
};

/**
 * A React component that provides actions for managing a schema, including importing, exporting,
 * and resetting changes. It uses a split button for export/import actions and a button for undoing changes.
 *
 * @param {ImportSchemaDialogProps} props - The props for the `SchemaActions` component.
 *
 * @returns {JSX.Element} A JSX element containing the schema action buttons.
 */
export function ImportSchemaDialog({
    onSchemaUpload,
    setImportDialogVisible,
}: ImportSchemaDialogProps): JSX.Element {
    const toast = useToast();
    const fileInputRef1 = useRef<HTMLInputElement>(null);
    const fileInputRef2 = useRef<HTMLInputElement>(null);

    // Handler for JSON schema uploads
    const handleInputSchemaUpload = async (file: File) => {
        if (!file) return;

        const maxSizeInBytes = 30 * 1024 * 1024;
        if (file.size > maxSizeInBytes) {
            toast({
                severity: 'error',
                detail: 'File is larger than 30MB.',
                summary: 'Upload failed',
            });
            return;
        }

        await uploadJSON(
            file,
            (schema) => {
                const ajv = new Ajv();
                ajv.validateSchema(schema);

                if (ajv.errors) {
                    toast({
                        severity: 'error',
                        detail: ajv.errorsText(),
                        summary: 'Invalid JSON schema',
                        life: 10000,
                    });
                } else {
                    toast({
                        severity: 'success',
                        detail: 'Input schema imported',
                        summary: 'Imported',
                    });
                    onSchemaUpload(schema);
                }
            },
            () => {
                toast({
                    severity: 'error',
                    detail: 'The file is not readable or does not contain valid JSON.',
                    summary: 'Invalid JSON file',
                });
            },
        );
        setImportDialogVisible(false);
    };

    // Handler for example data uploads
    const handleExampleDataUpload = async (file: File) => {
        if (!file) return;

        const maxSizeInBytes = 30 * 1024 * 1024;
        if (file.size > maxSizeInBytes) {
            toast({
                severity: 'error',
                detail: 'File is larger than 30MB.',
                summary: 'Upload failed',
            });
            return;
        }

        const schema = await extractSchemaFromExampleData(file)
            .then((response) => response)
            .catch((reason) => {
                toast({
                    severity: 'error',
                    detail: `${reason}`,
                    summary: 'Invalid JSON file',
                });
            });
        if (schema) {
            toast({
                severity: 'success',
                detail: 'Input schema imported',
                summary: 'Imported',
            });
            onSchemaUpload(schema.jsonSchema);
        }

        setImportDialogVisible(false);
    };

    // Handler for input change events
    const handleInputChange = (event, uploadHandler) => {
        const file = event.target.files?.[0];
        if (file) {
            uploadHandler(file);
        }
        // Reset input value to allow uploading the same file again
        event.target.value = '';
    };

    // Universal drag event handlers
    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e, uploadHandler) => {
        e.preventDefault();
        e.stopPropagation();

        const file = e.dataTransfer.files?.[0];
        if (file) {
            uploadHandler(file);
        }
    };

    return (
        <div>
            <Tooltip target=".input-definition-wrapper" />
            <input
                type="file"
                accept={'application/json'}
                className="hidden"
                ref={fileInputRef1}
                onChange={(e) => handleInputChange(e, handleInputSchemaUpload)}
            />
            <input
                type="file"
                accept={'application/sql, application/json, application/xml, text/csv, text/xml'}
                className="hidden"
                ref={fileInputRef2}
                onChange={(e) => handleInputChange(e, handleExampleDataUpload)}
            />

            <div
                className={clsx('input-definition-wrapper')}
                data-pr-tooltip="Import a file with the specific JSON schema"
                data-pr-position="top"
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, handleInputSchemaUpload)}
            >
                <div
                    className={'input-definition'}
                    onClick={() => {
                        fileInputRef1.current?.click();
                    }}
                >
                    <div className="input-definition__left">
                        <FontAwesomeIcon icon={faFileZipper} size="2xl" />
                    </div>
                    <div className="input-definition__center">
                        <h3>Import JSON Schema</h3>
                    </div>
                </div>
            </div>

            <div
                className={clsx('input-definition-wrapper')}
                data-pr-tooltip="Import an example file, the schema will be extracted automatically"
                data-pr-position="top"
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, handleExampleDataUpload)}
            >
                <div
                    className={'input-definition'}
                    onClick={() => {
                        fileInputRef2.current?.click();
                    }}
                >
                    <div className="input-definition__left">
                        <FontAwesomeIcon icon={faFileLines} size="2xl" />
                    </div>

                    <div className="input-definition__center">
                        <h3>Import Example Data</h3>
                    </div>

                    <div className="input-definition__right">
                        <div className="supported-files">Supported file types:</div>
                        <div className="file-types">
                            {Object.entries(exampleDataIcons).map(([key, icon]) => (
                                <div key={key} className="file-type">
                                    <i className={icon} style={{ marginRight: '0.5rem' }} />
                                    {key}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ImportSchemaDialog;
