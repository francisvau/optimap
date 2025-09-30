import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext.ts';
import { UseMutationResult } from '@tanstack/react-query';
import { ApiError } from '@/services/client';
import { User } from '@/types/models/User.ts';
import { ChangeSettingRequest } from '@/types/schemas/Auth';

export type UserSettingsProps = {
    mutation: UseMutationResult<User, ApiError, ChangeSettingRequest>;
};

/**
 * SettingsPage allows a user to view and edit their first and last name.
 *
 * This component fetches the user's current first and last name from the authentication context
 * and allows them to edit these fields. When the user clicks the "Save" button,
 * it updates the user's information in the backend and shows a success or error message.
 * @param {UserSettingsProps} props - The props for the UserSettings component.
 * @returns {React.JSX.Element} The SettingsPage component.
 */
export function UserSettings({ mutation }: UserSettingsProps): React.JSX.Element {
    const { user } = useAuth();

    const [firstName, setFirstName] = useState(user?.firstName || '');
    const [lastName, setLastName] = useState(user?.lastName || '');
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        if (user) {
            setFirstName(user.firstName || '');
            setLastName(user.lastName || '');
        }
    }, [user]);

    const handleSave = async () => {
        mutation.mutate({ firstName, lastName });
        setIsEditing(false);
    };
    return (
        <Card
            title={
                <div className="flex items-center gap-2 align-items-center">
                    <i className="pi pi-user" />
                    <span>User Settings</span>
                </div>
            }
            className="mx-auto"
            style={{ maxWidth: '650px' }}
        >
            <div className="grid formgrid">
                <div className="field col-6 mt-3">
                    <label htmlFor="name" className="font-medium mb-2 block">
                        First name
                    </label>
                    <InputText
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="w-full"
                        type={'text'}
                        disabled={!isEditing}
                    />
                </div>
                <div className="field col-6 mt-3">
                    <label htmlFor="name" className="font-medium mb-2 block">
                        Last name
                    </label>
                    <InputText
                        value={lastName}
                        type={'text'}
                        onChange={(e) => setLastName(e.target.value)}
                        className="w-full"
                        disabled={!isEditing}
                    />
                </div>
            </div>
            <div className="field col-12 flex justify-content-end mt-5">
                <Button
                    label={isEditing ? 'Save' : 'Edit'}
                    icon={isEditing ? 'pi pi-save' : 'pi pi-pencil'}
                    loading={mutation.isPending}
                    onClick={isEditing ? handleSave : () => setIsEditing(true)}
                    className="p-button-raised"
                />
            </div>
        </Card>
    );
}
