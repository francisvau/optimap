import { type InputDefinitionRequest } from '@/types/schemas/Blueprint';
import { FormProps } from '@/types/Form';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Message } from 'primereact/message';
import { JSX, useState } from 'react';

export type InputDefinitionFormProps = FormProps<InputDefinitionRequest>;

/**
 * A form component for defining input fields in the dashboard.
 *
 * @param {InputDefinitionFormProps} props - The properties for the InputDefinitionForm component.
 *
 * @returns {JSX.Element} The rendered InputDefinitionForm component.
 */
export function InputDefinitionForm({
    isLoading,
    error,
    onSubmit,
}: InputDefinitionFormProps): JSX.Element {
    const [form, setForm] = useState<InputDefinitionRequest>({
        name: '',
        description: '',
    });

    return (
        <>
            {error && <Message severity="error" text={error} className="mb-4 w-full text-center" />}

            <form action={() => void onSubmit(form)}>
                <div className="formgrid grid">
                    <div className="field col-12">
                        <label htmlFor="name">Name</label>
                        <InputText
                            id="name"
                            name="name"
                            placeholder="Input Definition Title"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            required
                        ></InputText>
                    </div>
                    <div className="field col-12">
                        <label htmlFor="description">Description</label>
                        <InputTextarea
                            id="description"
                            name="description"
                            placeholder="Input Definition Description"
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            rows={5}
                        ></InputTextarea>
                    </div>
                    <div className="col-12 mt-3 mb-3">
                        <Button className="w-full" label="Submit" loading={isLoading}></Button>
                    </div>
                </div>
            </form>
        </>
    );
}
