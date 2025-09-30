import { JobStatus } from '@/types/models/Job';
import { jobStatusMeta } from '@/utils/jobUtils';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { Tag } from 'primereact/tag';
import { JSX, useMemo } from 'react';
import clsx from 'clsx';

export type JobStatusTagProps = {
    status: JobStatus;
    text?: string;
    small?: boolean;
};

/**
 * A React component that renders a status tag for a job, displaying an icon and label
 * based on the provided job status.
 *
 * @param {JobStatus} status - The current status of the job, which determines the tag's appearance
 *                 and content. This should be a value of the `JobStatus` enum.
 * @returns A JSX element representing the job status tag, styled with a severity level
 *          and including an icon and label.
 */
export function JobStatusTag({ status, text, small = false }: JobStatusTagProps): JSX.Element {
    const meta = useMemo(() => jobStatusMeta[status], [status]);

    const clsn = {
        ['pi pi-spin']: status === JobStatus.RUNNING,
    };

    return (
        <Tag
            severity={meta.tagSeverity}
            value={
                <div className={clsx('flex align-items-center gap-2', { 'text-xs': small })}>
                    <FontAwesomeIcon className={clsx(clsn)} icon={meta.icon} /> {text ?? meta.label}
                </div>
            }
        />
    );
}
