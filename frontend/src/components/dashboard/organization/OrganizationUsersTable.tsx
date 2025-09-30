import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { PrimeIcons } from 'primereact/api';
import { OrganizationUser } from '@/types/models/Organization';
import { JSX } from 'react';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';

export type MembersTableProps = {
    members: OrganizationUser[];
    isLoading?: boolean;
    onDelete: (member: OrganizationUser) => void;
    onEdit: (member: OrganizationUser) => void;
};

/**
 * Displays a table of roles for an organization, allowing users to add, edit, and delete roles.
 *
 * @param {MembersTableProps} props - The component props
 *
 * @returns {JSX.Element} The rendered component.
 * */
export function OrganizationUsersTable({
    members,
    isLoading,
    onDelete,
    onEdit,
}: MembersTableProps): JSX.Element {
    const { user } = useAuth();

    return (
        <DataTable value={members} loading={isLoading} paginator rows={10}>
            <Column header="First Name" body={(rowData) => rowData.user.firstName} />
            <Column header="Last Name" body={(rowData) => rowData.user.lastName} />
            <Column header="Email" body={(rowData) => rowData.user.email} />
            <Column
                header="Role"
                body={(rowData) => (
                    <div className="flex gap-2">
                        <Tag key={rowData.role.name} value={rowData.role.name} />
                        <Button
                            icon={PrimeIcons.PENCIL}
                            onClick={() => onEdit(rowData)}
                            disabled={rowData.user.id === user?.id}
                            text
                        />
                    </div>
                )}
            />
            <Column
                body={(rowData) => (
                    <div className="flex gap-2 justify-content-end">
                        <Button
                            severity="danger"
                            label="Delete"
                            icon={PrimeIcons.TRASH}
                            onClick={() => onDelete(rowData)}
                            disabled={rowData.user.id === user?.id}
                            text
                        />
                    </div>
                )}
            />
        </DataTable>
    );
}
