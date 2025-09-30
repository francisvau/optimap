import {
    SourceMappingForm,
    SourceMappingFormProps,
} from '@/components/dashboard/forms/SourceMappingForm';
import { Dialog, DialogProps } from 'primereact/dialog';
import { Message } from 'primereact/message';
import { JSX } from 'react';

export type CreateSourceMappingDialog = DialogProps &
    SourceMappingFormProps & {
        forced?: boolean;
    };

/**
 * A React component that renders a dialog for creating an input definition.
 *
 * @component
 *
 * @param {InputDefinitionDialogProps} props - The props for the dialog component.
 *
 * @returns {JSX.Element} The rendered dialog component.
 */
export function CreateSourceMappingDialog({
    onSubmit,
    isLoading,
    error,
    forced,
    ...dialogProps
}: CreateSourceMappingDialog): JSX.Element {
    return (
        <Dialog {...dialogProps} closable={!forced} header="Create Source Mapping">
            {forced && (
                <Message
                    className="mb-4"
                    content="No source mapping defined for this input definition yet. Please create a new one first."
                />
            )}
            <SourceMappingForm onSubmit={onSubmit} isLoading={isLoading} error={error} />
        </Dialog>
    );
}
