import { DashboardHeader } from '@/layout/dashboard/DashboardHeader.tsx';
import { NavLink, useLoaderData, useRevalidator } from 'react-router';
import { Button } from 'primereact/button';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { Message } from 'primereact/message';
import { Fieldset } from 'primereact/fieldset';
import { JobStatus, MappingJob, MappingJobExecution } from '@/types/models/Job';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';
import { JobStatusTag } from '@/components/dashboard/jobs/JobStatusTag';
import { PrimeIcons } from 'primereact/api';
import { useMutation } from '@tanstack/react-query';
import { startJobExecution } from '@/services/mapping/jobService';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { useEffect, useMemo, useRef, useState } from 'react';
import { ProgressBar } from 'primereact/progressbar';
import { SourceMapping } from '@/types/models/Blueprint';
import { getDurationSeconds, jobStatusMeta } from '@/utils/jobUtils';
import { AxiosProgressEvent } from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFile } from '@fortawesome/free-solid-svg-icons';
import { Tag } from 'primereact/tag';

type UploadStatus = {
    uploading: boolean;
    progress: number;
};

/**
 * A React component that displays a mapping job preparation page.
 *
 * This page allows users to upload files for each source mapping defined in the job.
 * It tracks upload progress and validates that all required files are uploaded before
 * allowing the job to be started.
 *
 * @returns A JSX element containing the mapping job page content.
 */
