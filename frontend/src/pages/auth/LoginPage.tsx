import { JSX } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { LoginRequest } from '@/types/schemas/Auth';
import { useNavigate } from 'react-router';
import { useMutation } from '@tanstack/react-query';
import { ApiError } from '@/services/client';
import { User } from '@/types/models/User';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';

/**
 * LoginPage component provides a login form for users to sign in.
 *
 * @returns {JSX.Element} The rendered LoginPage component.
 */
export function LoginPage(): JSX.Element {
    const { login } = useAuth();
    const navigate = useNavigate();
    const toast = useToast();

    const { mutateAsync, error, isPaused } = useMutation<User, ApiError, LoginRequest>({
        mutationFn: login,
        onSuccess: async (user: User) => {
            if (user.isVerified) {
                void toast({ severity: 'success', detail: 'Login successful' });
                await navigate('/dashboard');
            } else {
                void toast({ severity: 'warn', detail: 'Please verify your account' });
                await navigate('/auth/verify');
            }
        },
    });

    return (
        <div className="flex align-items-center justify-content-center">
            <LoginForm error={error?.message} isLoading={isPaused} onSubmit={mutateAsync} />
        </div>
    );
}

export default LoginPage;
