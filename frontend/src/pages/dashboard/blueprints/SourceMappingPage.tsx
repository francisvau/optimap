import { SchemaEditor } from '@/components/dashboard/blueprints/schema/editor/SchemaEditor';
import { BlueprintLayoutContext } from '@/layout/dashboard/BlueprintLayout';
import { Divider } from 'primereact/divider';
import { JSX, MouseEvent, useEffect, useMemo, useState } from 'react';
import { useNavigate, useOutletContext, useParams, useRevalidator } from 'react-router';
import { Button } from 'primereact/button';
import { PrimeIcons } from 'primereact/api';
import { SchemaActions } from '@/components/dashboard/blueprints/schema/SchemaActions';
import { JSONSchema, SubSchemaSelection } from '@/types/Schema';
import { SourceMapping } from '@/types/models/Blueprint';
import { Card } from 'primereact/card';
import { CreateSourceMappingDialog } from '@/components/dashboard/blueprints/mapping/CreateSourceMappingDialog';
import { useMutation, useQuery } from '@tanstack/react-query';
import { JsonataGenerationResponse, SourceMappingRequest } from '@/types/schemas/Blueprint';
import {
    createSourceMapping,
    deleteSourceMapping,
    generateJsonataMapping,
    updateSourceMapping,
} from '@/services/mapping/blueprintService';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { JSONataEditor } from '@/components/editor/JSONataEditor.tsx';
import { Dropdown } from 'primereact/dropdown';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faCopy,
    faMagnifyingGlass,
    faObjectUngroup,
    faSave,
    faSitemap,
} from '@fortawesome/free-solid-svg-icons';
import { isEmptySchema } from '@/utils/schema/schemaUtils';
import { Message } from 'primereact/message';
import { useSchemaBuilder } from '@/hooks/useSchemaBuilder';
import { SelectSchemaDialog } from '@/components/dashboard/blueprints/schema/SelectSchemaDialog';

import { SaveMappingButton } from '@/components/shared/SaveMappingButton.tsx';
import { GenerateRulesButton } from '@/components/shared/GenerateRulesButton.tsx';
import { Splitter, SplitterPanel } from 'primereact/splitter';
import { JSONSchemaFaker } from 'json-schema-faker';

import jsonata from 'jsonata';

import './SourceMappingPage.scss';
import { getModelsForOrganization } from '@/services/organizationService';

/**
 * Represents the BlueprintPage component.
 *
 * This component renders a simple page with a title and a description
 * indicating that it is the blueprint page.
 *
 * @returns {JSX.Element} The rendered BlueprintPage component.
 */
