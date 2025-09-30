import { useParams } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { getUserLogs } from '@/services/logService.ts';
import { ProgressSpinner } from 'primereact/progressspinner';
import React, { JSX } from 'react';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { Tag } from 'primereact/tag';
import {
    getLogLevelSeverity,
    getLogTypeSeverity,
    getLogActionSeverity,
} from '@/utils/adminUtils.ts';

/**
 * * A React component that displays user logs in a data table format.
 * @returns {JSX.Element} - A JSX element containing the user logs data table.
 */
export function UserLogPage(): JSX.Element {
    const { id } = useParams();

    const { data, isLoading, isError } = useQuery({
        queryKey: ['userLogs', id],
        queryFn: async () => await getUserLogs(Number(id)),
    });

    if (isError) {
        return (
            <div className="flex justify-content-center h-full align-items-center">
                <h2>Failed to load</h2>
            </div>
        );
    }

    console.log(data);
    return (
        <>
            <div className="flex justify-content-center mb-3">
                {data && data[0] && (
                    <h2>
                        User Logs for {data[0].user.firstName} {data[0].user.lastName}
                    </h2>
                )}
            </div>
            <DataTable
                value={data}
                paginator
                rows={25}
                rowsPerPageOptions={[10, 25, 50]}
                emptyMessage="No logs found"
                loading={isLoading}
                loadingIcon={<ProgressSpinner />}
            >
                <Column field="id" header="ID" sortable style={{ width: '5%' }}></Column>
                <Column
                    field="createdAt"
                    header="Time"
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
                    field="level"
                    header="Level"
                    sortable
                    style={{ width: '5%' }}
                    body={(rowData) => (
                        <Tag value={rowData.level} severity={getLogLevelSeverity(rowData.action)} />
                    )}
                />
                <Column
                    field="action"
                    header="Action"
                    sortable
                    style={{ width: '5%' }}
                    body={(rowData) => (
                        <Tag
                            value={rowData.action}
                            severity={getLogActionSeverity(rowData.action)}
                        />
                    )}
                />
                <Column
                    field="type"
                    header="Type"
                    sortable
                    style={{ width: '5%' }}
                    body={(rowData) => (
                        <Tag value={rowData.type} severity={getLogTypeSeverity(rowData.action)} />
                    )}
                />
                <Column field="message" header="Details" style={{ width: '50%' }}></Column>
            </DataTable>
        </>
    );
}

export default UserLogPage;
