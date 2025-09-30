import { BlueprintList } from '@/components/dashboard/blueprints/BlueprintList';
import { DashboardHeader } from '@/layout/dashboard/DashboardHeader';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { JSX, useState } from 'react';
import { Dialog } from 'primereact/dialog';
import { type BlueprintRequest } from '@/types/schemas/Blueprint';
import { MappingBlueprint } from '@/types/models/Blueprint';
import { ApiError } from '@/services/client';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { useNavigate } from 'react-router';
import { BlueprintForm } from '@/components/dashboard/forms/BlueprintForm';
import { useOrganization } from '@/hooks/context/OrganizationProvider/OrganizationContext';
import {
    createBlueprint,
    deleteBlueprint,
    getOrganizationBlueprints,
    getUserBlueprints,
} from '@/services/mapping/blueprintService';
import { getUserOrganizations } from '@/services/organizationService.ts';

/**
 * Represents the ListBlueprintPage component, which displays a page
 * containing a heading for "Mapping Blueprints".
 *
 * @returns {JSX.Element} The rendered JSX element for the ListBlueprintPage.
 */
export function ListBlueprintPage(): JSX.Element {
    const [showBpDialog, setShowBpDialog] = useState(false);
    const { user } = useAuth();
    const { organization } = useOrganization();
    const queryClient = useQueryClient();
    const toast = useToast();
    const navigate = useNavigate();

    const { data: organizations } = useQuery({
        queryKey: ['organizations', user.id],
        queryFn: async () => await getUserOrganizations(),
    });

    const queryKey = ['blueprints', organization?.id ? organization.id : 'user'];

    const { data, isLoading, isError } = useQuery({
        queryKey,
        queryFn: async () => {
            if (organization) {
                return await getOrganizationBlueprints(organization.id);
            } else {
                return await getUserBlueprints(user.id);
            }
        },
    });

    const createBpMutation = useMutation<MappingBlueprint, ApiError, BlueprintRequest, string>({
        mutationFn: (form: BlueprintRequest) => createBlueprint(form),
        onSuccess: async (blueprint: MappingBlueprint) => {
            setShowBpDialog(false);
            toast({ severity: 'success', detail: 'Blueprint created successfully' });
            navigate(`/dashboard/blueprints/${blueprint.id}/edit`);
        },
    });

    const deleteBpMutation = useMutation<MappingBlueprint, ApiError, MappingBlueprint, string>({
        mutationFn: (blueprint: MappingBlueprint) => deleteBlueprint(blueprint.id),
        onSuccess: async () => {
            toast({ severity: 'success', detail: 'Blueprint deleted successfully' });
            queryClient.invalidateQueries({
                queryKey,
            });
        },
    });

    return (
        <>
            <DashboardHeader
                title="Mapping Blueprints"
                end={
                    <Button
                        label="Create new blueprint"
                        icon={PrimeIcons.PLUS}
                        onClick={() => setShowBpDialog(true)}
                    ></Button>
                }
            />

            <BlueprintList
                onDeleteClick={deleteBpMutation.mutateAsync}
                blueprints={data}
                isLoading={isLoading}
                isError={isError}
            />

            <Dialog
                header="Create a new blueprint"
                visible={showBpDialog}
                onHide={() => setShowBpDialog(false)}
            >
                <BlueprintForm
                    error={
                        createBpMutation.error?.message ||
                        createBpMutation.error?.response?.data.detail
                    }
                    isLoading={createBpMutation.isPending}
                    onSubmit={createBpMutation.mutateAsync}
                    organizations={organizations}
                />
            </Dialog>
        </>
    );
}

export default ListBlueprintPage;
