import { StaticJobPage } from '@/pages/dashboard/jobs/StaticJobPage';
import { DynamicJobPage } from '@/pages/dashboard/jobs/DynamicJobPage';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';
import { MappingJob, JobType } from '@/types/models/Job';
import { useLoaderData } from 'react-router';

/**
 * A React component that displays a mapping job preparation page.
 *
 * This page allows users to upload files for each source mapping defined in the job.
 * It tracks upload progress and validates that all required files are uploaded before
 * allowing the job to be started.
 *
 * @returns A JSX element containing the mapping job page content.
 */
export function JobPage() {
    const job = useStickyLoaderData<MappingJob>(useLoaderData());

    return job.type === JobType.STATIC ? <StaticJobPage /> : <DynamicJobPage />;
}

export default JobPage;
