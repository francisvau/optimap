import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { OrganizationRole, Permissions } from '@/types/models/User.ts';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';
import { JSX } from 'react';
import { Tooltip } from 'primereact/tooltip';
import { formatPermission } from '@/utils/permissionUtils';
import { OrganizationUser } from '@/types/models/Organization.ts';
import { PrimeIcons } from 'primereact/api';

export type RolesTableProps = {
    roles: OrganizationRole[];
    organizationUser: OrganizationUser;
    onDeleteRole: (role: OrganizationRole) => void;
    onEditRole: (role: OrganizationRole) => void;
};

/**
 * Displays a table of roles for an organization, allowing users to add, edit, and delete roles.
 *
 * @param {RolesTableProps} props - The component props
 *
 * @returns {JSX.Element} The rendered component.
 * */
export function OrganizationRolesTable({
    roles,
    organizationUser,
    onDeleteRole,
    onEditRole,
}: RolesTableProps): JSX.Element {
    /**
     * function to check if the current user can edit or delete a role
     * @param targetRole
     * @param currentUser
     * @returns {boolean}
     */
    function editOrDeleteRole(targetRole: OrganizationRole, currentUser: OrganizationUser | null) {
        if (!currentUser) {
            return false;
        }
        const isAdminRole = targetRole.name.toLowerCase() === 'admin';
        const isCurrentUserAdmin = currentUser.role.name.toLowerCase() === 'admin';
        const hasManageRolesPermission = currentUser.role.permissions.includes(
            Permissions.MANAGE_ROLES,
        );

        if (isAdminRole) {
            return false;
        }

        if (targetRole.id === currentUser.role.id) {
            return false;
        }

        return isCurrentUserAdmin || hasManageRolesPermission;
    }

    return (
        <>
            <DataTable value={roles} paginator rows={10} className="mt-2 w-full flex-grow-1">
                <Column field="name" header="Name" sortable />
                <Column
                    field="permissions"
                    header="Permissions"
                    body={(rowData) => (
                        <div className="flex flex-wrap gap-2">
                            {rowData.permissions.map((perm: Permissions) => (
                                <Tag
                                    className="text-sm"
                                    key={perm}
                                    value={formatPermission(perm)}
                                />
                            ))}
                        </div>
                    )}
                />
                <Column
                    body={(rowData: OrganizationRole) => {
                        const isEditable = editOrDeleteRole(rowData, organizationUser);
                        const tooltipText = "You can't modify this role";

                        return (
                            <div className="flex gap-2 justify-content-end">
                                {!isEditable && (
                                    <Tooltip
                                        target={`.disabled-${rowData.id}`}
                                        position={'top'}
                                        content={tooltipText}
                                    />
                                )}
                                <span className={`disabled-${rowData.id}`}>
                                    <Button
                                        label="Edit"
                                        icon={PrimeIcons.PENCIL}
                                        text
                                        onClick={() => onEditRole(rowData)}
                                        disabled={!isEditable}
                                    />
                                </span>
                                <span className={`disabled-${rowData.id}`}>
                                    <Button
                                        label="Delete"
                                        icon={PrimeIcons.TRASH}
                                        text
                                        severity={'danger'}
                                        onClick={() => onDeleteRole(rowData)}
                                        disabled={!isEditable}
                                    />
                                </span>
                            </div>
                        );
                    }}
                />
            </DataTable>
        </>
    );
}
