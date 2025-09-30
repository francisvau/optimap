import { FormEvent, JSX, useState } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { OrganizationRequest } from '@/types/schemas/Organization';
import { InputTextarea } from 'primereact/inputtextarea';
import { FormProps } from '@/types/Form';

export type CreateOrganizationFormFormProps = FormProps<OrganizationRequest>;

/**
 * ForgotPasswordForm component
 *
 * This component renders a form for users to request a password reset link.
 *
 * @param {CreateOrganizationFormFormProps} props - The component props
 *
 * @returns {JSX.Element} The rendered ForgotPasswordForm component
 */
export function CreateOrganizationForm({
    onSubmit,
    error,
    isLoading,
    initial,
}: CreateOrganizationFormFormProps): JSX.Element {
    const [form, setForm] = useState<OrganizationRequest>(
        initial ?? {
            name: '',
            address: '',
            branch: '',
            systemPrompt: '',
        },
    );

    const handleSubmit = async (e: FormEvent): Promise<void> => {
        e.preventDefault();
        await onSubmit(form);
    };

    return (
        <>
            {error && <p className="text-red-500">{error}</p>}

            <form onSubmitCapture={handleSubmit}>
                <div className="grid formgrid">
                    <div className="field col-6">
                        <label htmlFor="name">Name</label>
                        <InputText
                            id="name"
                            name="name"
                            type="text"
                            placeholder="Organization Name"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            required
                        />
                    </div>
                    <div className="field col-6">
                        <label htmlFor="address">Address</label>
                        <InputText
                            id="address"
                            name="address"
                            type="text"
                            placeholder="Organization Address"
                            value={form.address}
                            onChange={(e) => setForm({ ...form, address: e.target.value })}
                        />
                    </div>
                    <div className="field col-12">
                        <label htmlFor="branch">Branch</label>
                        <InputText
                            id="branch"
                            name="branch"
                            type="text"
                            placeholder="Organization Branch"
                            value={form.branch}
                            onChange={(e) => setForm({ ...form, branch: e.target.value })}
                        />
                    </div>
                    <div className="field col-12">
                        <label htmlFor="systemPrompt">Description</label>
                        <InputTextarea
                            id="systemPrompt"
                            name="systemPrompt"
                            placeholder="Organization Description"
                            value={form.systemPrompt}
                            onChange={(e) => setForm({ ...form, systemPrompt: e.target.value })}
                            required
                        />
                    </div>
                    <div className="field col-12 flex justify-content-center">
                        <Button
                            type={'submit'}
                            className="mt-4"
                            iconPos="right"
                            label={initial ? 'Update Organization' : 'Create Organization'}
                            disabled={isLoading}
                            loading={isLoading}
                        ></Button>
                    </div>
                </div>
            </form>
        </>
    );
}
