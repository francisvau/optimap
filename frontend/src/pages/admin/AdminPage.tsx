import React, { useEffect, useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Card } from 'primereact/card';
import { ProgressSpinner } from 'primereact/progressspinner';
import { useQuery } from '@tanstack/react-query';
import { getAllLogs, getLogsLevel } from '@/services/logService.ts';
import { getSystemMetrics } from '@/services/metricService.ts';
import { Log, logLevel } from '@/types/models/Log.ts';
import { useNavigate } from 'react-router';
import { Tag } from 'primereact/tag';
import { getLogLevelSeverity } from '@/utils/adminUtils.ts';

/**
 * A React component that displays a verification page for user accounts.
 *
 * This page is intended to inform the user that a verification email has been sent
 * to their email address and provides instructions on what to do if they do not
 * receive the email. If the `email` state is not available in the location object,
 * the user is redirected to the login page.
 *
 * @returns A JSX element containing the verification page content.
 */
export function AdminPage() {
    const [activeIndex, setActiveIndex] = useState<number>(0);
    const [userLogs, setUserLogs] = useState<Log[]>([]);
    const [organizationLogs, setOrganizationLogs] = useState<Log[]>([]);
    const navigate = useNavigate();
    const {
        data: allLogs,
        isLoading: isLoadingLogs,
        isError: isErrorLogs,
        isSuccess,
    } = useQuery({
        queryKey: ['allLogs'],
        queryFn: async () => await getAllLogs(),
    });

    const {
        data: systemStats,
        isLoading: isLoadingStats,
        isError: isErrorStats,
    } = useQuery({
        queryKey: ['systemStats'],
        queryFn: async () => await getSystemMetrics(),
    });

    const {
        data: urgentLogs,
        isLoading: isLoadingUrgentLogs,
        isError: isErrorUrgentLogs,
    } = useQuery({
        queryKey: ['urgentLogs'],
        queryFn: async () => await getLogsLevel(logLevel.CRITICAL),
    });

    useEffect(() => {
        if (isSuccess && allLogs.length > 0) {
            setUserLogs(allLogs.filter((log) => log.user && !log.organization));
            setOrganizationLogs(allLogs.filter((log) => log.organization));
        }
    }, [isSuccess, allLogs]);

    if (isErrorStats || isErrorLogs || isErrorUrgentLogs) {
        return (
            <div className="flex justify-content-center h-full align-items-center">
                <h2>Failed to load</h2>
            </div>
        );
    }

    if (isLoadingStats) {
        return (
            <div className="flex justify-content-center">
                <ProgressSpinner />
            </div>
        );
    }

    return (
        <div className="grid">
            <div className="col-12 pb-7">
                <div className="flex justify-content-between flex-wrap mx-8">
                    <Card
                        header={
                            <h2
                                style={{
                                    textAlign: 'center',
                                    fontWeight: 'bold',
                                    marginBottom: '0',
                                }}
                            >
                                Active Users
                            </h2>
                        }
                        className="m-2"
                        style={{ width: '13rem', height: '9rem' }}
                    >
                        <h2 className="text-center text-primary">{systemStats.totalUsers}</h2>
                    </Card>
                    <Card
                        header={
                            <h2
                                style={{
                                    textAlign: 'center',
                                    fontWeight: 'bold',
                                    marginBottom: '0',
                                }}
                            >
                                Running Jobs
                            </h2>
                        }
                        className="m-2"
                        style={{ width: '13rem', height: '9rem' }}
                    >
                        <h2 className="text-center text-primary">
                            {systemStats.activeMappingJobs}
                        </h2>
                    </Card>
                    <Card
                        header={
                            <h2
                                style={{
                                    textAlign: 'center',
                                    fontWeight: 'bold',
                                    marginBottom: '0',
                                }}
                            >
                                Organizations
                            </h2>
                        }
                        className="m-2"
                        style={{ width: '13rem', height: '9rem' }}
                    >
                        <h2 className="text-center text-primary">
                            {systemStats.totalOrganizations}
                        </h2>
                    </Card>
                </div>
            </div>

            <div className="col-12">
                <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
                    <TabPanel header="Urgent Logs" leftIcon="pi pi-exclamation-triangle mr-2">
                        <div className="grid">
                            <div className="col-12">
                                <h3>Urgent Activity Logs</h3>
                                <DataTable
                                    value={urgentLogs}
                                    paginator
                                    rows={10}
                                    rowsPerPageOptions={[10, 25, 50]}
                                    emptyMessage="No urgent logs"
                                    loading={isLoadingUrgentLogs}
                                    loadingIcon={<ProgressSpinner />}
                                >
                                    <Column
                                        field="id"
                                        header="ID"
                                        sortable
                                        style={{ width: '5%' }}
                                    ></Column>
                                    <Column
                                        field="user.name"
                                        header="User"
                                        sortable
                                        style={{ width: '20%' }}
                                    ></Column>
                                    <Column
                                        field="organization.name"
                                        header="Organization"
                                        sortable
                                        style={{ width: '20%' }}
                                    ></Column>
                                    <Column
                                        field="action"
                                        header="Action"
                                        sortable
                                        style={{ width: '5%' }}
                                    ></Column>
                                    <Column
                                        field="type"
                                        header="type"
                                        sortable
                                        style={{ width: '5%' }}
                                    />
                                    <Column
                                        field="level"
                                        header="Level"
                                        sortable
                                        style={{ width: '5%' }}
                                        body={(rowData) => (
                                            <Tag
                                                value={rowData.level}
                                                severity={getLogLevelSeverity(rowData.action)}
                                            />
                                        )}
                                    />
                                    <Column
                                        field="createdAt"
                                        header="Created At"
                                        sortable
                                        body={(rowData) => {
                                            const date = new Date(rowData.createdAt);
                                            date.setHours(date.getHours() + 2);
                                            return date.toLocaleString('nl-BE', {
                                                day: '2-digit',
                                                month: '2-digit',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                second: '2-digit',
                                            });
                                        }}
                                        style={{ width: '15%' }}
                                    />
                                    <Column
                                        field="message"
                                        header="Details"
                                        style={{ width: '50%' }}
                                    ></Column>
                                </DataTable>
                            </div>
                        </div>
                    </TabPanel>
                    <TabPanel header="User Logs" leftIcon="pi pi-user mr-2">
                        <div className="grid">
                            <div className="col-12">
                                <h3>User Activity Logs</h3>
                                <DataTable
                                    value={userLogs}
                                    paginator
                                    rows={10}
                                    rowsPerPageOptions={[10, 25, 50]}
                                    emptyMessage="No logs found"
                                    loading={isLoadingLogs}
                                    loadingIcon={<ProgressSpinner />}
                                    selectionMode="single"
                                    onRowClick={(e) => {
                                        const log = e.data;
                                        navigate(`/admin/logs/users/${log.user.id}`);
                                    }}
                                >
                                    <Column
                                        field="id"
                                        header="ID"
                                        sortable
                                        style={{ width: '5%' }}
                                    ></Column>
                                    <Column
                                        header="User"
                                        sortable
                                        style={{ width: '20%' }}
                                        body={(rowData) =>
                                            `${rowData.user.firstName} ${rowData.user.lastName}`
                                        }
                                    />
                                    <Column
                                        field="action"
                                        header="Action"
                                        sortable
                                        style={{ width: '5%' }}
                                    />
                                    <Column
                                        field="type"
                                        header="type"
                                        sortable
                                        style={{ width: '5%' }}
                                    />
                                    <Column
                                        field="createdAt"
                                        header="Created At"
                                        sortable
                                        body={(rowData) => {
                                            const date = new Date(rowData.createdAt);
                                            date.setHours(date.getHours() + 2);
                                            return date.toLocaleString('nl-BE', {
                                                day: '2-digit',
                                                month: '2-digit',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                second: '2-digit',
                                            });
                                        }}
                                    />
                                    <Column
                                        field="message"
                                        header="Details"
                                        style={{ width: '50%' }}
                                    ></Column>
                                </DataTable>
                            </div>
                        </div>
                    </TabPanel>
                    <TabPanel header="Organization Logs" leftIcon="pi pi-building mr-2">
                        <div className="grid">
                            <div className="col-12">
                                <h3>Organization Activity Logs</h3>
                                <DataTable
                                    value={organizationLogs}
                                    paginator
                                    rows={10}
                                    rowsPerPageOptions={[10, 25, 50]}
                                    emptyMessage="No logs found"
                                    loading={isLoadingLogs}
                                    loadingIcon={<ProgressSpinner />}
                                    selectionMode="single"
                                    onRowClick={(e) => {
                                        const log = e.data;
                                        navigate(
                                            `/admin/logs/organizations/${log.organization.id}`,
                                        );
                                    }}
                                >
                                    <Column
                                        field="id"
                                        header="ID"
                                        sortable
                                        style={{ width: '5%' }}
                                    ></Column>
                                    <Column
                                        field="organization.name"
                                        header="Organization"
                                        sortable
                                        style={{ width: '20%' }}
                                    ></Column>
                                    <Column
                                        field="action"
                                        header="Action"
                                        sortable
                                        style={{ width: '5%' }}
                                    ></Column>
                                    <Column
                                        field="type"
                                        header="type"
                                        sortable
                                        style={{ width: '5%' }}
                                    />
                                    <Column
                                        field="createdAt"
                                        header="Created At"
                                        sortable
                                        body={(rowData) => {
                                            const date = new Date(rowData.createdAt);
                                            date.setHours(date.getHours() + 2);
                                            return date.toLocaleString('nl-BE', {
                                                day: '2-digit',
                                                month: '2-digit',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                second: '2-digit',
                                            });
                                        }}
                                    />
                                    <Column
                                        field="message"
                                        header="Details"
                                        style={{ width: '50%' }}
                                    ></Column>
                                </DataTable>
                            </div>
                        </div>
                    </TabPanel>
                </TabView>
            </div>
        </div>
    );
}

export default AdminPage;
