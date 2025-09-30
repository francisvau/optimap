import React, { JSX, useState } from 'react';
import { useNavigate, useParams } from 'react-router';
import { isAxiosError } from 'axios';
import { ResetPasswordRequest } from '@/types/schemas/Auth';
import { ResetPasswordForm } from '@/components/auth/ResetPasswordForm';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { resetPassword } from '@/services/authenticationService';

/**
 * ResetPasswordPage component provides a form for users to request a password reset.
 *
 * @returns {JSX.Element} The rendered ResetPasswordPage component.
 */
export function ResetPasswordPage(): JSX.Element {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { token } = useParams<{ token: string }>();
    const toast = useToast();

    const handleSubmit = async (profile: ResetPasswordRequest): Promise<void> => {
        setError(null);
        setIsLoading(true);
        profile.token = token;

        if (profile.newPassword !== profile.confirmPassword) {
            setError('Passwords do not match');
            setIsLoading(false);
            return;
        }

        try {
            await resetPassword(profile);
            await navigate('/auth/login');
            toast({ severity: 'success', detail: 'Password has been reset' });
        } catch (error) {
            if (isAxiosError(error)) {
                const { data } = error.response;
                setError(data.detail ?? error.message);
            }
        } finally {
            setIsLoading(false);
        }
    };
    return (
        <div className="flex align-items-center justify-content-center">
            <ResetPasswordForm error={error} isLoading={isLoading} onSubmit={handleSubmit} />
        </div>
    );
}

export default ResetPasswordPage;
