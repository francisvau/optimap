import { PrimeIcons } from 'primereact/api';
import { Menu } from 'primereact/menu';
import { JSX, useState } from 'react';
import { NavLink, useNavigate } from 'react-router';
import { Dialog } from 'primereact/dialog';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { CreateOrganizationForm } from '@/components/dashboard/organization/forms/CreateOrganizationForm';
import { OrganizationRequest } from '@/types/schemas/Organization';
import { UserMenu } from '@/layout/navigation/UserMenu';
import { Organization } from '@/types/models/Organization';
import { OrganizationSelector } from '@/components/dashboard/organization/OrganizationSelector';
import { EXTERNAL_MOLNITORING_DASHBOARD } from '@/environment';

export type DashboardSidebarProps = {
    organizations: Organization[];
    organization: Organization | null;
    error: string | null;
    isLoading: boolean;
    onSetOrganization: (organization: Organization) => void;
    onSubmit: (name: OrganizationRequest) => Promise<unknown>;
};

/**
 * The `DashboardSidebar` component renders a sidebar menu for the dashboard layout.
 * It provides navigation options, organization management, and user-specific actions.
 *
 * @param {DashboardSidebarProps} props - The props for the `DashboardSidebar` component.
 *
 * @returns {JSX.Element} The rendered `DashboardSidebar` component.
 */
export function DashboardSidebar({
    organizations,
    organization,
    onSetOrganization,
    error,
    isLoading,
    onSubmit,
}: DashboardSidebarProps): JSX.Element {
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const navigate = useNavigate();
    const { user } = useAuth();

    // The base menu items that are always shown
    const baseItems = [
        {
            label: 'Dashboard',
            icon: PrimeIcons.MAP,
            command: () => {
                if (organization) {
                    void navigate(`/dashboard/organizations/${organization.id}`);
                } else {
                    void navigate('/dashboard');
                }
            },
        },
        {
            label: 'Mapping',
            icon: PrimeIcons.SITEMAP,
            items: [
                {
                    label: 'Mapping Blueprints',
                    icon: PrimeIcons.SITEMAP,
                    command: () => void navigate('/dashboard/blueprints'),
                },
                {
                    label: 'Mapping Jobs',
                    icon: PrimeIcons.PLAY,
                    command: () => void navigate('/dashboard/jobs'),
                },
            ],
        },
    ];

    // The organization-specific menu items
    const orgItems = organization
        ? [
              {
                  label: organization.name,
                  items: [
                      {
                          label: 'Overview',
                          icon: PrimeIcons.BUILDING,
                          command: () =>
                              void navigate(`/dashboard/organizations/${organization.id}`),
                      },
                      {
                          label: 'User Management',
                          icon: PrimeIcons.USER,
                          command: () =>
                              void navigate(`/dashboard/organizations/${organization.id}/users`),
                      },
                      {
                          label: 'Role Management',
                          icon: PrimeIcons.TAGS,
                          command: () =>
                              void navigate(`/dashboard/organizations/${organization.id}/roles`),
                      },
                      {
                          label: 'Invites',
                          icon: PrimeIcons.ENVELOPE,
                          command: () =>
                              navigate(`/dashboard/organizations/${organization.id}/invites`),
                      },
                  ],
              },
          ]
        : [];

    // Additional menu items for admin users
    const adminItems = user.isAdmin
        ? [
              {
                  label: 'Admin',
                  items: [
                      {
                          label: 'Logs',
                          icon: PrimeIcons.BOOK,
                          command: () => {
                              navigate('/admin');
                          },
                      },
                      {
                          label: 'Users',
                          icon: PrimeIcons.USER,
                          command: () => {
                              navigate('/admin/users');
                          },
                      },
                      {
                          label: 'Organizations',
                          icon: PrimeIcons.BUILDING,
                          command: () => {
                              navigate('/admin/organizations');
                          },
                      },
                      {
                          label: 'System Monitoring',
                          icon: PrimeIcons.COG,
                          command: () => {
                              window.open(EXTERNAL_MOLNITORING_DASHBOARD, '_blank');
                          },
                      },
                  ],
              },
          ]
        : [];

    const handleSubmitOrganization = async (data: OrganizationRequest) => {
        setShowCreateDialog(false);
        onSubmit(data);
    };

    const handleChangeOrganization = async (org: Organization) => {
        void onSetOrganization(org);
        void navigate(`/dashboard/organizations/${org.id}`);
    };

    // The header item for the menu
    const headerItem = {
        template: () => (
            <NavLink to="/">
                <h1 className="text-center text-2xl my-3">Optimap Prime</h1>
            </NavLink>
        ),
    };

    const footerTemplate = () => (
        <>
            <div className="p-3 flex flex-column text-md gap-3">
                <div className="flex align-items-center gap-2">
                    <UserMenu />
                    <span>
                        {user.firstName} {user.lastName}
                    </span>
                </div>
                <OrganizationSelector
                    organization={organization}
                    organizations={organizations}
                    onChangeOrganization={handleChangeOrganization}
                    onAddOrganizationClick={() => setShowCreateDialog(true)}
                />
            </div>
        </>
    );

    const menuModel = [
        headerItem,
        { separator: true, className: 'mb-2' },
        ...baseItems,
        ...orgItems,
        ...adminItems,
        { separator: true, className: 'mt-auto' },
        { template: footerTemplate },
    ];

    return (
        <>
            <Menu model={menuModel} className="h-full w-full" />
            <Dialog
                header="Create Organization"
                visible={showCreateDialog}
                onHide={() => setShowCreateDialog(false)}
                style={{ maxWidth: 600 }}
            >
                <CreateOrganizationForm
                    error={error}
                    isLoading={isLoading}
                    onSubmit={handleSubmitOrganization}
                />
            </Dialog>
        </>
    );
}
