import { JSX } from 'react';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { Button } from 'primereact/button';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import { MappingJob } from '@/types/models/Job';
import { JobStatusTag } from '@/components/dashboard/jobs/JobStatusTag';
import { getUserJobs } from '@/services/mapping/jobService';

/**
 * Represents the Dashboard component.
 * This component serves as the main dashboard page of the application.
 *
 * @returns {JSX.Element} The rendered Dashboard component.
 */
export function DashboardPage(): JSX.Element {
    const { user } = useAuth();
    const navigate = useNavigate();

    const { data: jobsData, isLoading: jobsLoading } = useQuery({
        queryKey: ['userJobs', user?.id],
        enabled: !!user?.id,
        queryFn: () => getUserJobs(user.id),
    });

    const dateTemplate = (rowData: MappingJob) => {
        return new Date(rowData.createdAt).toLocaleDateString();
    };

    const actionTemplate = (rowData: MappingJob) => (
        <Button
            icon="pi pi-eye"
            className="p-button-rounded p-button-text"
            onClick={() => navigate(`/dashboard/jobs/${rowData.id}`)}
            tooltip="View Job"
            tooltipOptions={{ position: 'bottom' }}
        />
    );

    const statusTemplate = (job: MappingJob) => {
        return <JobStatusTag status={job.status} />;
    };

    return (
        <>
            <DashboardHeader title={`Welcome Back, ${user.firstName}!`} />
            <div className="col-12">
                <Card
                    title="Recent Mapping Jobs"
                    className="shadow-2"
                    subTitle={`${jobsData?.length || 0} most recent jobs`}
                >
                    <DataTable
                        value={jobsData}
                        loading={jobsLoading}
                        rowHover
                        paginator
                        rows={5}
                        emptyMessage="No recent jobs"
                    >
                        <Column field="inputDefinition.name" header="Input Definition" sortable />
                        <Column field="createdAt" header="Created" body={dateTemplate} sortable />
                        <Column field="status" header="Status" body={statusTemplate} sortable />
                        <Column
                            header="Actions"
                            body={actionTemplate}
                            style={{ width: '8em', textAlign: 'center' }}
                        />
                    </DataTable>
                    <div className="flex justify-content-end mt-3">
                        <Button label="View All Jobs" onClick={() => navigate('/dashboard/jobs')} />
                    </div>
                </Card>
            </div>
        </>
    );
}

export default DashboardPage;
