import { endpoints } from '@/services/endpoints.ts';
import { apiClient } from '@/services/client.ts';
import { Notification, patchNotificationRequest } from '@/types/models/Notification.ts';

/**
 * Fetches the logs for a specific user.
 *  - The ID of the user whose logs to fetch.
 * @returns {Promise<Notification[]>} - A promise that resolves to an array of logs for the specified user.
 */
export async function getNotificationPreferences(): Promise<Notification> {
    const response = await apiClient.get<Notification>(endpoints.notifications.preferences);
    return response.data;
}

/**
 * Fetches the logs for a specific user.
 *  - The ID of the user whose logs to fetch.
 * @param request
 * @returns {Promise<Notification[]>} - A promise that resolves to an array of logs for the specified user.
 */
export async function patchNotificationPreferences(
    request: patchNotificationRequest,
): Promise<Notification> {
    const response = await apiClient.put<Notification>(
        endpoints.notifications.preferences,
        request,
    );
    return response.data;
}
