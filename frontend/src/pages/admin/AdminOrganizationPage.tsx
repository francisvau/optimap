import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { useQuery } from '@tanstack/react-query';

import { ProgressSpinner } from 'primereact/progressspinner';
import { Organization } from '@/types/models/Organization.ts';
import { getOrganizations } from '@/services/organizationService';
import { useNavigate } from 'react-router';
import { useOrganization } from '@/hooks/context/OrganizationProvider/OrganizationContext';

/**
 * ForgotPasswordForm component
 *
 * This component renders a form for users to request a password reset link.
 *
 *
 * @returns {JSX.Element} The rendered ForgotPasswordForm component
 */
export function AdminOrganizationPage() {
    const navigate = useNavigate();
    const { setOrganization } = useOrganization();

    const { data, isLoading } = useQuery<Organization[]>({
        queryKey: ['organizations'],
        queryFn: getOrganizations,
    });

    if (isLoading) {
        return (
            <div className="flex justify-content-center">
                <ProgressSpinner />
            </div>
        );
    }

    const handleRowClick = (organization: Organization) => {
        setOrganization(organization);
        navigate(`/dashboard`);
    };

    return (
        <DataTable
            value={data}
            paginator
            rows={25}
            className="mt-2 w-full flex-grow-1"
            emptyMessage={'No organizations found.'}
            selectionMode="single"
            onRowClick={(e) => handleRowClick(e.data as Organization)}
            rowClassName={() => 'cursor-pointer'}
        >
            <Column header="Name" field="name" style={{ maxWidth: '250px' }} />
            <Column
                header="Address"
                field="address"
                style={{ maxWidth: '250px' }}
                body={(rowData) => (
                    <div className="white-space-nowrap overflow-hidden text-overflow-ellipsis">
                        {rowData.address}
                    </div>
                )}
            />
            <Column
                header="Description"
                field="systemPrompt"
                style={{ maxWidth: '400px' }}
                body={(rowData) => (
                    <div className="white-space-nowrap overflow-hidden text-overflow-ellipsis">
                        {rowData.systemPrompt}
                    </div>
                )}
            />
        </DataTable>
    );
}

export default AdminOrganizationPage;
