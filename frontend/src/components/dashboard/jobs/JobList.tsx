import { JSX, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { DataList } from '@/components/shared/data/DataList';
import { SortOption } from '@/types/Filter';
import { Button } from 'primereact/button';
import { JobStatus, JobType, MappingJob } from '@/types/models/Job';
import { JobStatusTag } from '@/components/dashboard/jobs/JobStatusTag';
import { Tag } from 'primereact/tag';
import { PrimeIcons } from 'primereact/api';
import { jobTypeMeta } from '@/utils/jobUtils';
import { SourceMapping } from '@/types/models/Blueprint';
import { TreeNode, TreeNodeComponent } from '@/components/shared/data/tree/Tree';
import { HelpTooltip } from '@/components/shared/HelpTooltip';
import { dataTypeIcons } from '@/utils/fileUtils';

export type JobProps = {
    job: MappingJob;
    onDeleteClick?: (job: MappingJob) => Promise<unknown>;
};

/**
 * Represents a blueprint component that renders details of a blueprint.
 *
 * @param {JobProps} props - The props for the component.
 *
 * @returns A JSX element representing the blueprint.
 */
export function JobListItem({ job, onDeleteClick }: JobProps): JSX.Element {
    const navigate = useNavigate();

    const tree = useMemo<TreeNode>(() => {
        return {
            icon: 'pi pi-bullseye',
            children: job.inputDefinition.sourceMappings.map((mapping: SourceMapping) => ({
                icon: dataTypeIcons[mapping.fileType ?? 'JSON'],
                tooltip: mapping.name,
            })),
        };
    }, [job]);

    const jobTypeMetaData = jobTypeMeta[job.type];

    const openDefinition = () => {
        navigate(`/dashboard/jobs/${job.id}`, { replace: false });
    };

    return (
        <div
            className="grid align-items-center hover:surface-hover cursor-pointer"
            onClick={openDefinition}
        >
            <div className="col-12 md:col-4">
                <TreeNodeComponent node={tree} />
            </div>
            <div className="col-21 md:col-8 text-200">
                <div className="flex gap-2 justify-content-between align-items-center">
                    <h2 className="flex gap-3 align-items-center">
                        <span className="text-xs">{jobTypeMeta[job.type].label}</span>
                        <span>{job.name ?? `${job.inputDefinition.name} Mapping Job`}</span>
                        <HelpTooltip tooltip={jobTypeMetaData.description}></HelpTooltip>
                    </h2>

                    <div className="flex align-items-center gap-2">
                        <Button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDeleteClick(job);
                            }}
                            icon={PrimeIcons.TRASH}
                            tooltip="Delete Job"
                            severity="danger"
                            outlined
                        />
                    </div>
                </div>
                <div className="flex gap-1">
                    {job.executedAt && job.type === JobType.STATIC && (
                        <Tag severity="contrast">
                            Last ran on {new Date(job.executedAt).toLocaleDateString() || 'Never'}
                        </Tag>
                    )}
                    <Tag severity="contrast">
                        Created on {new Date(job.createdAt).toLocaleDateString()}
                    </Tag>
                </div>
                <div className="my-3 flex align-items-center gap-3 ">
                    {job.type === JobType.STATIC && (
                        <>
                            <JobStatusTag status={job.status} />
                            {job.status === JobStatus.SUCCESS && (
                                <a
                                    href={`/api/mappings/jobs/${job.id}/download`}
                                    download
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <Button
                                        icon={PrimeIcons.DOWNLOAD}
                                        label="Download Output File"
                                        text
                                    />
                                </a>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export type BlueprintListProps = {
    jobs?: MappingJob[];
    isLoading: boolean;
    isError: boolean;
    onDeleteClick?: (job: MappingJob) => Promise<unknown>;
};

/**
 * A React component that displays a list of mapping blueprints in a structured format.
 * It uses a callback to render each blueprint item and handles loading and error states.
 *
 * @param {BlueprintListProps} props - The props for the component.
 *
 * @returns {JSX.Element} The rendered BlueprintList component.
 *
 */
export function JobList({ jobs, isLoading, onDeleteClick }: BlueprintListProps): JSX.Element {
    const sortOptions = useMemo<SortOption<MappingJob>[]>(
        () => [
            { label: 'Creation Date', value: 'createdAt' },
            { label: 'Name', value: 'name' },
            { label: 'Execution Date', value: 'executedAt' },
        ],
        [],
    );

    return (
        <DataList<MappingJob>
            value={jobs}
            loading={isLoading}
            itemTemplate={(job) => <JobListItem job={job} onDeleteClick={onDeleteClick} />}
            sortOptions={sortOptions}
            rows={10}
            paginator
        />
    );
}
