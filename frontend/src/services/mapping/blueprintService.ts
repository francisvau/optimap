import { apiClient } from '@/services/client';
import { endpoints } from '@/services/endpoints';
import {
    BlueprintRequest,
    InputDefinitionRequest,
    JsonataGenerationResponse,
    OutputDefinitionRequest,
    SourceMappingRequest,
} from '@/types/schemas/Blueprint';
import {
    ExtractJSONSchemaResponse,
    InputDefinition,
    MappingBlueprint,
    OutputDefinition,
    SourceMapping,
} from '@/types/models/Blueprint';

/**
 * Creates a new blueprint using the provided form data.
 *
 * @param form - The data required to create a blueprint, adhering to the `BlueprintRequest` structure.
 * @returns The data from the API response after successfully creating the blueprint.
 */
export async function createBlueprint(form: BlueprintRequest): Promise<MappingBlueprint> {
    const response = await apiClient.post<MappingBlueprint>(endpoints.blueprints.create, form);
    return response.data;
}

/**
 * Deletes a blueprint by its ID.
 *
 * @param id - The unique identifier of the blueprint to be deleted.
 * @returns A promise that resolves to the deleted `MappingBlueprint` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function deleteBlueprint(id: number): Promise<MappingBlueprint> {
    const response = await apiClient.delete<MappingBlueprint>(
        endpoints.blueprints.delete.replace('{blueprintId}', id.toString()),
    );
    return response.data;
}

/**
 * Updates an existing blueprint with the provided form data.
 *
 * @param id - The unique identifier of the blueprint to be updated.
 * @param form - The data to update the blueprint, adhering to the `BlueprintRequest` structure.
 * @returns A promise that resolves to the updated `MappingBlueprint` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function updateBlueprint(
    id: number,
    form: BlueprintRequest,
): Promise<MappingBlueprint> {
    const response = await apiClient.patch<MappingBlueprint>(
        endpoints.blueprints.update.replace('{blueprintId}', id.toString()),
        form,
    );
    return response.data;
}

/**
 * Fetches the mapping blueprints associated with a specific organization.
 *
 * @param id - The unique identifier of the organization.
 * @returns A promise that resolves to an AxiosResponse containing an array of MappingBlueprint objects.
 */
export async function getOrganizationBlueprints(id: number): Promise<MappingBlueprint[]> {
    const response = await apiClient.get<MappingBlueprint[]>(
        endpoints.blueprints.getByOrgId.replace('{orgId}', id.toString()),
    );
    return response.data;
}

/**
 * Fetches the mapping blueprints associated with a specific user.
 *
 * @param id - The unique identifier of the user.
 * @returns A promise that resolves to an AxiosResponse containing an array of MappingBlueprint objects.
 */
export async function getUserBlueprints(id: number): Promise<MappingBlueprint[]> {
    const response = await apiClient.get<MappingBlueprint[]>(
        endpoints.blueprints.getByUserId.replace('{userId}', id.toString()),
    );
    return response.data;
}

/**
 * Fetches a mapping blueprint by its unique identifier.
 *
 * @param id - The unique identifier of the blueprint to retrieve.
 * @returns A promise that resolves to the retrieved `MappingBlueprint` object.
 * @throws An error if the API request fails or the blueprint is not found.
 */
export async function getBlueprint(id: number): Promise<MappingBlueprint> {
    const response = await apiClient.get<MappingBlueprint>(
        endpoints.blueprints.getById.replace('{blueprintId}', id.toString()),
    );
    return response.data;
}

/**
 * Creates a new input definition for a specified blueprint.
 *
 * @param blueprintId - The unique identifier of the blueprint for which the input definition is being created.
 * @param definition - The form data representing the input definition to be created.
 * @returns A promise that resolves to the updated `MappingBlueprint` object.
 *
 * @throws An error if the API request fails.
 */
export async function createInputDefinition(
    blueprintId: number,
    definition: InputDefinitionRequest,
): Promise<MappingBlueprint> {
    const endpoint = endpoints.blueprints.inputDefinitions.create.replace(
        '{blueprintId}',
        blueprintId.toString(),
    );
    const response = await apiClient.post<MappingBlueprint>(endpoint, definition);
    return response.data;
}

/**
 * Deletes an input definition from a specified blueprint.
 *
 * @param blueprintId - The unique identifier of the blueprint from which the input definition will be deleted.
 * @param definitionId - The unique identifier of the input definition to be deleted.
 */
export async function deleteInputDefinition(
    blueprintId: number,
    definitionId: number,
): Promise<void> {
    const endpoint = endpoints.blueprints.inputDefinitions.delete
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString());
    await apiClient.delete<MappingBlueprint>(endpoint);
}

/**
 * Fetches the input definition mappings for a specific blueprint and definition.
 *
 * @param blueprintId - The unique identifier of the blueprint.
 * @param definitionId - The unique identifier of the input definition.
 * @returns A promise that resolves to a `MappingBlueprint` object containing the input definition mappings.
 * @throws An error if the API request fails.
 */
export async function getInputDefinitionMappings(
    blueprintId: number,
    definitionId: number,
): Promise<MappingBlueprint> {
    const endpoint = endpoints.blueprints.inputDefinitions.create
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString());

    const response = await apiClient.get<MappingBlueprint>(endpoint);

    return response.data;
}

/**
 * Fetches the versions of an input definition for a specific blueprint.
 *
 * @param blueprintId - The unique identifier of the blueprint.
 * @param definitionId - The unique identifier of the input definition.
 *
 * @returns A promise that resolves to a `MappingBlueprint` object containing the input definition versions.
 */
