import { createContext, useContext } from 'react';
import { Organization } from '@/types/models/Organization';

type OrganizationContextType = {
    organization: Organization | null;
    setOrganization: (organization: Organization) => void;
    deselectOrganization: () => void;
};

export const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export const useOrganization = (): OrganizationContextType => {
    const context = useContext(OrganizationContext);
    if (!context) {
        throw new Error('useOrganization must be used within an OrganizationProvider');
    }
    return context;
};
