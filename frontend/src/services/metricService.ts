import { endpoints } from '@/services/endpoints.ts';
import { apiClient } from '@/services/client.ts';
import { Metrics } from '@/types/models/Metrics.ts';

/**
 * Fetches the system metrics from the API.
 * @returns {Promise<Metrics>} - A promise that resolves to the system metrics.
 */
export async function getSystemMetrics(): Promise<Metrics> {
    const response = await apiClient.get<Metrics>(endpoints.metrics.system);
    return response.data;
}
