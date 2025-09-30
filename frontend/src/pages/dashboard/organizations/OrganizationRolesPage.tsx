import { useMutation, useQuery } from '@tanstack/react-query';
import { OrganizationRole } from '@/types/models/User.ts';
import { ApiError } from '@/services/client';
import { RoleRequest } from '@/types/schemas/Organization';
import { AxiosError } from 'axios';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { JSX, useState } from 'react';
import { useRouteLoaderData } from 'react-router';
import { Organization } from '@/types/models/Organization';
import {
    createOrganizationRole,
    deleteOrganizationRole,
    editOrganizationRole,
    getOrganizationRoles,
    getOrganizationUser,
} from '@/services/organizationService';
import { OrganizationRolesTable } from '@/components/dashboard/organization/OrganizationRolesTable';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { Button } from 'primereact/button';
import { PrimeIcons } from 'primereact/api';
import { Dialog } from 'primereact/dialog';
import { RoleForm } from '@/components/dashboard/organization/forms/RoleForm';
import { Skeleton } from 'primereact/skeleton';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext.ts';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';

/**
 * Component: OrganizationRolesPage
 *
 * This component displays a table of roles for the currently selected organization.
 * It uses the `useOrganization` hook to retrieve the selected organization from the global context.
 * The roles data is fetched using the `useQuery` hook from `@tanstack/react-query`.
 *
 * Behavior:
 * - If no organization is selected, or the data is still loading, or an error occurs,
 *   a loading message is displayed.
 * - Once the data is successfully fetched, the `RolesTable` component is rendered with the roles data.
 *
 * @returns {JSX.Element} The roles table or a loading message.
 */
export function OrganizationRolesPage(): JSX.Element {
    const organization = useStickyLoaderData<Organization>(useRouteLoaderData('organization'));
    const { user } = useAuth();
    const toast = useToast();

    const [roleDialogVisible, setRoleDialogVisible] = useState(false);
    const [roleToEdit, setRoleToEdit] = useState<OrganizationRole | null>(null);

    const roles = useQuery({
        queryKey: ['organization', organization?.id, 'roles'],
        queryFn: () => getOrganizationRoles(organization.id),
    });

    const organizationUser = useQuery({
        queryKey: ['organization', organization?.id, 'user'],
        queryFn: () => getOrganizationUser(user.id, organization.id),
    });

    const createRoleMutation = useMutation<OrganizationRole, ApiError, RoleRequest>({
        mutationFn: (data) => createOrganizationRole(data, organization?.id),
        onSuccess: async (newRole: OrganizationRole) => {
            toast({ severity: 'success', detail: `${newRole.name} has been created!` });
            await roles.refetch();
        },
        onError: (e: AxiosError<{ detail: string }>) => {
            toast({ severity: 'error', detail: e.message });
        },
    });

    const editRoleMutation = useMutation<OrganizationRole, ApiError, RoleRequest>({
        mutationFn: (form) => editOrganizationRole(organization?.id, roleToEdit.id, form),
        onSuccess: async (editedRole: OrganizationRole) => {
            setRoleToEdit(null);
            await roles.refetch();
            toast({ severity: 'success', detail: `${editedRole.name} has been edited` });
        },
        onError: (e: AxiosError<{ detail: string }>) => {
            toast({ severity: 'error', detail: e.message });
        },
    });

    const deleteRoleMutation = useMutation<void, ApiError, { roleId: number; orgId: number }>({
        mutationFn: ({ roleId, orgId }) => deleteOrganizationRole(roleId, orgId),
        onSuccess: async () => {
            toast({ severity: 'success', detail: 'Role has been deleted' });
            await roles.refetch();
        },
        onError: () => {
            toast({ severity: 'error', detail: 'Error deleting role' });
        },
    });

    const handleRoleEdit = (role: OrganizationRole) => {
        setRoleToEdit(role);
        setRoleDialogVisible(true);
    };

    const handleRoleDelete = (role: OrganizationRole) => {
        deleteRoleMutation.mutate({ roleId: role.id, orgId: organization.id });
    };

    const handleRoleSave = async (formData: RoleRequest) => {
        if (roleToEdit) {
            const updatedRole = {
                ...formData,
                id: roleToEdit.id,
            };
            console.log(roleToEdit);
            await editRoleMutation.mutateAsync(updatedRole);
        } else {
            await createRoleMutation.mutateAsync(formData);
        }
        setRoleDialogVisible(false);
    };

    return (
        <>
            <DashboardHeader
                title="Organization Roles"
                end={
                    <Button
                        label="Add Role"
                        icon={PrimeIcons.PLUS}
                        onClick={() => setRoleDialogVisible(true)}
                    />
                }
            />

            {roles.isFetched && organizationUser.isFetched ? (
                <OrganizationRolesTable
                    roles={roles.data}
                    organizationUser={organizationUser.data}
                    onDeleteRole={handleRoleDelete}
                    onEditRole={handleRoleEdit}
                />
            ) : (
                <Skeleton height="5rem" />
            )}

            <Dialog
                header={roleToEdit ? 'Edit role' : 'Create role'}
                visible={roleDialogVisible}
                onHide={() => {
                    setRoleDialogVisible(false);
                    setRoleToEdit(null);
                }}
            >
                <RoleForm
                    onSubmit={handleRoleSave}
                    error={
                        roleToEdit
                            ? editRoleMutation.error?.message
                            : createRoleMutation.error?.message
                    }
                    isLoading={
                        roleToEdit ? editRoleMutation.isPending : createRoleMutation.isPending
                    }
                    initial={roleToEdit}
                />
            </Dialog>
        </>
    );
}

export default OrganizationRolesPage;
