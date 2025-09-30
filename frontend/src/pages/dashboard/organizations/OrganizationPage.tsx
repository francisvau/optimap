import { JSX, MouseEvent, useEffect, useState } from 'react';
import { useLoaderData, useNavigate, useParams, useRevalidator } from 'react-router';
import { Button } from 'primereact/button';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import {
    createModelForOrganization,
    deleteModelForOrganization,
    deleteOrganization,
    editOrganization,
    getModelsForOrganization,
    getOrganizationUsers,
    getPendingInvitations,
    organizationStats,
    updateModelForOrganization,
} from '@/services/organizationService';
import { useOrganization } from '@/hooks/context/OrganizationProvider/OrganizationContext';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';
import { ProgressSpinner } from 'primereact/progressspinner';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader.tsx';
import { CreateOrganizationForm } from '@/components/dashboard/organization/forms/CreateOrganizationForm.tsx';
import { Dialog } from 'primereact/dialog';
import { ApiError } from '@/services/client';
import { Organization } from '@/types/models/Organization.ts';
import { Card } from 'primereact/card';
import { TabView, TabPanel } from 'primereact/tabview';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Divider } from 'primereact/divider';
import { PrimeIcons } from 'primereact/api';
import { getOrganizationJobs } from '@/services/mapping/jobService';
import { useStickyLoaderData } from '@/hooks/util/useStickyLoaderData';
import { MappingJob } from '@/types/models/Job';
import { jobStatusMeta } from '@/utils/jobUtils';
import { OrganizationRequest } from '@/types/schemas/Organization';
import { Model } from '@/types/models/Model';
import { baseModelMeta } from '@/utils/modelUtils';
import { Tooltip } from 'primereact/tooltip';
import { capitalize } from '@/utils/stringUtils';
import { ModelForm } from '@/components/dashboard/forms/ModelForm';
import { ModelRequest } from '@/types/schemas/Model';

/**
 * OrganizationPage component displays the details of an organization with an overview
 * of data mapping jobs, statistics, and organization settings.
 *
 * @component
 * @returns {JSX.Element} The rendered component.
 */
