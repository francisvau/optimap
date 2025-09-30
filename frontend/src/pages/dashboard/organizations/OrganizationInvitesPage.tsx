import { PendingInvitationsTable } from '@/components/dashboard/organization/PendingInvitationsTable';
import { useQuery } from '@tanstack/react-query';
import { getPendingInvitations } from '@/services/organizationService';
import { JSX } from 'react';
import { useRouteLoaderData } from 'react-router';
import { Organization } from '@/types/models/Organization';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';

/**
 * Component: OrganizationInvitesPage
 *
 * This component displays a table of pending invitations for the currently selected organization.
 * It uses the `useOrganization` hook to retrieve the currently selected organization from the global context.
 *
 * If no organization is selected, it displays a loading message.
 *
 * @returns {JSX.Element} The pending invitations table or a loading message.
 */
export function OrganizationInvitesPage(): JSX.Element {
    const organization = useStickyLoaderData<Organization>(useRouteLoaderData('organization'));

    const invites = useQuery({
        queryKey: ['organization', organization.id, 'invites'],
        queryFn: () => getPendingInvitations(organization.id),
        staleTime: 0,
    });

    return (
        <>
            <DashboardHeader title="Pending user invitations" />
            <PendingInvitationsTable isLoading={invites.isLoading} pendingUsers={invites.data} />
        </>
    );
}

export default OrganizationInvitesPage;
