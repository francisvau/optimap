import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { blockUser, getUsers, unblockUser } from '@/services/userService';
import { User } from '@/types/models/User.ts';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { JSX, useState } from 'react';
import { ApiError } from '@/services/client';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';

/**
 * ForgotPasswordForm component
 *
 * This component renders a form for users to request a password reset link.
 *
 *
 * @returns {JSX.Element} The rendered ForgotPasswordForm component
 */
export function AdminUsersPage(): JSX.Element {
    const [confirmDialogVisible, setConfirmDialogVisible] = useState(false);
    const [userToBlock, setuserToBlock] = useState<User | null>(null);
    const toast = useToast();
    const queryClient = useQueryClient();

    const blockUserMutation = useMutation<void, ApiError, { userId: number }>({
        mutationFn: async ({ userId }) => {
            const response = await blockUser(userId);
            return response.data;
        },
        onSuccess: () => {
            toast({ severity: 'success', detail: 'User has been blocked' });
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
        onError: (error) => {
            toast({ severity: 'error', detail: error.response.data.detail });
        },
    });

    const unblockUserMutation = useMutation<void, ApiError, { userId: number }>({
        mutationFn: async ({ userId }) => {
            const response = await unblockUser(userId);
            return response.data;
        },
        onSuccess: () => {
            toast({ severity: 'success', detail: 'User has been unblocked' });
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
        onError: (error) => {
            toast({ severity: 'error', detail: error.response.data.detail });
        },
    });

    const { data, isLoading } = useQuery<User[]>({
        queryKey: ['users'],
        queryFn: async () => {
            const result = await getUsers();
            return result.data;
        },
    });

    if (isLoading) {
        return (
            <div className="flex justify-content-center">
                <ProgressSpinner />
            </div>
        );
    }

    const handleBlock = () => {
        if (userToBlock) {
            blockUserMutation.mutate({ userId: userToBlock.id });
            setuserToBlock(null);
            setConfirmDialogVisible(false);
        }
    };

    const handleUnblock = (rowData: User) => {
        if (rowData) {
            unblockUserMutation.mutate({ userId: rowData.id });
            setuserToBlock(null);
            setConfirmDialogVisible(false);
        }
    };

    const confirmBlock = (rowData: User) => {
        setuserToBlock(rowData);
        setConfirmDialogVisible(true);
    };

    const confirmDialogFooter = (
        <div className="flex gap-2 justify-content-end">
            <Button
                label="Cancel"
                icon="pi pi-times"
                className="p-button-text"
                onClick={() => setConfirmDialogVisible(false)}
            />

            <Button
                label="Block"
                icon="pi pi-trash"
                className="p-button-danger"
                onClick={handleBlock}
            />
        </div>
    );

    return (
        <>
            <DataTable
                value={data?.slice().sort((a, b) => a.firstName.localeCompare(b.firstName))}
                paginator
                rows={25}
                className="mt-2 w-full flex-grow-1"
                emptyMessage={'No users found.'}
            >
                <Column header="First Name" field="firstName" />
                <Column header="Last Name" field="lastName" />
                <Column header="Email" field="email" />
                <Column
                    body={(rowData) => (
                        <div className="flex gap-2 justify-content-end">
                            {rowData.blockedAt ? (
                                <Button
                                    label="Unblock"
                                    icon="pi pi-unlock"
                                    className="p-button-text p-button-success"
                                    onClick={() => handleUnblock(rowData)}
                                />
                            ) : (
                                <Button
                                    label="Block"
                                    icon="pi pi-lock"
                                    className="p-button-text p-button-danger"
                                    onClick={() => confirmBlock(rowData)}
                                />
                            )}
                        </div>
                    )}
                />
            </DataTable>
            <Dialog
                header="Confirm Block"
                visible={confirmDialogVisible}
                style={{ width: '450px' }}
                modal
                footer={confirmDialogFooter}
                onHide={() => setConfirmDialogVisible(false)}
            >
                <div className="flex align-items-center gap-3 py-4">
                    <i className="pi pi-exclamation-triangle text-yellow-500 text-5xl" />
                    <div>
                        <h4 className="m-0 font-bold">Block User</h4>
                        <p className="m-0 mt-2">
                            Are you sure you want to block {userToBlock?.firstName}{' '}
                            {userToBlock?.lastName}?
                        </p>
                    </div>
                </div>
            </Dialog>
        </>
    );
}

export default AdminUsersPage;
