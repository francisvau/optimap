import { JobStatus, JobType } from '@/types/models/Job';
import {
    faBug,
    faCheck,
    faMapSigns,
    faPause,
    faSpinner,
    faTimeline,
    IconDefinition,
} from '@fortawesome/free-solid-svg-icons';
import { MessageProps } from 'primereact/message';
import { TagProps } from 'primereact/tag';

export type JobStatusMeta = {
    severity: MessageProps['severity'];
    tagSeverity: TagProps['severity'];
    label: string;
    icon: IconDefinition;
    description: string;
};

export type JobTypeMeta = {
    label: string;
    icon: IconDefinition;
    description: string;
};

export const jobTypeMeta: Record<JobType, JobTypeMeta> = {
    STATIC: {
        label: 'Static',
        icon: faMapSigns,
        description:
            'Static jobs get their input from files and provide the mapped result as output JSON files.',
    },
    DYNAMIC: {
        label: 'Dynamic',
        icon: faTimeline,
        description:
            'Dynamic jobs get their input dynamically through an API call and forward the mapped result to a target API.',
    },
};

export const jobStatusMeta: Record<JobStatus, JobStatusMeta> = {
    SUCCESS: {
        severity: 'success',
        tagSeverity: 'success',
        label: 'Success',
        icon: faCheck,
        description: 'Processing finished successfully!',
    },
    FAILED: {
        severity: 'error',
        tagSeverity: 'danger',
        label: 'Failed',
        icon: faBug,
        description: 'Processing failed',
    },
    PENDING: {
        severity: 'warn',
        tagSeverity: 'warning',
        label: 'Pending',
        icon: faPause,
        description: 'Waiting for execution',
    },
    RUNNING: {
        severity: 'info',
        tagSeverity: 'info',
        label: 'Running',
        icon: faSpinner,
        description: 'Execution in progress...',
    },
};

/**
 * When a job is in the PENDING or FAILED state, it can be retried.
 *
 * @param status - The status of the job
 * @returns true if the job can be retried, false otherwise
 */
export function isUploadStatus(status: JobStatus): boolean {
    return status === JobStatus.PENDING || status === JobStatus.FAILED;
}

/**
 * Calculates the duration in seconds between two Date objects.
 *
 * @param start - The start date and time.
 * @param end - The end date and time.
 * @returns The absolute difference in seconds between the two dates as a string.
 */
export function getDurationSeconds(start: Date, end: Date): string {
    const diff = Math.abs(end.getTime() - start.getTime()) / 1000;
    return diff.toFixed(0);
}

export const formatDateTime = (value: Date | null) =>
    value ? new Date(value).toLocaleString() : '—';

export const formatBytes = (bytes: number) =>
    bytes.toLocaleString(undefined, { maximumFractionDigits: 0 });
