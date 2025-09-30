import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { DashboardSidebar } from '@/layout/dashboard/DashboardSidebar';
import { Outlet } from '@/router/Outlet';
import { createOrganization, getUserOrganizations } from '@/services/organizationService';
import { Organization } from '@/types/models/Organization';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { JSX } from 'react';
import { ApiError } from '@/services/client';
import { OrganizationRequest } from '@/types/schemas/Organization';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { useNavigate } from 'react-router';
import { OrganizationHeader } from '@/layout/dashboard/OrganizationHeader';
import { useOrganization } from '@/hooks/context/OrganizationProvider/OrganizationContext';

/**
 * The `DashboardLayout` component serves as the main layout for the dashboard view.
 * It manages the user's selected organization and provides a sidebar for organization selection.
 * The layout also wraps its children with an `OrganizationProvider` to ensure the selected
 * organization context is available throughout the application.
 *
 * @returns {JSX.Element} The rendered dashboard layout component.
 *
 * @remarks
 * - The component uses the `useAuth` hook to retrieve the current user.
 * - It fetches the list of organizations associated with the user using a `useQuery` hook.
 * - The selected organization is stored in both the component state and localStorage for persistence.
 *
 * @component
 */
export function DashboardLayout(): JSX.Element {
    const { user } = useAuth();
    const { organization, setOrganization, deselectOrganization } = useOrganization();
    const toast = useToast();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const organizations = useQuery({
        enabled: !!user,
        queryKey: ['organizations', user.id],
        queryFn: getUserOrganizations,
    });

    const createOrgMutation = useMutation<Organization, ApiError, OrganizationRequest>({
        mutationFn: createOrganization,
        onSuccess: async (org: Organization) => {
            void toast({ severity: 'success', detail: 'Organization has been made' });
            void setOrganization(org);
            void navigate(`/dashboard/organizations/${org.id}`);
            await queryClient.invalidateQueries({ queryKey: ['organizations'] });
        },
        onError: (error) => {
            void toast({
                severity: 'error',
                summary: 'Failed to create organization',
                detail: error.message,
            });
        },
    });

    return (
        <div className="relative flex">
            <div className="fixed top-0 left-0 h-full w-13rem">
                <DashboardSidebar
                    organizations={organizations.data}
                    organization={organization}
                    onSetOrganization={setOrganization}
                    onSubmit={createOrgMutation.mutateAsync}
                    error={createOrgMutation.error?.message}
                    isLoading={createOrgMutation.isPending}
                />
            </div>

            <div
                className="w-full min-h-screen"
                style={{ marginLeft: 'calc(13rem + 1rem)', padding: '0 2rem 5rem' }}
            >
                <div className="mx-auto h-full w-12 lg:w-10">
                    {organization && (
                        <OrganizationHeader
                            organization={organization}
                            onDeselectOrganization={deselectOrganization}
                        />
                    )}
                    <Outlet />
                </div>
            </div>
        </div>
    );
}

export default DashboardLayout;
