import { OrganizationUsersTable } from '@/components/dashboard/organization/OrganizationUsersTable';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    blacklistFromOrganization,
    deleteFromOrganization,
    getOrganizationRoles,
    getOrganizationUsers,
    inviteOrganization,
    updateOrganizationUserRole,
} from '@/services/organizationService';
import { ApiError } from '@/services/client';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { Organization, OrganizationUser } from '@/types/models/Organization.ts';
import {
    EditMemberRoleRequest,
    InviteOrganizationRequest,
    InviteOrganizationResponse,
} from '@/types/schemas/Organization';
import { JSX, useState } from 'react';
import { useRouteLoaderData } from 'react-router';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { EditMemberForm } from '@/components/dashboard/organization/forms/EditMemberForm';
import { InviteOrganizationForm } from '@/components/dashboard/organization/forms/InviteOrganizationForm';
import { Dialog } from 'primereact/dialog';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';

/**
 * This component displays a table of members for the currently selected organization.
 * It uses the `useOrganization` hook to retrieve the selected organization from the global context.
 * The roles data for the organization is fetched using the `useQuery` hook from `@tanstack/react-query`.
 *
 * Behavior:
 * - If no organization is selected, or the data is still loading, or an error occurs,
 *   a loading message is displayed.
 * - Once the data is successfully fetched, the `MembersTable` component is rendered with the roles data.
 *
 * @returns {JSX.Element} The members table or a loading message.
 */
export function OrganizationUsersPage(): JSX.Element {
    const organization = useStickyLoaderData<Organization>(useRouteLoaderData('organization'));
    const toast = useToast();
    const queryClient = useQueryClient();

    const [addMemberVisible, setAddMemberVisible] = useState(false);
    const [editMemberVisible, setEditMemberVisible] = useState(false);
    const [deleteConfirmVisible, setDeleteConfirmVisible] = useState(false);
    const [selectedMember, setSelectedMember] = useState<OrganizationUser | null>(null);

    const roles = useQuery({
        queryKey: ['organizationRoles', organization.id],
        queryFn: () => getOrganizationRoles(organization.id),
    });

    const users = useQuery({
        queryKey: ['organization', organization.id, 'users'],
        queryFn: async () => await getOrganizationUsers(organization.id),
    });

    const deleteUser = useMutation<void, ApiError, { userId: number; orgId: number }>({
        mutationFn: ({ userId, orgId }) => deleteFromOrganization(orgId, userId),
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: ['organization', organization.id, 'users'],
            });
            toast({ severity: 'success', detail: 'User has been deleted' });
        },
        onError: (error) => {
            toast({ severity: 'error', detail: error.response.data.detail });
        },
    });

    const blacklistMutation = useMutation<void, ApiError, { userId: number; orgId: number }>({
        mutationFn: ({ userId, orgId }) => blacklistFromOrganization(orgId, userId),
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: ['organization', organization.id, 'users'],
            });
            toast({ severity: 'success', detail: 'User has been blacklisted' });
        },
        onError: (error) => {
            toast({ severity: 'error', detail: error.response.data.detail });
        },
    });

    const editMemberMutation = useMutation<OrganizationUser, ApiError, EditMemberRoleRequest>({
        mutationFn: (form) => {
            return updateOrganizationUserRole(organization.id, selectedMember.user.id, form);
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: ['organization', organization.id, 'users'],
            });
            await queryClient.invalidateQueries({
                queryKey: ['organization', organization.id, 'user'],
            });
            void toast({ severity: 'success', detail: 'Member has been updated' });
        },
        onError: (e) => {
            return e.response?.data.detail ?? e.message;
        },
    });

    const inviteMemberMutation = useMutation<
        InviteOrganizationResponse,
        ApiError,
        InviteOrganizationRequest
    >({
        mutationFn: (data) => inviteOrganization(organization.id, data),
        onSuccess: () => {
            toast({ severity: 'success', detail: 'Member has been invited' });
        },
        onError: (error) => {
            toast({ severity: 'error', detail: error.response.data.detail });
        },
    });

    const handleEditClick = (user: OrganizationUser) => {
        setSelectedMember(user);
        setEditMemberVisible(true);
    };

    const handleDeleteClick = (user: OrganizationUser) => {
        setSelectedMember(user);
        setDeleteConfirmVisible(true);
    };

    const handleBlacklist = async () => {
        if (selectedMember) {
            await blacklistMutation.mutateAsync({
                userId: selectedMember.user.id,
                orgId: organization.id,
            });
        }
        setDeleteConfirmVisible(false);
    };

    const handleDelete = async () => {
        if (selectedMember) {
            await deleteUser.mutateAsync({
                userId: selectedMember.user.id,
                orgId: organization.id,
            });
        }
        setDeleteConfirmVisible(false);
    };

    const handleInvite = async (data: InviteOrganizationRequest) => {
        await inviteMemberMutation.mutateAsync(data);
        setAddMemberVisible(false);
    };

    const handleEditMember = async (data: EditMemberRoleRequest) => {
        if (selectedMember) {
            await editMemberMutation.mutateAsync(data);
        }
        setEditMemberVisible(false);
    };

    return (
        <>
            <DashboardHeader
                title="Users"
                end={
                    <Button
                        label="Add Member"
                        icon={PrimeIcons.PLUS}
                        onClick={() => setAddMemberVisible(true)}
                    />
                }
            />

            <OrganizationUsersTable
                members={users.data}
                isLoading={users.isLoading}
                onDelete={handleDeleteClick}
                onEdit={handleEditClick}
            />

            <Dialog
                header="Confirm User Removal"
                visible={deleteConfirmVisible}
                footer={
                    <div className="flex gap-2 justify-content-end">
                        <Button
                            label="Cancel"
                            icon={PrimeIcons.TIMES}
                            className="p-button-text"
                            onClick={() => setDeleteConfirmVisible(false)}
                        />
                        <Button
                            label="Add to Blacklist"
                            icon={PrimeIcons.BAN}
                            className="p-button-warning"
                            onClick={handleBlacklist}
                        />
                        <Button
                            label="Delete"
                            icon={PrimeIcons.TRASH}
                            className="p-button-danger"
                            onClick={handleDelete}
                        />
                    </div>
                }
                onHide={() => setDeleteConfirmVisible(false)}
                modal
            >
                <div className="flex align-items-center gap-3 py-4">
                    <i className="pi pi-exclamation-triangle text-yellow-500 text-5xl" />
                    <div>
                        <h4 className="m-0 font-bold">Remove User</h4>
                        <p className="m-0 mt-2">
                            Are you sure you want to remove {selectedMember?.user.firstName}{' '}
                            {selectedMember?.user.lastName}?
                        </p>
                    </div>
                </div>
            </Dialog>

            <Dialog
                header={'Add New Member'}
                visible={addMemberVisible}
                onHide={() => setAddMemberVisible(false)}
            >
                <InviteOrganizationForm
                    error={inviteMemberMutation.error?.message}
                    isLoading={inviteMemberMutation.isPending}
                    onSubmit={handleInvite}
                    roles={roles.data}
                />
            </Dialog>

            <Dialog
                header={'Edit member'}
                visible={editMemberVisible}
                onHide={() => setEditMemberVisible(false)}
            >
                <EditMemberForm
                    onSubmit={handleEditMember}
                    isLoading={editMemberMutation.isPending}
                    error={editMemberMutation.error?.message}
                    roles={roles.data}
                    initial={selectedMember}
                />
            </Dialog>
        </>
    );
}

export default OrganizationUsersPage;
