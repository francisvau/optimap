import { useMutation } from '@tanstack/react-query';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { ProgressSpinner } from 'primereact/progressspinner';
import { JSX } from 'react';
import { useNavigate, useParams } from 'react-router';
import { ApiError } from '@/services/client';
import { JoinOrganizationRequest, JoinOrganizationResponse } from '@/types/schemas/Organization';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { joinOrganization } from '@/services/organizationService';

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
export function JoinOrganizationPage(): JSX.Element {
    const params = useParams();
    const toast = useToast();
    const navigate = useNavigate();

    const JoinMutation = useMutation<JoinOrganizationResponse, ApiError, JoinOrganizationRequest>({
        mutationFn: (form) => joinOrganization(form),
        onSuccess: (data) => {
            void toast({ severity: 'success', detail: 'You have joined the organization!' });
            void navigate(`/dashboard/organizations/${data.organizationId}`);
        },
        onError: (error) => {
            void toast({ severity: 'error', detail: error.message ?? 'Invalid or expired token.' });
        },
    });

    const handleJoin = () => {
        if (params.token) {
            void JoinMutation.mutateAsync({ token: params.token });
        }
    };

    return (
        <div className="flex justify-content-center align-items-center h-full">
            <Card className="inline-block w-full" style={{ maxWidth: '600px' }}>
                {params.token && JoinMutation.isPending ? (
                    <div className="flex justify-content-center">
                        <ProgressSpinner />
                    </div>
                ) : (
                    <>
                        <h1 className="m-0">Join organization</h1>
                        <p className="my-4">Press the button below to join the organization.</p>
                        <Button
                            label="Join organization"
                            className="w-full"
                            onClick={handleJoin}
                            loading={JoinMutation.isPending}
                            disabled={JoinMutation.isPending}
                        />
                    </>
                )}
            </Card>
        </div>
    );
}

export default JoinOrganizationPage;
