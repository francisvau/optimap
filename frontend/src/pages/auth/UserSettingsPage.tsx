import React from 'react';
import { NotificationSettings } from '@/components/auth/NotificationSettings.tsx';
import { UserSettings } from '@/components/auth/UserSettings.tsx';
import { useMutation } from '@tanstack/react-query';
import { ChangeSettingRequest } from '@/types/schemas/Auth';
import { updateUser } from '@/services/authenticationService';
import { AxiosError } from 'axios';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { User } from '@/types/models/User.ts';
import { ApiError } from '@/services/client';

/**
 * SettingsPage allows a user to view and edit their first and last name.
 *
 * This component fetches the user's current first and last name from the authentication context
 * and allows them to edit these fields. When the user clicks the "Save" button,
 * it updates the user's information in the backend and shows a success or error message.
 *
 * @returns {React.JSX.Element} The SettingsPage component.
 */
export function SettingsPage(): React.JSX.Element {
    const toast = useToast();

    const mutation = useMutation<User, ApiError, ChangeSettingRequest>({
        mutationFn: updateUser,
        onSuccess: () => {
            toast({ severity: 'success', detail: 'Settings saved successfully' });
        },
        onError: (e: AxiosError<{ detail: string }>) => {
            toast({ severity: 'error', detail: 'Error saving settings' });
            return e.response?.data.detail ?? e.message;
        },
    });

    return (
        <div style={{ paddingBottom: '100px' }}>
            <UserSettings mutation={mutation} />
            <NotificationSettings />
        </div>
    );
}

export default SettingsPage;
