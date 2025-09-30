import { JobStatusTag } from '@/components/dashboard/jobs/JobStatusTag';
import { HelpTooltip } from '@/components/shared/HelpTooltip';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { ApiError } from '@/services/client';
import { dynamicJobExecution, updateJob } from '@/services/mapping/jobService';
import { SourceMapping } from '@/types/models/Blueprint';
import { JobStatus, MappingJob, MappingJobExecution } from '@/types/models/Job';
import { formatBytes, formatDateTime } from '@/utils/jobUtils';
import { useMutation } from '@tanstack/react-query';
import { JSONSchemaFaker } from 'json-schema-faker';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { Dialog } from 'primereact/dialog';
import { Fieldset } from 'primereact/fieldset';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Message } from 'primereact/message';
import { Tooltip } from 'primereact/tooltip';
import { JSX, useState } from 'react';
import { NavLink, useLoaderData, useRevalidator } from 'react-router';

/**
 * A React component that displays a dynamic mapping job page.
 *
 * This page provides information about the mapping job, including its name,
 * associated blueprint, and status. It is part of the dashboard interface.
 *
 * @returns {JSX.Element} The rendered JSX element for the DynamicJobPage.
 */
export function DynamicJobPage(): JSX.Element {
    const toast = useToast();
    const job = useStickyLoaderData<MappingJob>(useLoaderData());
    const { revalidate } = useRevalidator();

    const [form, setForm] = useState(job);

    const [showEditDialog, setShowEditDialog] = useState(false);

    const updateJobMutation = useMutation({
        mutationFn: () => updateJob(job.id, form),
        onSuccess: async () => {
            await revalidate();
            setShowEditDialog(false);
            toast({
                severity: 'success',
                summary: 'Success',
                detail: 'Job updated successfully',
            });
        },
    });

    JSONSchemaFaker.option({
        minItems: 1,
        maxItems: 1,
        useExamplesValue: true,
        useDefaultValue: true,
    });

    const SourceMappingCard = ({ mapping }: { mapping: SourceMapping }) => {
        const endpoint = `${window.location.origin}/api/mappings/jobs/dynamic/${job.uuid}/${mapping.id}`;

        const [body, setBody] = useState(
            JSON.stringify(JSONSchemaFaker.generate(mapping.inputJsonSchema), null, 4),
        );

        const [lastExecution, setLastExecution] = useState<object | null>(null);

        const executeMutation = useMutation({
            mutationFn: (payload: string) =>
                dynamicJobExecution(job.uuid, mapping.id, JSON.parse(payload), false),

            onSuccess: (execution) => {
                setLastExecution(execution);
                toast({
                    severity: 'success',
                    summary: 'Execution started',
                    detail: `The dynamic mapping job has been started successfully.`,
                });
            },

            onError: (err: ApiError) =>
                toast({ severity: 'error', summary: 'Error', detail: err.message }),
        });

        return (
            <div className="col-12 md:col-6">
                <Card title={mapping.name}>
                    {/* URL input with prepend icon + copy button */}
                    <div className="p-inputgroup w-full">
                        <span className="p-inputgroup-addon">
                            <i className="pi pi-link" />
                        </span>

                        <InputText value={endpoint} className="w-full" disabled />

                        <Button
                            icon={PrimeIcons.COPY}
                            tooltip="Copy URL"
                            tooltipOptions={{ position: 'top' }}
                            onClick={() => {
                                navigator.clipboard.writeText(endpoint);
                                toast({
                                    severity: 'success',
                                    summary: 'Copied!',
                                    detail: 'Endpoint copied to clipboard',
                                });
                            }}
                        />
                    </div>

                    <Fieldset className="mt-5" legend="Try it out" toggleable>
                        {executeMutation.isError && (
                            <Message
                                severity="error"
                                text={(executeMutation.error as Error).message}
                                className="mb-3"
                            />
                        )}

                        {executeMutation.isSuccess && (
                            <Message
                                severity="success"
                                text="Execution started successfully"
                                className="mb-3"
                            />
                        )}

                        <label>
                            <div className="w-full mb-3 font-bold">JSON Body:</div>
                            <InputTextarea
                                value={body}
                                onChange={(e) => setBody(e.target.value)}
                                rows={10}
                                className="w-full mb-5"
                                autoResize
                            />
                            {lastExecution && (
                                <>
                                    <div className="w-full mb-3 font-bold">Result</div>
                                    <InputTextarea
                                        value={JSON.stringify(lastExecution, null, 4)}
                                        rows={10}
                                        className="w-full mb-5"
                                        autoResize
                                    />
                                </>
                            )}
                        </label>

                        <Button
                            label="Try API"
                            icon={PrimeIcons.PLAY}
                            className="w-full"
                            loading={executeMutation.isPending}
                            onClick={() => executeMutation.mutate(body)}
                        />
                    </Fieldset>
                </Card>
            </div>
        );
    };

    const statusBody = (exec: MappingJobExecution): JSX.Element => {
        const id = `exec-status-${exec.id}`;
        const showTooltip = exec.status === JobStatus.FAILED || exec.errorMessage;
        return (
            <>
                <span id={id}>
                    <JobStatusTag status={exec.status} />
                </span>
                {showTooltip && (
                    <Tooltip target={`#${id}`} content={exec.errorMessage ?? 'Execution failed'} />
                )}
            </>
        );
    };

    const dataSizeBody = (exec: MappingJobExecution) => formatBytes(exec.dataSizeBytes) + ' B';

    return (
        <>
            <Dialog
                header="Update External API Endpoint"
                visible={showEditDialog}
                onHide={() => setShowEditDialog(false)}
            >
                {updateJobMutation.isError && (
                    <Message
                        severity="error"
                        text={updateJobMutation.error.message}
                        className="mb-3"
                    />
                )}

                <form action={() => updateJobMutation.mutate()}>
                    <div className="formgrid grid">
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

                        <div className="col-12 mt-3 mb-3">
                            <Button
                                className="w-full"
                                label="Submit"
                                loading={updateJobMutation.isPending}
                            ></Button>
                        </div>
                    </div>
                </form>
            </Dialog>
            <DashboardHeader
                title={job.name ?? `${job.inputDefinition.name} Dynamic Mapping Job`}
                end={
                    <div className="flex items-center gap-2 align-items-center">
                        <NavLink to={`/dashboard/blueprints/${job.inputDefinition.blueprint.id}`}>
                            <Button
                                label={`Blueprint: ${job.inputDefinition.blueprint.name}`}
                                text
                            />
                        </NavLink>
                        <Button
                            icon={PrimeIcons.PENCIL}
                            tooltip="Edit Dynamic Job"
                            tooltipOptions={{ position: 'top' }}
                            onClick={(e) => {
                                e.stopPropagation();
                                setShowEditDialog(true);
                            }}
                        />
                    </div>
                }
            />
            <div className="grid mb-7">
                {job.inputDefinition.sourceMappings.map((mapping: SourceMapping) => (
                    <SourceMappingCard key={mapping.id} mapping={mapping} />
                ))}
            </div>
            <DataTable
                value={job.executions}
                paginator
                rows={10}
                rowsPerPageOptions={[10, 25, 50]}
                sortMode="multiple"
                removableSort
            >
                <Column
                    field="dataSizeBytes"
                    header="Data Size (bytes)"
                    body={dataSizeBody}
                    sortable
                />
                <Column field="status" header="Status" body={statusBody} sortable />
                <Column
                    field="createdAt"
                    header="Created"
                    body={(r) => formatDateTime(r.createdAt)}
                    sortable
                />
                <Column
                    field="completedAt"
                    header="Completed"
                    body={(r) => formatDateTime(r.completedAt)}
                    sortable
                />
            </DataTable>
        </>
    );
}