export function StaticJobPage() {
    const job = useStickyLoaderData<MappingJob>(useLoaderData());
    const { revalidate } = useRevalidator();
    const toast = useToast();
    const pollingIntervalRef = useRef(null);

    // Track upload status for each source mapping
    const fileUploadRefs = useRef<Record<number, FileUpload | null>>({});
    const [uploadStatus, setUploadStatus] = useState<Record<number, UploadStatus>>({});

    // Find existing executions for each source mapping
    const executions = useMemo(() => {
        const executionMap: Record<number, MappingJobExecution> = {};

        job.executions.forEach((execution) => {
            executionMap[execution.sourceMapping.id] = execution;
        });

        return executionMap;
    }, [job.executions]);

    // Start job execution mutation
    const startExecutionMutation = useMutation<
        MappingJobExecution,
        Error,
        { sourceMappingId: number; file: File }
    >({
        mutationFn: async ({ sourceMappingId, file }) => {
            const formData = new FormData();
            formData.append('file', file);
            const execution = await startJobExecution(
                job.id,
                sourceMappingId,
                formData,
                (progress: AxiosProgressEvent) => {
                    setUploadStatus((prevStatus) => ({
                        ...prevStatus,
                        [sourceMappingId]: {
                            uploading: true,
                            progress: Math.round((progress.loaded / progress.total) * 100),
                        },
                    }));
                },
            );
            setUploadStatus((prevStatus) => ({
                ...prevStatus,
                [sourceMappingId]: {
                    uploading: false,
                    progress: 100,
                },
            }));
            await revalidate();
            return execution;
        },
        onSuccess: async (data: MappingJobExecution) => {
            const { sourceMapping } = data;
            await revalidate();
            toast({
                severity: 'success',
                summary: 'File uploaded successfully',
                detail: `Upload for ${job.inputDefinition.sourceMappings.find((m) => m.id === sourceMapping.id)?.name} completed`,
            });
        },
        onError: (error) => {
            toast({
                severity: 'error',
                summary: 'Upload failed',
                detail:
                    error.message || 'There was an error uploading your file. Please try again.',
            });
        },
    });

    // Setup polling when component mounts
    useEffect(() => {
        // Poll for job status updates
        const fetchJobDetails = async () => {
            try {
                await revalidate();

                // If job is complete or failed, stop polling
                if (job.status === JobStatus.SUCCESS || job.status === JobStatus.FAILED) {
                    clearInterval(pollingIntervalRef.current);
                }
            } catch (error) {
                console.error('Error polling job status:', error);
            }
        };

        // Start polling only if job is running
        if (job.status === JobStatus.RUNNING || job.status === JobStatus.PENDING) {
            pollingIntervalRef.current = setInterval(fetchJobDetails, 5000);
        }

        // Cleanup polling when component unmounts
        return () => {
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
            }
        };
    }, [job, revalidate]);

    // Artificially set selected files based on executions.
    useEffect(() => {
        Object.entries(fileUploadRefs.current).forEach(([mappingId, fileUploadref]) => {
            const execution = executions[mappingId];

            if (execution) {
                fileUploadref.setFiles([
                    {
                        name: execution.originalFileName,
                        size: execution.dataSizeBytes,
                        lastModified: 0,
                        type: null,
                        webkitRelativePath: null,
                        arrayBuffer: null,
                        bytes: null,
                        slice: null,
                        stream: null,
                        text: null,
                        objectURL: null,
                    },
                ]);
            }
        });
    });

    // Handle file upload
    const handleFileUpload = async (sourceMappingId: number, event: FileUploadHandlerEvent) => {
        const file = event.files[0];
        setUploadStatus({
            ...uploadStatus,
            [sourceMappingId]: {
                uploading: true,
                progress: 0,
            },
        });

        if (file) {
            await startExecutionMutation.mutateAsync({ sourceMappingId, file });
        }
    };

    return (
        <>
            <DashboardHeader
                title={job.name ?? `${job.inputDefinition.name} Static Mapping Job`}
                end={
                    <div className="flex items-center gap-2 align-items-center">
                        <NavLink to={`/dashboard/blueprints/${job.inputDefinition.blueprint.id}`}>
                            <Button
                                label={`Blueprint: ${job.inputDefinition.blueprint.name}`}
                                text
                            />
                        </NavLink>
                        <JobStatusTag status={job.status} />
                    </div>
                }
            />
            <div className="grid mt-4">
                {job.inputDefinition.sourceMappings?.map((mapping: SourceMapping) => {
                    const execution = executions[mapping.id];
                    const status = uploadStatus[mapping.id];
                    const hasExecution = !!execution;
                    const isProcessing = status?.uploading && status?.progress === 100;

                    return (
                        <div className="col-12 md:col-6" key={mapping.id}>
                            <Fieldset legend={mapping.name} key={mapping.id} toggleable>
                                <div className="flex flex-column gap-3">
                                    {!hasExecution && (
                                        <Message
                                            severity="info"
                                            text={`Upload files conforming to the source mapping's input schema to start the execution.`}
                                        />
                                    )}
                                    <div className="flex flex-column gap-2">
                                        {hasExecution && (
                                            <>
                                                <Message
                                                    className="mb-2"
                                                    severity={
                                                        jobStatusMeta[execution.status].severity
                                                    }
                                                    text={
                                                        jobStatusMeta[execution.status].description
                                                    }
                                                />

                                                {execution.status === JobStatus.FAILED && (
                                                    <Message
                                                        severity="error"
                                                        text={`Error: ${execution.errorMessage}`}
                                                    />
                                                )}

                                                <div className="flex gap-2 align-items-center my-3">
                                                    <Tag
                                                        value={
                                                            <>
                                                                <b>Attempts</b>:{' '}
                                                                {execution.attempts}
                                                            </>
                                                        }
                                                        severity="contrast"
                                                    />
                                                    {execution.completedAt &&
                                                        execution.completedAt && (
                                                            <Tag
                                                                value={
                                                                    <>
                                                                        <b>Last Attempt Duration</b>
                                                                        :{' '}
                                                                        {getDurationSeconds(
                                                                            new Date(
                                                                                execution.startedAt,
                                                                            ),
                                                                            new Date(
                                                                                execution.completedAt,
                                                                            ),
                                                                        )}
                                                                        s
                                                                    </>
                                                                }
                                                                severity="contrast"
                                                            />
                                                        )}
                                                </div>

                                                {execution.status === JobStatus.RUNNING && (
                                                    <ProgressBar
                                                        mode="indeterminate"
                                                        style={{ height: '6px' }}
                                                        className="my-3"
                                                    />
                                                )}
                                            </>
                                        )}

                                        <FileUpload
                                            className="my-3"
                                            ref={(el) => {
                                                fileUploadRefs.current[mapping.id] = el;
                                            }}
                                            accept={mapping.fileType}
                                            chooseLabel="Select File"
                                            uploadLabel="Upload"
                                            customUpload={true}
                                            auto={true}
                                            uploadHandler={(e) => handleFileUpload(mapping.id, e)}
                                            progressBarTemplate={
                                                status && (
                                                    <ProgressBar
                                                        showValue={true}
                                                        style={{ height: '18px' }}
                                                        value={status?.progress}
                                                    />
                                                )
                                            }
                                            emptyTemplate={
                                                <div className="text-center text-300">
                                                    No file selected.
                                                </div>
                                            }
                                            itemTemplate={(file: File, options) => (
                                                <div className="flex align-items-center justify-content-between gap-2">
                                                    <div className="flex align-items-center gap-2">
                                                        <FontAwesomeIcon icon={faFile} />
                                                        {options.fileNameElement}
                                                        <Tag severity="contrast">
                                                            {options.sizeElement}
                                                        </Tag>
                                                    </div>
                                                    {isProcessing && (
                                                        <JobStatusTag
                                                            status={JobStatus.RUNNING}
                                                            text={'Converting'}
                                                        />
                                                    )}
                                                </div>
                                            )}
                                        />

                                        <div className="flex justify-content-end gap-2">
                                            {execution?.status === JobStatus.SUCCESS && (
                                                <a
                                                    href={`/api/mappings/jobs/${job.id}/execution/${execution.id}/download`}
                                                    download="result.json"
                                                >
                                                    <Button
                                                        label="Download Result"
                                                        icon={PrimeIcons.DOWNLOAD}
                                                    />
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </Fieldset>
                        </div>
                    );
                })}
            </div>
        </>
    );
}

export default StaticJobPage;
