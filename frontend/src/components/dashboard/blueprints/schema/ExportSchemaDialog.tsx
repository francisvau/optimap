import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { downloadJSON } from '@/utils/fileUtils.ts';
import { FormEvent, JSX, useState } from 'react';
import { JSONSchema } from '@/types/Schema.ts';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';

export type ExportSchemaDialogProps = {
    setExportDialogVisible: (visible: boolean) => void;
    schema: JSONSchema;
};

/**
 * jlfdsjfklqjsdlkf
 * @param setExportDialogVisible.setExportDialogVisible
 * @param setExportDialogVisible ffff
 * @param schema
 * @param setExportDialogVisible.schema
 * @returns element
 */
export function ExportSchemaDialog({
    setExportDialogVisible,
    schema,
}: ExportSchemaDialogProps): JSX.Element {
    const toast = useToast();
    const [fileName, setFileName] = useState<string>('');

    const handleExportSchema = async (e: FormEvent): Promise<void> => {
        e.preventDefault();
        const safeFileName = fileName.trim();
        const finalFileName = safeFileName.endsWith('.json')
            ? safeFileName
            : `${safeFileName}.json`;

        downloadJSON(schema, finalFileName);
        toast({
            severity: 'success',
            detail: 'Input schema exported',
            summary: 'Exported',
        });
        setExportDialogVisible(false);
    };

    return (
        <form onSubmitCapture={handleExportSchema}>
            <div className="grid formgrid">
                <div className="field col-12">
                    <label htmlFor="name">Name</label>
                    <InputText
                        id="name"
                        type="text"
                        placeholder="Export file name"
                        value={fileName}
                        onChange={(e) => setFileName(e.target.value)}
                        required
                    />
                </div>
                <div className="field col-12 flex justify-content-center">
                    <Button
                        type={'submit'}
                        className="mt-4"
                        label={'Export schema'}
                        onClick={handleExportSchema}
                    ></Button>
                </div>
            </div>
        </form>
    );
}
