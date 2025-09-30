import { JSX } from 'react';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { useNavigate } from 'react-router';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { register } from '@/services/authenticationService';
import { useMutation } from '@tanstack/react-query';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';

/**
 * RegisterPage component provides a registration form for users to sign up.
 *
 * @returns {JSX.Element} The rendered RegisterPage component.
 */
export function RegisterPage(): JSX.Element {
    const navigate = useNavigate();
    const toast = useToast();
    const { reload } = useAuth();

    const { mutateAsync, isPending, error } = useMutation({
        mutationFn: register,
        onSuccess: async () => {
            void toast({
                severity: 'success',
                detail: 'Account created successfully! Please check your email to verify your account before logging in.',
            });
            await reload();
            await navigate('/auth/verify');
        },
    });

    return (
        <div className="flex align-items-center justify-content-center">
            <RegisterForm error={error?.message} isLoading={isPending} onSubmit={mutateAsync} />
        </div>
    );
}

export default RegisterPage;
