import { JSX, useMemo } from 'react';
import { AxiosError } from 'axios';
import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm';
import { ForgotPasswordRequest } from '@/types/schemas/Auth';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { forgotPassword } from '@/services/authenticationService';
import { useMutation } from '@tanstack/react-query';

/**
 * ForgotPasswordPage component provides a form for users to request a password reset.
 *
 * @returns {JSX.Element} The rendered ForgotPasswordPage component.
 */
export function ForgotPasswordPage(): JSX.Element {
    const toast = useToast();

    const mutation = useMutation({
        mutationFn: (data: ForgotPasswordRequest) => forgotPassword(data),
        onSuccess: () => {
            void toast({ severity: 'success', detail: 'Email has been sent' });
        },
        onError: (e: AxiosError<{ detail: string }>) => {
            return e.response?.data.detail ?? e.message;
        },
    });

    const error = useMemo(() => {
        if (mutation.error !== null) {
            return mutation.error.response?.data.detail ?? mutation.error.message;
        }

        return null;
    }, [mutation]);

    return (
        <div className="flex align-items-center justify-content-center">
            <ForgotPasswordForm
                error={error}
                isLoading={mutation.isPending}
                onSubmit={mutation.mutateAsync}
            />
        </div>
    );
}

export default ForgotPasswordPage;
