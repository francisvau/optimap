import React, { JSX, useEffect, useState } from 'react';
import { Organization } from '@/types/models/Organization.ts';
import { Outlet } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { getUserOrganizations } from '@/services/organizationService';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext.ts';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { OrganizationContext } from '@/hooks/context/OrganizationProvider/OrganizationContext';

export const OrganizationProvider = (): JSX.Element => {
    const { user } = useAuth();
    const [organization, setOrg] = useState<Organization | null>();
    const toast = useToast();

    const organizations = useQuery({
        enabled: !!user,
        queryKey: ['organizations', user?.id],
        queryFn: getUserOrganizations,
    });

    useEffect(() => {
        if (!organizations.data) return;

        const storedOrg = JSON.parse(localStorage.getItem('organization') ?? 'null');
        const stillInOrg = organizations.data.some((org: Organization) => org.id === storedOrg?.id);

        if (!stillInOrg) {
            localStorage.removeItem('organization');
            setOrg(null);
        } else {
            setOrg(storedOrg);
        }
    }, [organizations.data]);

    const setOrganization = (organization: Organization) => {
        setOrg(organization);
        localStorage.setItem('organization', JSON.stringify(organization));
        toast({ severity: 'success', detail: `You are now viewing as ${organization.name}` });
    };

    const deselectOrganization = () => {
        localStorage.removeItem('organization');
        setOrg(null);
        toast({ severity: 'info', detail: 'You are now viewing your personal view' });
    };

    return (
        <OrganizationContext.Provider
            value={{ organization, setOrganization, deselectOrganization }}
        >
            <Outlet />
        </OrganizationContext.Provider>
    );
};