export function OrganizationPage(): JSX.Element {
    const { deselectOrganization } = useOrganization();
    const { revalidate } = useRevalidator();
    const { tabView } = useParams();

    const navigate = useNavigate();
    const toast = useToast();

    const organization = useStickyLoaderData(useLoaderData<Organization>());
    const queryClient = useQueryClient();

    const [modelDialogVisible, setModelDialogVisible] = useState(false);
    const [selectedModel, setSelectedModel] = useState<Model | null>(null);

    const [dialogVisible, setDialogVisible] = useState(false);
    const [activeTab, setActiveTab] = useState(0);

    // Fetch recent mapping jobs
    const jobsQuery = useQuery({
        queryKey: ['organization', organization.id, 'jobs'],
        enabled: !!organization?.id,
        queryFn: () => getOrganizationJobs(organization?.id),
    });

    // Fetch organization members
    const membersQuery = useQuery({
        queryKey: ['organization', organization.id, 'users'],
        queryFn: async () => await getOrganizationUsers(organization.id),
    });

    // Fetch pending invitations
    const invitiationsQuery = useQuery({
        queryKey: ['organization', organization.id, 'invites'],
        queryFn: () => getPendingInvitations(organization.id),
        staleTime: 0,
    });

    const stats = useQuery({
        queryKey: ['organization', organization.id, 'stats'],
        queryFn: () => organizationStats(organization.id),
        enabled: !!organization?.id,
    });

    // Fetch models
    const modelsQuery = useQuery({
        enabled: !!organization?.id,
        queryKey: ['organization', organization.id, 'models'],
        queryFn: () => getModelsForOrganization(organization.id),
    });

    // Mutation to delete organization
    const deleteOrganisationMutation = useMutation({
        mutationFn: deleteOrganization,
        onSuccess: () => {
            deselectOrganization();
            navigate('/dashboard');
        },
        onError: (error) => {
            toast({ severity: 'error', detail: 'Error deleting organization' });
            console.error('Delete error:', error);
            navigate('/dashboard');
        },
    });

    // Mutation to edit organization
    const editOrganizationMutation = useMutation<Organization, ApiError, OrganizationRequest>({
        mutationFn: async (data: OrganizationRequest) => editOrganization(organization.id, data),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['organizations'] });
            await revalidate();
            void toast({ severity: 'success', detail: 'Organization has been updated' });
            setDialogVisible(false);
        },
        onError: async (error: ApiError) => {
            toast({ severity: 'error', detail: error.response.data.detail });
        },
    });

    // Mutation to create model
    const createModelMutation = useMutation({
        mutationFn: (form: ModelRequest) => {
            return createModelForOrganization(organization.id, form);
        },
        onSuccess: async () => {
            await modelsQuery.refetch();
            toast({ severity: 'success', detail: 'Model has been created' });
            setModelDialogVisible(false);
        },
        onError: (error: ApiError) => {
            toast({ severity: 'error', detail: error.message });
        },
    });

    // Mutation to update model
    const updateModelMutation = useMutation({
        mutationFn: (form: ModelRequest) => {
            if (!selectedModel) {
                toast({ severity: 'error', detail: 'No model selected' });
            } else {
                return updateModelForOrganization(organization.id, selectedModel.id, form);
            }
        },
        onSuccess: async () => {
            await modelsQuery.refetch();
            toast({ severity: 'success', detail: 'Model has been updated' });
            setModelDialogVisible(false);
            setSelectedModel(null);
        },
        onError: (error: ApiError) => {
            toast({ severity: 'error', detail: error.message });
        },
    });

    // Mutation to delete model
    const deleteModelMutation = useMutation({
        mutationFn: (modelId: string) => deleteModelForOrganization(organization.id, modelId),
        onSuccess: async () => {
            await modelsQuery.refetch();
            toast({ severity: 'success', detail: 'Model has been deleted' });
        },
    });

    // Open the tab view based on the URL parameter.
    useEffect(() => {
        if (tabView !== undefined) {
            const index = ['dashboard', 'settings', 'team'].indexOf(tabView);

            if (index !== -1) {
                setActiveTab(index);
            }
        }
    }, [tabView]);

    const confirmDelete = () => {
        confirmDialog({
            message: 'Are you sure you want to delete this organization?',
            header: 'Confirm Deletion',
            icon: PrimeIcons.EXCLAMATION_TRIANGLE,
            accept: () => {
                deleteOrganisationMutation.mutate(organization?.id);
            },
        });
    };

    const handleTabChange = (event: { index: number }) => {
        const view = ['dashboard', 'settings', 'team'][event.index];
        navigate(`/dashboard/organizations/${organization.id}/${view}`);
    };

    const handleSelectModel = (model: Model) => {
        setSelectedModel(model);
        setModelDialogVisible(true);
    };

    const handleCloseModelDialog = () => {
        setModelDialogVisible(false);
        setSelectedModel(null);
    };

    const handleDeleteModelClick = (e: MouseEvent, model: Model) => {
        e.stopPropagation();
        confirmDialog({
            message: `Are you sure you want to delete the model "${model.name}"?`,
            header: 'Confirm Deletion',
            icon: PrimeIcons.EXCLAMATION_TRIANGLE,
            accept: () => {
                deleteModelMutation.mutate(model.id);
            },
        });
    };

    if (!organization) {
        return (
            <div className="flex justify-content-center">
                <ProgressSpinner />
            </div>
        );
    }

    return (
        <>
            <ConfirmDialog />
            <Dialog
                header="Edit Organization"
                visible={dialogVisible}
                onHide={() => setDialogVisible(false)}
            >
                <CreateOrganizationForm
                    error={editOrganizationMutation.error?.message}
                    isLoading={editOrganizationMutation.isPending}
                    onSubmit={editOrganizationMutation.mutateAsync}
                    initial={organization}
                />
            </Dialog>

            <Dialog
                header="Create a tailored model"
                visible={modelDialogVisible}
                onHide={handleCloseModelDialog}
            >
                {selectedModel ? (
                    <ModelForm
                        initial={selectedModel}
                        error={updateModelMutation.error?.message}
                        isLoading={updateModelMutation.isPending}
                        onSubmit={updateModelMutation.mutateAsync}
                    />
                ) : (
                    <ModelForm
                        error={createModelMutation.error?.message}
                        isLoading={createModelMutation.isPending}
                        onSubmit={createModelMutation.mutateAsync}
                    />
                )}
            </Dialog>
            <DashboardHeader
                title={organization?.name}
                end={
                    <>
                        <Button
                            icon={PrimeIcons.PENCIL}
                            className="p-button-text"
                            onClick={() => setDialogVisible(true)}
                            tooltip="Edit Organization"
                            tooltipOptions={{ position: 'bottom' }}
                        />
                        <Button
                            icon={PrimeIcons.TRASH}
                            className="p-button-danger p-button-text"
                            onClick={confirmDelete}
                            tooltip="Delete Organization"
                            tooltipOptions={{ position: 'bottom' }}
                            disabled={deleteOrganisationMutation.isPending}
                        />
                    </>
                }
            />

            <TabView activeIndex={activeTab} onTabChange={handleTabChange}>
                {/* Overview */}
                <TabPanel header="Dashboard">
                    <div className="grid p-2">
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.userCount || 0}
                                </h2>
                                <p className="text-sm text-color-secondary">Team Members</p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.jobCount || 0}
                                </h2>
                                <p className="text-sm text-color-secondary">Total Jobs</p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.pendingInviteCount || 0}
                                </h2>
                                <p className="text-sm text-color-secondary">Pending invites</p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.adminUserCount || 0}
                                </h2>
                                <p className="text-sm text-color-secondary">Admins</p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {(stats.data?.bytes / 1024 / 1024).toFixed(2) || 0} MB
                                </h2>
                                <p className="text-sm text-color-secondary">Total MB Processed</p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.minExecutionTime || 0} s
                                </h2>
                                <p className="text-sm text-color-secondary">
                                    Minimum Execution Time
                                </p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.maxExecutionTime || 0} s
                                </h2>
                                <p className="text-sm text-color-secondary">
                                    Maximum Execution Time
                                </p>
                            </Card>
                        </div>
                        <div className="col-12 md:col-6 lg:col-3">
                            <Card className="text-center shadow-2">
                                <h2 className="text-xl font-bold text-primary">
                                    {stats.data?.avgExecutionTime || 0} s
                                </h2>
                                <p className="text-sm text-color-secondary">
                                    Average Execution Time
                                </p>
                            </Card>
                        </div>

                        <div className="col-12">
                            <Card
                                title="Recent Mapping Jobs"
                                className="shadow-2"
                                subTitle={`${jobsQuery.data?.length} most recent jobs`}
                            >
                                <DataTable
                                    value={jobsQuery.data}
                                    loading={jobsQuery.isLoading}
                                    rowHover
                                    paginator
                                    rows={5}
                                    emptyMessage="No recent jobs"
                                >
                                    <Column
                                        field="inputDefinition.name"
                                        header="Input Definition"
                                        sortable
                                    />
                                    <Column
                                        field="createdAt"
                                        header="Created"
                                        body={(data: MappingJob) =>
                                            new Date(data.createdAt).toLocaleDateString()
                                        }
                                        sortable
                                    />
                                    <Column
                                        field="status"
                                        header="Status"
                                        body={(data: MappingJob) => (
                                            <Tag
                                                severity={jobStatusMeta[data.status].tagSeverity}
                                                value={data.status}
                                            />
                                        )}
                                        sortable
                                    />
                                    <Column
                                        header="Actions"
                                        body={(data: MappingJob) => (
                                            <Button
                                                icon={PrimeIcons.EYE}
                                                text
                                                rounded
                                                onClick={() =>
                                                    navigate(`/dashboard/jobs/${data.id}`)
                                                }
                                                tooltip="View Job"
                                                tooltipOptions={{ position: 'bottom' }}
                                            />
                                        )}
                                        style={{ width: '8em', textAlign: 'center' }}
                                    />
                                </DataTable>
                                <div className="flex justify-content-end mt-3">
                                    <Button
                                        label="View All Jobs"
                                        onClick={() => navigate('/dashboard/jobs')}
                                    />
                                </div>
                            </Card>
                        </div>
                    </div>
                </TabPanel>
                {/* Settings */}
                <TabPanel header="Organization Settings">
                    <div className="card p-4 shadow-2 border-round">
                        <div className="flex align-items-center mb-4">
                            <i className="pi pi-cog text-2xl mr-3 text-primary"></i>
                            <h3 className="m-0">Organization Settings</h3>
                        </div>

                        <Divider className="my-3" />

                        <div className="grid">
                            <div className="col-12 md:col-6">
                                <Card className="shadow-1" title="Basic Information">
                                    <CreateOrganizationForm
                                        initial={organization}
                                        isLoading={editOrganizationMutation.isPending}
                                        error={editOrganizationMutation.error?.message}
                                        onSubmit={editOrganizationMutation.mutateAsync}
                                    />
                                </Card>
                            </div>

                            <div className="col-12 md:col-6">
                                <Card
                                    className="shadow-1"
                                    title={
                                        <div className="flex align-items-center justify-content-between gap-3">
                                            <h4 className="m-0">Tailored Engine Models</h4>
                                            <Button
                                                icon={PrimeIcons.PLUS}
                                                tooltip="Create New Model"
                                                tooltipOptions={{ position: 'top' }}
                                                onClick={() => {
                                                    setSelectedModel(null);
                                                    setModelDialogVisible(true);
                                                }}
                                            />
                                        </div>
                                    }
                                >
                                    <div className="mb-4">
                                        Create tailored models to enhance the performance of your
                                        generated JSONata mapping rules. Tailored models are based
                                        on the base models and can be customized to suit your
                                        specific needs.
                                    </div>
                                    {!modelsQuery.data?.length ? (
                                        <div className="text-300 text-center">
                                            No tailored models created yet.
                                        </div>
                                    ) : (
                                        modelsQuery.data?.map((model: Model) => (
                                            <div
                                                key={model.id}
                                                className="p-3 flex align-items-center gap-4 mb-3 hover:surface-hover cursor-pointer"
                                                onClick={handleSelectModel.bind(null, model)}
                                            >
                                                <Tooltip
                                                    target={`#model-${model.id}-logo`}
                                                    content={
                                                        baseModelMeta[model.baseModel].description
                                                    }
                                                    position="top"
                                                />
                                                <img
                                                    id={`model-${model.id}-logo`}
                                                    style={{
                                                        width: '50px',
                                                        objectPosition: 'center',
                                                    }}
                                                    src={baseModelMeta[model.baseModel].logo}
                                                />
                                                <div>
                                                    <h4 className="text-lg font-bold m-0">
                                                        {model.name}
                                                    </h4>
                                                    <p className="text-sm text-color-secondary mb-0 mt-2">
                                                        Based On: {capitalize(model.baseModel)}
                                                    </p>
                                                </div>
                                                <Button
                                                    onClick={(e) =>
                                                        handleDeleteModelClick(e, model)
                                                    }
                                                    className="ml-auto"
                                                    severity="danger"
                                                    icon={PrimeIcons.TRASH}
                                                    text
                                                />
                                            </div>
                                        ))
                                    )}
                                </Card>
                            </div>
                        </div>
                    </div>
                </TabPanel>
                {/* Team Overview */}
                <TabPanel header="Team Overview">
                    <div className="card p-4 shadow-2">
                        <div className="flex justify-content-between align-items-center mb-3">
                            <div className="flex align-items-center">
                                <i className="pi pi-users text-2xl mr-3 text-primary"></i>
                                <h3 className="m-0">Team Members</h3>
                            </div>
                            <Button
                                label="Manage Team"
                                icon="pi pi-users"
                                onClick={() =>
                                    navigate(`/dashboard/organizations/${organization?.id}/users`)
                                }
                            />
                        </div>
                        <Divider />

                        <div className="grid">
                            <div className="col-12 md:col-4">
                                <Card className="text-center">
                                    <h2 className="text-xl font-bold text-primary">
                                        {membersQuery.data?.length || 0}
                                    </h2>
                                    <p>Total Members</p>
                                </Card>
                            </div>
                            <div className="col-12 md:col-4">
                                <Card className="text-center">
                                    <h2 className="text-xl font-bold text-primary">
                                        {membersQuery.data?.filter(
                                            (member) => member.role.name === 'admin',
                                        ).length || 0}
                                    </h2>
                                    <p>Administrators</p>
                                </Card>
                            </div>
                            <div className="col-12 md:col-4">
                                <Card className="text-center">
                                    <h2 className="text-xl font-bold text-primary">
                                        {invitiationsQuery.data?.length || 0}
                                    </h2>
                                    <p>Pending Invites</p>
                                </Card>
                            </div>
                        </div>

                        <div className="mt-4">
                            <h4>Recent Activity</h4>
                            <ul className="list-none p-0 m-0">
                                {invitiationsQuery.data && invitiationsQuery.data.length > 0 ? (
                                    invitiationsQuery.data?.map((user, index) => (
                                        <li
                                            key={index}
                                            className="flex items-center justify-between p-4 border-b border-gray-200"
                                        >
                                            <div className="flex items-center space-x-3">
                                                <span className="pi pi-user text-primary" />
                                                <div>
                                                    <div className="font-medium text-gray-900">
                                                        {user.email}
                                                    </div>
                                                    <div className="text-sm text-gray-500">
                                                        {user.joinedAt
                                                            ? `Joined on ${new Date(user.joinedAt).toLocaleDateString()}`
                                                            : `Pending — expires on ${new Date(user.expiresAt).toLocaleDateString()}`}
                                                    </div>
                                                </div>
                                            </div>
                                        </li>
                                    ))
                                ) : (
                                    <li className="p-4 text-gray-500">No pending users</li>
                                )}
                            </ul>
                        </div>
                    </div>
                </TabPanel>
            </TabView>
        </>
    );
}

export default OrganizationPage;
