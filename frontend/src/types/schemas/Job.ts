import { JobType } from '@/types/models/Job';

export type CreateJobRequest = {
    name?: string | null;
    type: JobType;
    blueprintId: number;
    inputDefinitionId: number;
    externalApiEndpoint?: string | null;
};

export type UpdateJobRequest = {
    name?: string | null;
};
