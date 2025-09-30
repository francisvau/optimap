import { Avatar } from 'primereact/avatar';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { useNavigate } from 'react-router';
import { JSX } from 'react';
import { PrimeIcons } from 'primereact/api';
import { HttpStatus } from '@/services/client';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { deleteUserById } from '@/services/userService';

/**
 * ProfilePage component displays the user's profile information and provides options to edit or delete the profile.
 *
 * @returns {JSX.Element} The rendered ProfilePage component.
 */
export function ProfilePage(): JSX.Element {
    const { user } = useAuth();
    const navigate = useNavigate();

    const accept = async () => {
        const response = await deleteUserById(user.id);

        if (response.status === HttpStatus.NO_CONTENT) {
            navigate('/');
        }
    };

    const confirm = () => {
        confirmDialog({
            message: 'Do you want to delete your account?',
            header: 'Delete Confirmation',
            icon: PrimeIcons.INFO_CIRCLE,
            defaultFocus: 'reject',
            accept,
        });
    };

    return (
        <>
            <ConfirmDialog />
            <div className="flex justify-content-center p-3">
                <Card className="w-10 md:w-6 lg:w-4 relative">
                    <div className="flex justify-content-end mb-3">
                        <Button icon={PrimeIcons.PENCIL} tooltip="Edit Profile" />
                    </div>

                    <div className="flex flex-column align-items-center gap-3 mb-3">
                        <Avatar
                            label={user.firstName[0] + user.lastName[0]}
                            shape="circle"
                            size="xlarge"
                        />
                        <h2 className="text-center">
                            {user.firstName} {user.lastName}
                        </h2>
                    </div>

                    <div className="flex flex-column gap-2">
                        <p>
                            <strong>Email:</strong> {user.email}
                        </p>
                        <p>
                            <strong>User ID:</strong> {user.id}
                        </p>
                    </div>
                    <div className="flex justify-content-end mt-3">
                        <Button
                            icon="pi pi-times"
                            label="Delete"
                            className="p-button-danger p-button-text"
                            onClick={confirm}
                        />
                    </div>
                </Card>
            </div>
        </>
    );
}

export default ProfilePage;
