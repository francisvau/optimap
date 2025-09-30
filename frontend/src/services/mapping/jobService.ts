import { apiClient } from '@/services/client';
import { endpoints } from '@/services/endpoints';
import { MappingJob, MappingJobExecution } from '@/types/models/Job';
import { CreateJobRequest, UpdateJobRequest } from '@/types/schemas/Job';
import { AxiosProgressEvent } from 'axios';

/**
 * Creates a new job using the provided form data.
 *
 * @param form - The data required to create a job, adhering to the `JobRequest` structure.
 * @returns The data from the API response after successfully creating the job.
 */
export async function createJob(form: CreateJobRequest): Promise<MappingJob> {
    const response = await apiClient.post<MappingJob>(endpoints.jobs.create, form);
    return response.data;
}

/**
 * Deletes a job by its ID.
 *
 * @param id - The unique identifier of the job to be deleted.
 * @returns A promise that resolves to the deleted `MappingJob` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function deleteJob(id: number): Promise<MappingJob> {
    const response = await apiClient.delete<MappingJob>(
        endpoints.jobs.delete.replace('{jobId}', id.toString()),
    );
    return response.data;
}

/**
 * Updates an existing job with the provided form data.
 *
 * @param id - The unique identifier of the job to be updated.
 * @param form - The data to update the job, adhering to the `JobRequest` structure.
 * @returns A promise that resolves to the updated `MappingJob` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function updateJob(id: number, form: UpdateJobRequest): Promise<MappingJob> {
    const response = await apiClient.patch<MappingJob>(
        endpoints.jobs.update.replace('{jobId}', id.toString()),
        form,
    );
    return response.data;
}

/**
 * Fetches the mapping jobs associated with a specific organization.
 *
 * @param id - The unique identifier of the organization.
 * @returns A promise that resolves to an AxiosResponse containing an array of MappingJob objects.
 */
export async function getOrganizationJobs(id: number): Promise<MappingJob[]> {
    const response = await apiClient.get<MappingJob[]>(
        endpoints.jobs.getByOrgId.replace('{orgId}', id.toString()),
    );
    return response.data;
}

/**
 * Fetches the mapping jobs associated with a specific user.
 *
 * @param id - The unique identifier of the user.
 * @returns A promise that resolves to an AxiosResponse containing an array of MappingJob objects.
 */
export async function getUserJobs(id: number): Promise<MappingJob[]> {
    const response = await apiClient.get<MappingJob[]>(
        endpoints.jobs.getByUserId.replace('{userId}', id.toString()),
    );
    return response.data;
}

/**
 * Fetches a mapping job by its unique identifier.
 *
 * @param id - The unique identifier of the job to retrieve.
 * @returns A promise that resolves to the retrieved `MappingJob` object.
 * @throws An error if the API request fails or the job is not found.
 */
export async function getJob(id: number): Promise<MappingJob> {
    const response = await apiClient.get<MappingJob>(
        endpoints.jobs.getById.replace('{jobId}', id.toString()),
    );
    return response.data;
}

/**
 * Starts the execution of a job with the specified ID and source mapping ID.
 *
 * @param jobId - The unique identifier of the job to execute.
 * @param sourceMappingId - The unique identifier of the source mapping to execute.
 * @param data - The form data to be sent with the request.
 * @param onUploadProgress - Optional callback function to track upload progress.
 * @returns A promise that resolves to the response data from the API.
 */
export async function startJobExecution(
    jobId: number,
    sourceMappingId: number,
    data: FormData,
    onUploadProgress?: (progress: AxiosProgressEvent) => void,
): Promise<MappingJobExecution> {
    const endpoint = endpoints.jobs.startExecution
        .replace('{jobId}', jobId.toString())
        .replace('{sourceMappingId}', sourceMappingId.toString());

    const response = await apiClient.post(endpoint, data, {
        onUploadProgress,
    });

    return response.data;
}

/**
 * Starts the execution of a dynamic job with the specified ID and source mapping ID.
 *
 * @param jobUuid - The unique identifier of the job
 * @param sourceMappingId - The unique identifier of the source mapping to execute.
 * @param data - The form data to be sent with the request.
 * @param forward - Optional flag to indicate whether to forward the data.
 *
 * @returns A promise that resolves to the response data from the API.
 */
export async function dynamicJobExecution(
    jobUuid: string,
    sourceMappingId: number,
    data: object,
    forward: boolean = true,
): Promise<object> {
    const endpoint = endpoints.jobs.dynamicExection
        .replace('{uuid}', jobUuid.toString())
        .replace('{sourceMappingId}', sourceMappingId.toString());
    const response = await apiClient.post(endpoint, { data, forward });
    return response.data;
}
