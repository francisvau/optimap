import { FormProps } from '@/types/Form';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { Message } from 'primereact/message';
import { JSX, useMemo, useState } from 'react';
import { CreateJobRequest } from '@/types/schemas/Job';
import { JobType } from '@/types/models/Job';
import { InputDefinition, MappingBlueprint } from '@/types/models/Blueprint';
import { HelpTooltip } from '@/components/shared/HelpTooltip';
import { jobTypeMeta } from '@/utils/jobUtils';
import { InputText } from 'primereact/inputtext';

export type CreateJobFormProps = FormProps<CreateJobRequest> & {
    blueprints: MappingBlueprint[] | null;
};

/**
 * A React component that renders a form for creating a blueprint.
 *
 * @template T - The type of the form data.
 * @param {FormProps<T>} props - The props for the form component.
 * @param {function} props.handleSubmit - The function to handle the form submission.
 * @returns {JSX.Element} The rendered form component.
 */
export function CreateJobForm({
    onSubmit,
    isLoading,
    error,
    initial,
    blueprints,
}: CreateJobFormProps): JSX.Element {
    const [form, setForm] = useState<CreateJobRequest>(
        initial ?? {
            blueprintId: null,
            inputDefinitionId: null,
            type: JobType.STATIC,
            externalApiEndpoint: null,
        },
    );

    const inputDefinitions = useMemo<InputDefinition[]>(() => {
        if (blueprints !== null) {
            const blueprint = blueprints.find((b) => b.id === form.blueprintId);
            return blueprint?.inputDefinitions ?? [];
        }
    }, [blueprints, form.blueprintId]);

    return (
        <>
            {error && <Message severity="error" text={error} className="mb-4 w-full text-center" />}

            <form action={() => void onSubmit(form)}>
                <div className="formgrid grid">
                    {/* <div className="field col-6">
                        <label htmlFor="name">Mapping Job name</label>
                        <InputText
                            id="name"
                            name="name"
                            placeholder="Job Name"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            required
                        ></InputText>
                    </div> */}
                    <div className="field col-12">
                        <label
                            htmlFor="type"
                            className="flex justify-content-between font-medium mb-2 block"
                        >
                            Type
                            <HelpTooltip
                                overlay={
                                    <div className="p-2">
                                        <p className="m-0">
                                            <b>Static mapping job:</b> a one-time execution of a
                                            mapping blueprint where a dataset is uploaded,
                                            transformed, and produced as a file.
                                        </p>
                                        <p className="mt-3">
                                            <b>Dynamic mapping job:</b> a repeatable, on-demand
                                            execution of a mapping blueprint where incoming data is
                                            continuously mapped to the target schema through a
                                            pipeline.
                                        </p>
                                    </div>
                                }
                            />
                        </label>

                        <Dropdown
                            id="type"
                            name="type"
                            value={form.type}
                            onChange={(e) => {
                                setForm({
                                    ...form,
                                    type: e.value,
                                });
                            }}
                            options={Object.values(JobType)}
                            valueTemplate={(option) => jobTypeMeta[option].label}
                            itemTemplate={(option) => jobTypeMeta[option].label}
                            placeholder="Select a Type"
                            required
                        />
                    </div>

                    <div className="field col-6">
                        <label htmlFor="blueprint" className="font-medium mb-2 block">
                            Blueprint
                        </label>
                        <Dropdown
                            id="blueprint"
                            name="blueprint"
                            value={form.blueprintId}
                            onChange={(e) => {
                                setForm({
                                    ...form,
                                    blueprintId: e.value,
                                });
                            }}
                            options={blueprints}
                            optionLabel="name"
                            optionValue="id"
                            placeholder="Select a Blueprint"
                            required
                        />
                    </div>

                    <div className="field col-6">
                        <label htmlFor="inputDefinition" className="font-medium mb-2 block">
                            Input Definition
                        </label>
                        <Dropdown
                            id="inputDefinition"
                            name="inputDefinition"
                            value={form.inputDefinitionId}
                            onChange={(e) => {
                                setForm({
                                    ...form,
                                    inputDefinitionId: e.value,
                                });
                            }}
                            options={inputDefinitions}
                            optionLabel="name"
                            optionValue="id"
                            placeholder="Select an Input Definition"
                            required
                            className="w-full"
                        />
                    </div>

                    {form.type === JobType.DYNAMIC && (
                        <div className="field col-12">
                            <label
                                htmlFor="externalApiEndpoint"
                                className="flex justify-content-between font-medium mb-2 block"
                            >
                                External API
                                <HelpTooltip
                                    overlay={
                                        <div className="p-2">
                                            The external API endpoint will be used to forward the
                                            mapped results.
                                        </div>
                                    }
                                />
                            </label>
                            <InputText
                                id="externalApiEndpoint"
                                name="externalApiEndpoint"
                                placeholder="https://api.example.com/endpoint"
                                value={form.externalApiEndpoint}
                                onChange={(e) => {
                                    setForm({
                                        ...form,
                                        externalApiEndpoint: e.target.value,
                                    });
                                }}
                                required
                            ></InputText>
                        </div>
                    )}

                    <div className="col-12 mt-3 mb-3">
                        <Button className="w-full" label="Submit" loading={isLoading}></Button>
                    </div>
                </div>
            </form>
        </>
    );
}
