import { FormProps } from '@/types/Form';
import { SourceMappingRequest } from '@/types/schemas/Blueprint';
import { JSX, useState } from 'react';
import { Message } from 'primereact/message';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';

export type SourceMappingFormProps = FormProps<SourceMappingRequest>;

/**
 * A React component that renders a form for source mapping. This form allows users
 * to input a name and submit the data. It also displays an error message if an error
 * occurs and shows a loading state during submission.
 *
 * @param {SourceMappingFormProps} props - The props for the `SourceMappingForm` component.
 *
 * @returns {JSX.Element} The rendered `SourceMappingForm` component.
 */
export function SourceMappingForm({
    onSubmit,
    isLoading,
    error,
}: SourceMappingFormProps): JSX.Element {
    const [form, setForm] = useState<SourceMappingRequest>({
        name: '',
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
                            placeholder="Source Mapping Title"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            required
                        ></InputText>
                    </div>
                    <div className="col-12 mt-3 mb-3">
                        <Button className="w-full" label="Submit" loading={isLoading}></Button>
                    </div>
                </div>
            </form>
        </>
    );
}
