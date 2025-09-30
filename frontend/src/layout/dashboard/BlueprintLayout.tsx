import { CreateInputDefinitionDialog } from '@/components/dashboard/blueprints/definition/CreateInputDefinitionDialog';
import { InputDefinitionDialog } from '@/components/dashboard/blueprints/definition/InputDefinition';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { BlueprintHeader } from '@/layout/dashboard/BlueprintHeader';
import { Outlet } from '@/router/Outlet';
import {
    createInputDefinition,
    createInputDefinitionVersion,
    deleteInputDefinition,
    getInputdefinitionVersions,
    selectInputDefinitionVersion,
} from '@/services/mapping/blueprintService';
import { MappingBlueprint, InputDefinition } from '@/types/models/Blueprint';
import { isEmptySchema } from '@/utils/schema/schemaUtils';
import { useMutation, useQuery } from '@tanstack/react-query';
import { JSX, useCallback, useMemo, useState } from 'react';
import { useLoaderData, useNavigate, useParams, useRevalidator } from 'react-router';

export type BlueprintLayoutContext = {
    blueprint: MappingBlueprint;
    definition: InputDefinition;
    openDefinitionDialog: () => void;
};

/**
 * A layout component that serves as a placeholder for rendering child routes.
 *
 * @returns {JSX.Element} The rendered child route component.
 */
export function BlueprintLayout(): JSX.Element {
    const { blueprint: bpParam, definition: defParam } = useParams();
    const { revalidate } = useRevalidator();
    const navigate = useNavigate();
    const toast = useToast();
    const blueprint = useLoaderData<MappingBlueprint>();

    const [showDefinitionDialog, setShowDefinitionDialog] = useState(false);
    const [showCreateDefinitionDialog, setShowCreateDefinitionDialog] = useState(false);

    // The selected input definition.
    const definition = useMemo<InputDefinition | null>(() => {
        const definitions = blueprint.inputDefinitions;
        const definition = definitions.find((def) => def.versionGroupId === defParam);
        return definition ?? null;
    }, [blueprint, defParam]);

    const versionsQuery = useQuery({
        queryKey: ['blueprint', blueprint.id, 'inputDefinition', definition?.id, 'versions'],
        queryFn: () => getInputdefinitionVersions(blueprint.id, definition?.id),
        enabled: !!definition,
    });

    const selectVersionMutation = useMutation({
        mutationFn: (def: InputDefinition) => selectInputDefinitionVersion(blueprint.id, def.id),
        onSuccess: async () => {
            await revalidate();
            toast({
                severity: 'success',
                detail: 'Input definition version selected successfully',
            });
        },
    });

    const createVersionMutation = useMutation({
        mutationFn: (def: InputDefinition) => createInputDefinitionVersion(blueprint.id, def.id),
        onSuccess: () => {
            toast({ severity: 'success', detail: 'Input definition version created successfully' });
            revalidate();
        },
    });

    const createDefinitionMutation = useMutation({
        mutationFn: (definition: InputDefinition) => createInputDefinition(+bpParam, definition),
        onSuccess: () => {
            setShowCreateDefinitionDialog(false);
            toast({ severity: 'success', detail: 'Input definition created successfully' });
            revalidate();
        },
    });

    const deleteDefinitionMutation = useMutation({
        mutationFn: (definitionId: number) => deleteInputDefinition(+bpParam, definitionId),
        onSuccess: () => {
            toast({ severity: 'success', detail: 'Input definition deleted successfully' });
            revalidate();
        },
    });

    const handleOpenDefinitionDialog = useCallback(async () => {
        if (isEmptySchema(blueprint.outputDefinition.jsonSchema)) {
            toast({
                severity: 'warn',
                detail: 'Output definition is empty. Please build the output schema first.',
            });
            await navigate(`/dashboard/blueprints/${blueprint.id}/edit`);
        } else {
            setShowDefinitionDialog(true);
        }
    }, [blueprint, navigate, toast]);

    const handleHideDefinitionDialog = () => {
        setShowDefinitionDialog(false);
    };

    const handleSelectDefinition = async (newDefinition: InputDefinition) => {
        void setShowDefinitionDialog(false);
        await navigate(`${newDefinition.versionGroupId}`);
    };

    const handleDeleteDefinition = async (definition: InputDefinition) => {
        await deleteDefinitionMutation.mutateAsync(definition.id);
        await navigate(`/dashboard/blueprints/${blueprint.id}`);
    };

    const handleClickCreateDefinition = () => {
        setShowCreateDefinitionDialog(true);
    };

    return (
        <div className="py-4 px-3 lg:px-5 mx-auto w-12">
            <InputDefinitionDialog
                defs={blueprint.inputDefinitions}
                selected={definition}
                onSelectDefinition={handleSelectDefinition}
                onCreateClick={handleClickCreateDefinition}
                onHide={handleHideDefinitionDialog}
                visible={showDefinitionDialog}
            />

            <CreateInputDefinitionDialog
                visible={showCreateDefinitionDialog}
                onHide={() => setShowCreateDefinitionDialog(false)}
                onSubmit={createDefinitionMutation.mutateAsync}
                error={createDefinitionMutation.error?.message}
                isLoading={createDefinitionMutation.isPending}
            />

            <BlueprintHeader
                blueprint={blueprint}
                definition={definition}
                onVersionClick={selectVersionMutation.mutate}
                onVersionCreateClick={createVersionMutation.mutate}
                versions={versionsQuery.data}
                onDefinitionClick={handleOpenDefinitionDialog}
                onDeleteDefinitionClick={handleDeleteDefinition}
            />

            <div className="my-4" />

            <Outlet
                context={{
                    blueprint,
                    definition,
                    openDefinitionDialog: handleOpenDefinitionDialog,
                }}
            />
        </div>
    );
}
