import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { PendingUser } from '@/types/models/Organization';
import { JSX } from 'react';

export type PendingInvitationsTableProps = {
    pendingUsers: PendingUser[];
    isLoading: boolean;
};

/**
 * Displays a table of roles for an organization, allowing users to add, edit, and delete roles.
 *
 * @param {PendingInvitationsTableProps} props - The component props
 *
 * @returns {JSX.Element} The rendered component.
 * */
export function PendingInvitationsTable({
    isLoading,
    pendingUsers,
}: PendingInvitationsTableProps): JSX.Element {
    return (
        <>
            <DataTable value={pendingUsers} paginator rows={10} loading={isLoading}>
                <Column field="email" header="Email" sortable />
                <Column
                    field="expiresAt"
                    header="Expiration Date"
                    sortable
                    body={(rowData) => {
                        const date = new Date(rowData.expiresAt);
                        return `${date.toLocaleTimeString('en-GB', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false,
                        })} ${date.toLocaleDateString('en-GB', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                        })}`;
                    }}
                />
            </DataTable>
            <div className="flex flex-grow" />
        </>
    );
}
