import { JSONSchema, SchemaPathString } from '@/types/Schema';

export type BlueprintRequest = {
    name?: string;
    description?: string;
    userId?: string;
    organizationId?: number;
};

export type InputDefinitionRequest = {
    name?: string;
    description?: string;
};

export type OutputDefinitionRequest = {
    jsonSchema?: object;
};

export type SourceMappingRequest = {
    name?: string;
    inputJsonSchema?: JSONSchema;
    jsonataMapping?: string;
    outputJsonSchema?: JSONSchema;
    targetPath?: SchemaPathString;
};

export type JsonataGenerationResponse = {
    mapping: string;
    retries: number;
    corrupted: boolean;
    errorMessage: string | null;
};