export async function getInputdefinitionVersions(
    blueprintId: number,
    definitionId: number,
): Promise<InputDefinition[]> {
    const endpoint = endpoints.blueprints.inputDefinitions.versions.get
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString());
    const response = await apiClient.get<InputDefinition[]>(endpoint);
    return response.data;
}

/**
 * Creates a new version of an input definition for a specific blueprint.
 *
 * @param blueprintId - The unique identifier of the blueprint.
 * @param definitionId - The unique identifier of the input definition.
 *
 * @returns A promise that resolves to the created `InputDefinition` object.
 */
export async function createInputDefinitionVersion(
    blueprintId: number,
    definitionId: number,
): Promise<InputDefinition> {
    const endpoint = endpoints.blueprints.inputDefinitions.versions.create
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString());
    const response = await apiClient.post<InputDefinition>(endpoint);
    return response.data;
}

/**
 * Selects a specific version of an input definition for a given blueprint.
 *
 * @param blueprintId - The unique identifier of the blueprint.
 * @param definitionId - The unique identifier of the input definition.
 * @returns
 */
export async function selectInputDefinitionVersion(
    blueprintId: number,
    definitionId: number,
): Promise<InputDefinition> {
    const endpoint = endpoints.blueprints.inputDefinitions.versions.select
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString());
    const response = await apiClient.post<InputDefinition>(endpoint);
    return response.data;
}

/**
 * Updates the output definition of a specified blueprint.
 *
 * @param blueprintId - The unique identifier of the blueprint to update.
 * @param definition - The new output definition to be applied to the blueprint.
 * @returns A promise that resolves to the updated `MappingBlueprint` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function updateOutputDefinition(
    blueprintId: number,
    definition: OutputDefinitionRequest,
): Promise<OutputDefinition> {
    const endpoint = endpoints.blueprints.outputDefinitions.update.replace(
        '{blueprintId}',
        blueprintId.toString(),
    );
    const response = await apiClient.patch<OutputDefinition>(endpoint, definition);
    return response.data;
}

/**
 * Creates a new source mapping for a specific blueprint and input definition.
 *
 * @param blueprintId - The ID of the blueprint for which the source mapping is being created.
 * @param definitionId - The ID of the input definition associated with the source mapping.
 * @param mapping - The source mapping form data to be sent in the request.
 * @returns A promise that resolves to the created source mapping.
 *
 * @throws An error if the API request fails.
 */
export async function createSourceMapping(
    blueprintId: number,
    definitionId: number,
    mapping: SourceMappingRequest,
): Promise<SourceMapping> {
    const endpoint = endpoints.blueprints.inputDefinitions.sourceMappings.create
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString());
    const response = await apiClient.post<SourceMapping>(endpoint, mapping);
    return response.data;
}

/**
 * Updates an existing source mapping for a specific blueprint and input definition.
 *
 * @param blueprintId - The ID of the blueprint for which the source mapping is being updated.
 * @param definitionId - The ID of the input definition associated with the source mapping.
 * @param mappingId - The ID of the source mapping to be updated.
 * @param mapping - The updated source mapping form data to be sent in the request.
 * @returns A promise that resolves to the updated source mapping.
 *
 * @throws An error if the API request fails.
 */
export async function updateSourceMapping(
    blueprintId: number,
    definitionId: number,
    mappingId: number,
    mapping: SourceMappingRequest,
): Promise<SourceMapping> {
    const endpoint = endpoints.blueprints.inputDefinitions.sourceMappings.update
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString())
        .replace('{mappingId}', mappingId.toString());
    const response = await apiClient.patch<SourceMapping>(endpoint, mapping);
    return response.data;
}

/**
 * Deletes a source mapping for a specific blueprint and input definition.
 *
 * @param blueprintId - The ID of the blueprint from which the source mapping will be deleted.
 * @param definitionId - The ID of the input definition associated with the source mapping.
 * @param mappingId - The ID of the source mapping to be deleted.
 * @returns A promise that resolves to the deleted source mapping.
 *
 * @throws An error if the API request fails.
 */
export async function deleteSourceMapping(
    blueprintId: number,
    definitionId: number,
    mappingId: number,
): Promise<void> {
    const endpoint = endpoints.blueprints.inputDefinitions.sourceMappings.delete
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString())
        .replace('{mappingId}', mappingId.toString());
    await apiClient.delete<SourceMapping>(endpoint);
}

/**
 * Generates a JSONata mapping for a specific source mapping.
 *
 * @param blueprintId - The ID of the blueprint for which to generate the JSONata mapping.
 * @param definitionId - The ID of the input definition associated with the source mapping.
 * @param mappingId - The ID of the source mapping for which to generate the JSONata mapping.
 * @param modelId - Optional model ID to be used in the generation process.
 *
 * @returns A promise that resolves to the generated JSONata mapping as a string.
 *
 * @throws An error if the API request fails.
 */
export async function generateJsonataMapping(
    blueprintId: number,
    definitionId: number,
    mappingId: number,
    modelId?: string,
): Promise<JsonataGenerationResponse> {
    const endpoint = endpoints.blueprints.inputDefinitions.sourceMappings.generate
        .replace('{blueprintId}', blueprintId.toString())
        .replace('{definitionId}', definitionId.toString())
        .replace('{mappingId}', mappingId.toString());

    const response = await apiClient.post(endpoint, {
        model: modelId,
    });

    return response.data;
}

/**
 * Retrieves a mapping job by its ID.
 * @param file
 * @returns A promise that resolves to an AxiosResponse containing the requested MappingJob.
 */
export async function extractSchemaFromExampleData(file: File): Promise<ExtractJSONSchemaResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<ExtractJSONSchemaResponse>(
        endpoints.schema.extraction,
        formData,
    );
    return response.data;
}
