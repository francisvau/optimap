import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { verify, verifyRequest } from '@/services/authenticationService';
import { useMutation } from '@tanstack/react-query';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { ProgressSpinner } from 'primereact/progressspinner';
import { useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router';

/**
 * A React component that displays a verification page for user accounts.
 *
 * This page is intended to inform the user that a verification email has been sent
 * to their email address and provides instructions on what to do if they do not
 * receive the email. If the `email` state is not available in the location object,
 * the user is redirected to the login page.
 *
 * @returns A JSX element containing the verification page content.
 */
export function VerifyPage() {
    const { token } = useParams();
    const toast = useToast();
    const navigate = useNavigate();
    const { user, isLoading, reload } = useAuth();
    const isVerifying = useRef(false);

    // Verification mutation for token-based verification
    const verifyMutation = useMutation({
        mutationFn: verify,
        onSuccess: async () => {
            await reload?.();
            toast({ severity: 'success', detail: 'Account verified successfully!' });
            navigate('/dashboard', { replace: true });
        },
        onError: () => {
            toast({ severity: 'error', detail: 'Invalid or expired verification token' });
            navigate('/auth/verify', { replace: true });
        },
    });

    // Resend mutation for email verification
    const resendMutation = useMutation({
        mutationFn: () => verifyRequest(user!.email),
        onSuccess: () => toast({ severity: 'success', detail: 'Verification email resent' }),
        onError: () => toast({ severity: 'error', detail: 'Failed to resend verification email' }),
    });

    // Handle token verification flow
    useEffect(() => {
        if (token && !isVerifying.current) {
            isVerifying.current = true;
            verifyMutation.mutate(token);
        }
    }, [token, verifyMutation]);

    // Redirect logged-out users when no token present
    useEffect(() => {
        if (!token && !isLoading && !user) {
            navigate('/auth/login', { replace: true });
        }
    }, [token, isLoading, user, navigate]);

    // Token verification in progress
    if (token) {
        return (
            <div className="flex justify-content-center">
                <Card className="w-full max-w-30rem">
                    <div className="flex justify-content-center p-4">
                        <ProgressSpinner />
                    </div>
                </Card>
            </div>
        );
    }

    // Resend verification UI
    return (
        user && (
            <div className="flex justify-content-center">
                <Card className="w-full max-w-30rem" title="Verify Your Account">
                    <div className="flex flex-column gap-3">
                        <p>
                            A verification link was sent to <strong>{user.email}</strong>. Check
                            your inbox and spam folder.
                        </p>

                        <Button
                            label="Resend Verification Email"
                            loading={resendMutation.isPending}
                            onClick={() => resendMutation.mutate()}
                        />
                    </div>
                </Card>
            </div>
        )
    );
}

export default VerifyPage;
