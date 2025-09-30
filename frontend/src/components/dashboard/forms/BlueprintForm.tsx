import { BlueprintRequest } from '@/types/schemas/Blueprint';
import { FormProps } from '@/types/Form';
import { Organization } from '@/types/models/Organization';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Message } from 'primereact/message';
import { JSX, useState } from 'react';
import { useOrganization } from '@/hooks/context/OrganizationProvider/OrganizationContext';

export type CreateBlueprintFormProps = FormProps<BlueprintRequest> & {
    organizations?: Organization[] | null;
};

/**
 * A React component that renders a form for creating a blueprint.
 *
 * @template T - The type of the form data.
 * @param {FormProps<T>} props - The props for the form component.
 * @param {function} props.handleSubmit - The function to handle the form submission.
 * @returns {JSX.Element} The rendered form component.
 */
export function BlueprintForm({
    onSubmit,
    isLoading,
    error,
    organizations,
    initial,
}: CreateBlueprintFormProps): JSX.Element {
    const { organization } = useOrganization();
    const [form, setForm] = useState<BlueprintRequest>(
        initial ?? {
            name: '',
            description: '',
            userId: undefined,
            organizationId: organization?.id,
        },
    );

    return (
        <>
            {error && <Message severity="error" text={error} className="mb-4 w-full text-center" />}

            <form action={() => void onSubmit(form)}>
                <div className="formgrid grid">
                    <div className="field col-6">
                        <label htmlFor="name">Name</label>
                        <InputText
                            id="name"
                            name="name"
                            placeholder="Blueprint Name"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            required
                        ></InputText>
                    </div>
                    {organizations && (
                        <div className="field col-6">
                            <label htmlFor="organizationId">Organization (optional)</label>
                            <Dropdown
                                showClear
                                id="organizationId"
                                value={form.organizationId}
                                options={organizations}
                                optionLabel="name"
                                optionValue="id"
                                placeholder="Select an organization"
                                onChange={(e) => setForm({ ...form, organizationId: e.value })}
                            />
                        </div>
                    )}
                    <div className="field col-12">
                        <label htmlFor="description">Description</label>
                        <InputTextarea
                            id="description"
                            name="description"
                            placeholder="Blueprint Description"
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
