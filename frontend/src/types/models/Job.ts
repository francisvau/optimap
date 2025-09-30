import { InputDefinition, MappingBlueprint, SourceMapping } from '@/types/models/Blueprint';
import { Organization } from '@/types/models/Organization';
import { User } from '@/types/models/User';

export enum JobType {
    STATIC = 'STATIC',
    DYNAMIC = 'DYNAMIC',
}

export enum JobStatus {
    PENDING = 'PENDING',
    RUNNING = 'RUNNING',
    SUCCESS = 'SUCCESS',
    FAILED = 'FAILED',
}

export interface MappingJob {
    id: number;
    uuid: string | null;
    externalApiEndpoint: string | null;
    name: string | null;
    type: JobType;
    status: JobStatus;
    file: string;

    blueprintId: number;
    blueprint?: MappingBlueprint;

    userId: number;
    user?: User;

    inputDefinitionId: number;
    inputDefinition: InputDefinition;

    organizationId?: number | null;
    organization?: Organization | null;

    executions: MappingJobExecution[];

    executedAt: Date | null;
    createdAt: Date;
    updatedAt?: Date;
}

export interface MappingJobExecution {
    id: number;
    dataSizeBytes: number;
    status: JobStatus;
    createdAt: Date;
    startedAt: Date | null;
    completedAt: Date | null;
    attempts: number;
    durationSeconds: number | null;
    errorMessage: string | null;
    mappingJob?: MappingJob;
    sourceMapping?: SourceMapping;
    originalFileName: string;
}
