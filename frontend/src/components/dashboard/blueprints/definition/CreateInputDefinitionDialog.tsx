import {
    InputDefinitionForm,
    InputDefinitionFormProps,
} from '@/components/dashboard/forms/InputDefinitionForm';
import { InputDefinitionRequest } from '@/types/schemas/Blueprint';
import { Dialog, DialogProps } from 'primereact/dialog';
import { JSX } from 'react';

export type InputDefinitionDialogProps = DialogProps &
    InputDefinitionFormProps & {
        onSubmit?: (definition: InputDefinitionRequest) => void;
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
export function CreateInputDefinitionDialog({
    onSubmit,
    isLoading,
    error,
    ...dialogProps
}: InputDefinitionDialogProps): JSX.Element {
    return (
        <Dialog {...dialogProps} header="Create Input Definition">
            <InputDefinitionForm onSubmit={onSubmit} isLoading={isLoading} error={error} />
        </Dialog>
    );
}