function SourceMappingPage(): JSX.Element {
    const toast = useToast();
    const navigate = useNavigate();

    const { revalidate } = useRevalidator();
    const { mapping: mapParam, definition: defParam } = useParams();

    const context = useOutletContext<BlueprintLayoutContext>();
    const { blueprint, definition, openDefinitionDialog } = context;

    const [draftJsonataMapping, setDraftJsonataMapping] = useState<string | null>(null);
    const [showExampleOutput, setShowExampleOutput] = useState(false);
    const [exampleOutput, setExampleOutput] = useState(null);
    const [exampleInput, setExampleInput] = useState(null);
    const [showSelectSchemaDialog, setShowSelectSchemaDialog] = useState(false);
    const [showCreateMappingDialog, setShowCreateMappingDialog] = useState(false);
    const [, setAdvancedMode] = useState(false);

    const mapping = useMemo<SourceMapping | null>(() => {
        return (
            definition?.sourceMappings.find((map) => map.id === parseInt(mapParam)) ||
            definition?.sourceMappings[0] ||
            null
        );
    }, [mapParam, definition]);

    const jsonataMapping = useMemo(
        () => draftJsonataMapping ?? mapping?.jsonataMapping,
        [draftJsonataMapping, mapping],
    );

    const [[inputSchema, inputSchemaDirty], builder] = useSchemaBuilder(mapping?.inputJsonSchema);

    const modelsQuery = useQuery({
        enabled: blueprint.organizationId != null,
        queryKey: ['organization', blueprint.organizationId, 'models'],
        queryFn: () => getModelsForOrganization(blueprint.organizationId),
    });

    const createMappingMutation = useMutation({
        mutationFn: (mapping: SourceMappingRequest) => {
            return createSourceMapping(blueprint.id, definition.id, mapping);
        },
        onSuccess: async (newMapping: SourceMapping) => {
            toast({ severity: 'success', detail: 'Source mapping created successfully!' });
            await revalidate();
            await navigate(
                `/dashboard/blueprints/${blueprint.id}/${definition.versionGroupId}/${newMapping.id}`,
            );
        },
    });

    const updateMappingMutation = useMutation({
        mutationFn: (form: SourceMappingRequest) => {
            return updateSourceMapping(blueprint.id, definition.id, mapping.id, form);
        },
        onSuccess: async () => {
            await revalidate();
            toast({ severity: 'success', detail: 'Source mapping updated successfully!' });
        },
    });

    const deleteMappingMutation = useMutation({
        mutationFn: () => deleteSourceMapping(blueprint.id, definition?.id, mapping?.id),
        onSuccess: async () => {
            await revalidate();
            toast({ severity: 'success', detail: 'Input schema deleted successfully!' });
        },
    });

    const generateMappingMutation = useMutation({
        mutationFn: (modelId?: string) =>
            generateJsonataMapping(blueprint.id, definition.id, mapping.id, modelId),
        onSuccess: async (result: JsonataGenerationResponse) => {
            if (!result.corrupted) {
                toast({
                    severity: 'success',
                    detail: 'The engine successfully generated a mapping that validates against the target schema! Please double check to ensure it is correct.',
                });
            } else {
                toast({
                    severity: 'warn',
                    summary: 'The engine generated a mapping, but is unsure if it is correct',
                });
            }

            setAdvancedMode(true);
            setDraftJsonataMapping(result.mapping);
        },
        onError: (error) => {
            toast({
                severity: 'error',
                summary: 'Mapping generation failed',
                detail: error.message,
            });
        },
    });

    const isGenerationDisabled = useMemo(
        () => isEmptySchema(mapping?.outputJsonSchema) || isEmptySchema(mapping?.inputJsonSchema),
        [mapping],
    );

    const forceShowCreateMappingDialog = useMemo(
        () => definition && mapping == null && !createMappingMutation.submittedAt,
        [definition, mapping, createMappingMutation.submittedAt],
    );

    const forceSelectSchemaDialog = useMemo(
        () => mapping && isEmptySchema(mapping.outputJsonSchema),
        [mapping],
    );

    // Open the definition dialog if none was selected yet.
    useEffect(() => {
        if (!defParam) {
            openDefinitionDialog();
        }
    }, [defParam, openDefinitionDialog]);

    // Generate a input JSON object from the schema.
    // Used for the live preview.
    useEffect(() => {
        if (!inputSchema) return;

        JSONSchemaFaker.option({
            minItems: 1,
            maxItems: 2,
            useExamplesValue: true,
            useDefaultValue: true,
        });

        try {
            const generatedInput = JSONSchemaFaker.generate(inputSchema);
            setExampleInput(generatedInput);
        } catch (error) {
            setExampleInput('Error:' + error.message);
        }
    }, [inputSchema]);

    // Evaluate the input JSON object with the JSONata expression.
    // Adds a debounce to prevent frequent updates.
    useEffect(() => {
        const timeoutId = setTimeout(async () => {
            try {
                if (!jsonataMapping || !exampleInput) return;

                const expression = jsonata(jsonataMapping);
                const result = await expression.evaluate(exampleInput);
                setExampleOutput(result);
            } catch (error) {
                setExampleOutput('Error:' + error.message);
            }
        }, 750);

        return () => clearTimeout(timeoutId);
    }, [jsonataMapping, exampleInput]);

    const handleSelectSourceMapping = (mapping: SourceMapping) => {
        navigate(
            `/dashboard/blueprints/${blueprint.id}/${definition.versionGroupId}/${mapping.id}`,
        );
    };

    const handleUpdateInputSchema = async () => {
        await updateMappingMutation.mutateAsync({
            inputJsonSchema: inputSchema,
        });
    };

    const handleCopySchema = async (schema: JSONSchema) => {
        await navigator.clipboard.writeText(JSON.stringify(schema, null, 2));
        toast({ severity: 'success', detail: 'Schema is copied to clipboard!' });
    };

    const handleSelectionSave = async (selection: SubSchemaSelection) => {
        if (selection) {
            await updateMappingMutation.mutateAsync({
                outputJsonSchema: selection.jsonSchema,
                targetPath: selection.targetPath,
            });

            setShowSelectSchemaDialog(false);

            if (!isEmptySchema(mapping.inputJsonSchema)) {
                await generateMappingMutation.mutateAsync(undefined);
            }
        }
    };

    const handleJsonataMappingChange = (value: string) => {
        updateMappingMutation.mutateAsync({
            jsonataMapping: value,
        });
    };

    const mappingDropdownItemTemplate = (option: SourceMapping) => {
        return (
            <div className="flex gap-3 justify-content-between align-items-center w-full">
                <span>{option.name}</span>
                <Button
                    loading={deleteMappingMutation.isPending}
                    severity="danger"
                    icon={PrimeIcons.TRASH}
                    onClick={(e: MouseEvent) => {
                        e.stopPropagation();
                        deleteMappingMutation.mutateAsync();
                    }}
                    disabled={deleteMappingMutation.isPending}
                    tooltip="Delete mapping"
                    text
                />
            </div>
        );
    };

    return (
        <>
            <CreateSourceMappingDialog
                visible={forceShowCreateMappingDialog || showCreateMappingDialog}
                onHide={() => setShowCreateMappingDialog(false)}
                header="Create a Source Mapping"
                forced={forceShowCreateMappingDialog}
                error={createMappingMutation.error?.message}
                isLoading={createMappingMutation.isPending}
                onSubmit={createMappingMutation.mutateAsync}
                modal
            />

            {mapping && (
                <SelectSchemaDialog
                    header="Select a target schema"
                    schema={blueprint.outputDefinition.jsonSchema}
                    visible={forceSelectSchemaDialog || showSelectSchemaDialog}
                    closable={!forceSelectSchemaDialog}
                    targetSchema={blueprint.outputDefinition.jsonSchema}
                    initial={mapping}
                    onHide={() => setShowSelectSchemaDialog(false)}
                    onSelectionSave={handleSelectionSave}
                    modal
                >
                    <Message text="Use the schema selector below to define the target schema for this source mapping." />
                </SelectSchemaDialog>
            )}

            {mapping && (
                <>
                    <h4 className="flex align-items-center justify-content-between gap-3">
                        <span>Selected Source Mapping</span>
                        <Button
                            icon={PrimeIcons.PLUS}
                            label="Create New"
                            onClick={() => setShowCreateMappingDialog(true)}
                            text
                        />
                    </h4>
                    <Dropdown
                        className="w-full"
                        options={definition.sourceMappings}
                        value={mapping}
                        onChange={(e) => handleSelectSourceMapping(e.value)}
                        itemTemplate={mappingDropdownItemTemplate}
                        valueTemplate={mappingDropdownItemTemplate}
                    />
                </>
            )}

            {mapping ? (
                <div className="grid mt-4 align-items-stretch">
                    <div className="col-12 lg:col-4">
                        <Card>
                            <div className="flex justify-content-between align-items-center gap-3">
                                <h3 className="m-0 flex gap-2">
                                    <span>Input Schema</span>
                                </h3>

                                <div className="flex gap-2">
                                    <Button
                                        icon={<FontAwesomeIcon icon={faCopy} />}
                                        onClick={handleCopySchema.bind(null, inputSchema)}
                                        disabled={inputSchemaDirty}
                                        outlined
                                        tooltip="Copy schema to clipboard"
                                        tooltipOptions={{ position: 'top' }}
                                    />
                                    <Button
                                        icon={<FontAwesomeIcon icon={faSave} />}
                                        onClick={handleUpdateInputSchema}
                                        loading={updateMappingMutation.isPending}
                                        disabled={!inputSchemaDirty}
                                        tooltip="Save changes to schema"
                                        tooltipOptions={{ position: 'top' }}
                                    />
                                    <SchemaActions
                                        isDirty={inputSchemaDirty}
                                        schema={inputSchema}
                                        onResetClick={builder.reset}
                                        onSchemaUpload={builder.setSchema}
                                    />
                                </div>
                            </div>
                            <Divider />
                            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                                <SchemaEditor schema={inputSchema} builder={builder} target={''} />
                            </div>
                        </Card>
                    </div>
                    <div className="col-12 lg:col-8">
                        <Card>
                            <div className="flex justify-content-between align-items-center gap-3">
                                <div className="flex gap-2 flex-1 align-items-center">
                                    <Button
                                        onClick={() => setShowExampleOutput(!showExampleOutput)}
                                        icon={
                                            !showExampleOutput ? (
                                                <FontAwesomeIcon icon={faMagnifyingGlass} />
                                            ) : (
                                                <FontAwesomeIcon icon={faSitemap} />
                                            )
                                        }
                                        tooltip={
                                            !showExampleOutput
                                                ? 'View Live Preview'
                                                : 'View Target Schema'
                                        }
                                        outlined
                                    />
                                    <h3 className="m-0 flex gap-2">
                                        <span>
                                            {showExampleOutput ? 'Live Preview' : 'Target Schema'}
                                        </span>
                                    </h3>
                                </div>
                                <Button
                                    icon={<FontAwesomeIcon icon={faCopy} />}
                                    onClick={handleCopySchema.bind(null, mapping.outputJsonSchema)}
                                    outlined
                                    tooltip="Copy schema to clipboard"
                                    tooltipOptions={{ position: 'top' }}
                                />
                                <SaveMappingButton
                                    disabled={
                                        draftJsonataMapping === mapping.jsonataMapping ||
                                        !jsonataMapping ||
                                        !draftJsonataMapping
                                    }
                                    loading={updateMappingMutation.isPending}
                                    onClick={() => {
                                        handleJsonataMappingChange(jsonataMapping);
                                    }}
                                />
                                <GenerateRulesButton
                                    disabled={isGenerationDisabled}
                                    onClick={generateMappingMutation.mutateAsync}
                                    loading={generateMappingMutation.isPending}
                                    models={modelsQuery.data}
                                />
                                <Button
                                    icon={<FontAwesomeIcon icon={faObjectUngroup} />}
                                    label="Select Target Schema"
                                    onClick={() => setShowSelectSchemaDialog(true)}
                                    text
                                />
                            </div>

                            <Divider />

                            <div style={{ height: '600px' }} className="overflow-auto">
                                <Splitter layout="horizontal" className="w-full">
                                    <SplitterPanel size={50} className="overflow-hidden">
                                        {isEmptySchema(mapping.outputJsonSchema) ? (
                                            <Message
                                                className="w-full"
                                                text="No target (sub)schema selected yet!"
                                            />
                                        ) : (
                                            <>
                                                {showExampleOutput && exampleInput ? (
                                                    <div
                                                        style={{ height: '600px' }}
                                                        className="w-full"
                                                    >
                                                        <JSONataEditor
                                                            mapping={JSON.stringify(
                                                                exampleOutput,
                                                                null,
                                                                2,
                                                            )}
                                                            readOnly={true}
                                                        />
                                                    </div>
                                                ) : (
                                                    <SchemaEditor
                                                        schema={mapping.outputJsonSchema}
                                                        target={mapping.targetPath}
                                                    />
                                                )}
                                            </>
                                        )}
                                    </SplitterPanel>
                                    <SplitterPanel className="overflow-hidden">
                                        <div style={{ height: '600px' }} className="w-full">
                                            <JSONataEditor
                                                onChange={setDraftJsonataMapping}
                                                mapping={jsonataMapping}
                                                inputSchema={inputSchema}
                                                disableSave={
                                                    draftJsonataMapping ===
                                                        mapping.jsonataMapping || !jsonataMapping
                                                }
                                                loadingSave={updateMappingMutation.isPending}
                                                onSave={handleJsonataMappingChange}
                                                saveSuccess={updateMappingMutation.isSuccess}
                                                generatingSuccess={updateMappingMutation.isSuccess}
                                                disableGenerate={isGenerationDisabled}
                                                loadingGenerate={generateMappingMutation.isPending}
                                                onGenerate={() =>
                                                    generateMappingMutation.mutateAsync(undefined)
                                                }
                                            />
                                        </div>
                                    </SplitterPanel>
                                </Splitter>
                            </div>
                        </Card>
                    </div>
                </div>
            ) : (
                <div className="flex flex-column align-items-center justify-content-center">
                    <h2 className="m-0">No mapping found</h2>
                    <p className="text-300">Please select a mapping to view its details.</p>
                </div>
            )}
        </>
    );
}

export default SourceMappingPage;
