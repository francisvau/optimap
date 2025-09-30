import { BlueprintForm } from '@/components/dashboard/forms/BlueprintForm';
import { BlueprintLayoutContext } from '@/layout/dashboard/BlueprintLayout';
import { useMutation } from '@tanstack/react-query';
import { Card } from 'primereact/card';
import { Skeleton } from 'primereact/skeleton';
import { JSX } from 'react';
import { useOutletContext, useRevalidator } from 'react-router';
import { BlueprintRequest, OutputDefinitionRequest } from '@/types/schemas/Blueprint';
import { SchemaEditor } from '@/components/dashboard/blueprints/schema/editor/SchemaEditor';
import { Divider } from 'primereact/divider';
import { ApiError } from '@/services/client';
import { MappingBlueprint, OutputDefinition } from '@/types/models/Blueprint';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { SchemaActions } from '@/components/dashboard/blueprints/schema/SchemaActions';
import { Button } from 'primereact/button';
import { updateBlueprint, updateOutputDefinition } from '@/services/mapping/blueprintService';
import { useSchemaBuilder } from '@/hooks/useSchemaBuilder';
import { faSave } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { Message } from 'primereact/message';

/**
 * Represents the Edit Blueprint page component.
 *
 * @returns {JSX.Element} The rendered Edit Blueprint page component.
 */
export function EditBlueprintPage(): JSX.Element {
    // Hooks
    const { revalidate } = useRevalidator();
    const { blueprint } = useOutletContext<BlueprintLayoutContext>();
    const toast = useToast();

    // Memo
    const [[outputSchema, outputSchemaDirty], builder] = useSchemaBuilder(
        blueprint.outputDefinition.jsonSchema,
    );

    const updateBp = useMutation<MappingBlueprint, ApiError, BlueprintRequest>({
        mutationFn: (data: BlueprintRequest) => updateBlueprint(blueprint.id, data),
        onSuccess: async () => {
            toast({ severity: 'success', detail: 'Blueprint updated successfully' });
            await revalidate();
        },
    });

    const updateDef = useMutation<OutputDefinition, ApiError, OutputDefinitionRequest>({
        mutationFn: (form: OutputDefinitionRequest) => updateOutputDefinition(blueprint.id, form),
        onSuccess: async () => {
            toast({ severity: 'success', detail: 'Output definition updated successfully!' });
            await revalidate();
        },
    });

    const handleUpdateOuputputDefinition = () => {
        updateDef.mutateAsync({
            jsonSchema: outputSchema,
        });
    };

    return (
        <div className="grid">
            <div className="col-12 lg:col-5">
                {blueprint ? (
                    <Card>
                        <h3 className="m-0 flex align-items-center gap-2">
                            <i className="pi pi-list" />
                            <span>Edit blueprint details</span>
                        </h3>
                        <Divider />
                        <BlueprintForm
                            isLoading={updateBp.isPending}
                            initial={blueprint}
                            onSubmit={updateBp.mutateAsync}
                            error={
                                updateBp.error?.response?.data.detail.toString() ||
                                updateBp.error?.message
                            }
                        />
                    </Card>
                ) : (
                    <Skeleton />
                )}
            </div>
            <div className="col-12 lg:col-7">
                {outputSchema ? (
                    <Card>
                        <div className="flex justify-content-between align-items-center gap-3">
                            <h3 className="m-0 flex align-items-center gap-2">
                                <i className="pi pi-bullseye" />
                                <span>Output Definition</span>
                            </h3>
                            <div className="flex gap-3">
                                <Button
                                    icon={<FontAwesomeIcon icon={faSave} />}
                                    onClick={handleUpdateOuputputDefinition}
                                    loading={updateDef.isPending}
                                    disabled={!outputSchemaDirty}
                                    tooltip="Save changes to schema"
                                    tooltipOptions={{ position: 'top' }}
                                />

                                <SchemaActions
                                    isDirty={outputSchemaDirty}
                                    schema={outputSchema}
                                    onResetClick={builder.reset}
                                    onSchemaUpload={builder.setSchema}
                                />
                            </div>
                        </div>

                        <Divider />

                        {blueprint.inputDefinitions.length > 0 && outputSchemaDirty && (
                            <Message
                                text="Note: changing (part of) the output definition schema does not automatically update the selected target schema's of the existing source mappings. Please re-select these target schemas on the respective source mappings if necessary."
                                className="mb-3"
                            />
                        )}

                        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                            <SchemaEditor schema={outputSchema} builder={builder} />
                        </div>
                    </Card>
                ) : (
                    <Skeleton />
                )}
            </div>
        </div>
    );
}

export default EditBlueprintPage;
