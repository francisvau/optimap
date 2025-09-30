import { Organization } from '@/types/models/Organization';
import { User } from '@/types/models/User';
import { JSONSchema, SchemaPathString } from '@/types/Schema';
import { SupportedDataType } from '@/utils/fileUtils';

// A mapping contains an input schema extracted from a data source,
// a jsonata mapping and and output schema.
export interface SourceMapping {
    id: number;
    name: string;
    fileType: SupportedDataType;
    inputJsonSchema: JSONSchema;
    jsonataMapping: string;
    outputJsonSchema: JSONSchema;
    targetPath?: SchemaPathString;
}

// An input definition contains multiple mappings.
// These mappings represent different data sources mapped
// to a different schema, e.g. JSON customer data and JSON order data.
export interface InputDefinition {
    id: number;
    name: string;
    description: string;
    sourceMappings: SourceMapping[];
    blueprint?: MappingBlueprint;
    version: number;
    versionGroupId: string;
    isSelected: boolean;
}

// The output definition is the final schema of the
// data after the mapping is applied. Its primary purpose
// is to join the output of the different input definitions into one output
// definition. In case of one mapping in the input definition, these output schemas
// are the same.
export interface OutputDefinition {
    id: number;
    name: string;
    description: string;
    jsonSchema: JSONSchema;
}

// A mapping blueprint consists of one or multiple
// input definitions and one output definition.
export interface MappingBlueprint {
    id: number;
    name: string;
    description: string;
    usageCount: number;
    inputDefinitions: InputDefinition[];
    outputDefinition: OutputDefinition;
    organizationId: number | null;
    organization?: Organization | null;
    user?: User;
    createdAt: Date;
    updatedAt?: Date;
}

export interface ExtractJSONSchemaResponse {
    jsonSchema: JSONSchema;
}
