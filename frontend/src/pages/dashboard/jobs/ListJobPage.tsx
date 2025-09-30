import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { Button } from 'primereact/button';
import { JSX, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useOrganization } from '@/hooks/context/OrganizationProvider/OrganizationContext';
import { JobList } from '@/components/dashboard/jobs/JobList.tsx';
import { PrimeIcons } from 'primereact/api';
import { Dialog } from 'primereact/dialog';
import {
    createJob,
    deleteJob,
    getOrganizationJobs,
    getUserJobs,
} from '@/services/mapping/jobService';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { CreateJobForm } from '@/components/dashboard/forms/CreateJobForm';
import { getOrganizationBlueprints, getUserBlueprints } from '@/services/mapping/blueprintService';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { MappingJob } from '@/types/models/Job';

/**
 * Represents the page component for listing mapping jobs.
 *
 * This component renders a dashboard header with the title "Mapping Jobs"
 * and a placeholder button labeled "TODO". It serves as the entry point
 * for displaying and managing mapping jobs within the dashboard.
 *
 * @returns {JSX.Element} The rendered JSX element for the ListJobPage.
 */
function ListJobPage(): JSX.Element {
    const { organization } = useOrganization();
    const { user } = useAuth();
    const [dialogVisible, setDialogVisible] = useState(false);

    const toast = useToast();

    const jobs = useQuery({
        queryKey: ['jobs', organization?.id ? organization.id : 'user'],
        queryFn: async () => {
            if (organization) {
                return await getOrganizationJobs(organization.id);
            } else {
                return await getUserJobs(user.id);
            }
        },
    });

    const blueprints = useQuery({
        enabled: dialogVisible,
        queryKey: ['blueprints', organization?.id ? organization.id : 'user'],
        queryFn: async () => {
            if (organization) {
                return await getOrganizationBlueprints(organization.id);
            } else {
                return await getUserBlueprints(user.id);
            }
        },
    });

    const createJobMutation = useMutation({
        mutationFn: createJob,
        onSuccess: async () => {
            await jobs.refetch();
            setDialogVisible(false);
            toast({
                severity: 'success',
                detail: 'Mapping Job Created',
            });
        },
    });

    const deleteJobMutation = useMutation({
        mutationFn: (job: MappingJob) => deleteJob(job.id),
        onSuccess: async () => {
            await jobs.refetch();
            toast({
                severity: 'success',
                detail: 'Mapping Job Deleted',
            });
        },
    });

    return (
        <>
            <DashboardHeader
                title="Mapping Jobs"
                end={
                    <Button
                        label="Create Mapping Job"
                        icon={PrimeIcons.PLUS}
                        onClick={() => setDialogVisible(true)}
                        loading={blueprints.isLoading}
                    />
                }
            />
            <JobList
                jobs={jobs.data}
                isLoading={jobs.isLoading}
                isError={jobs.isError}
                onDeleteClick={deleteJobMutation.mutateAsync}
            />
            {blueprints.data && (
                <Dialog
                    onHide={() => setDialogVisible(false)}
                    visible={dialogVisible}
                    header={'Create Mapping Job'}
                >
                    <CreateJobForm
                        blueprints={blueprints.data}
                        error={createJobMutation.error?.message}
                        isLoading={createJobMutation.isPending}
                        onSubmit={createJobMutation.mutateAsync}
                    />
                </Dialog>
            )}
        </>
    );
}

export default ListJobPage;
