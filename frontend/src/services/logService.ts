import { endpoints } from '@/services/endpoints.ts';
import { apiClient } from '@/services/client.ts';
import { Log } from '@/types/models/Log.ts';

/**
 * Fetches the logs for a specific user.
 * @param userId - The ID of the user whose logs to fetch.
 * @returns {Promise<Log[]>} - A promise that resolves to an array of logs for the specified user.
 */
export async function getUserLogs(userId: number): Promise<Log[]> {
    const response = await apiClient.get<Log[]>(
        endpoints.logs.user.replace('{userId}', userId.toString()),
    );
    return response.data;
}

/**
 * Fetches the logs for a specific organization.
 * @param organizationId - The ID of the organization whose logs to fetch.
 * @returns {Promise<Log[]>} - A promise that resolves to an array of logs for the specified organization.
 */
export async function getOrganizationLogs(organizationId: number): Promise<Log[]> {
    const response = await apiClient.get<Log[]>(
        endpoints.logs.organization.replace('{orgId}', organizationId.toString()),
    );
    return response.data;
}

/**
 * Fetches the logs for a specific level.
 * @param level - The level of logs to fetch (e.g., 'INFO', 'ERROR').
 * @returns {Promise<Log[]>} - A promise that resolves to an array of logs for the specified level.
 */
export async function getLogsLevel(level: string): Promise<Log[]> {
    const response = await apiClient.get<Log[]>(endpoints.logs.level.replace('{level}', level));
    return response.data;
}

/**
 * Fetches all logs.
 * @returns {Promise<Log[]>} - A promise that resolves to an array of all logs.
 */
export async function getAllLogs(): Promise<Log[]> {
    const response = await apiClient.get<Log[]>(endpoints.logs.all);
    return response.data;
}
