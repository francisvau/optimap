import { apiClient } from '@/services/client';
import { User } from '@/types/models/User';
import { AxiosResponse } from 'axios';
import { endpoints } from '@/services/endpoints';

/**
 * Fetches a user by their unique identifier.
 *
 * @param id - The unique identifier of the user to retrieve.
 * @returns A promise that resolves to an AxiosResponse containing the user data.
 */
export async function getUserById(id: number): Promise<AxiosResponse<User>> {
    return await apiClient.get<User>(`/api/users/${id}`);
}

/**
 * Deletes a user by their unique identifier.
 *
 * @param id - The unique identifier of the user to be deleted.
 * @returns A promise that resolves to an AxiosResponse with no content (void) upon successful deletion.
 */
export async function deleteUserById(id: number): Promise<AxiosResponse<void>> {
    return await apiClient.delete<void>(`/users/${id}`);
}

/**
 * Deletes a user by their unique identifier.
 *
 * @returns A promise that resolves to an AxiosResponse with no content (void) upon successful deletion.
 */
export async function getUsers(): Promise<AxiosResponse<User[]>> {
    return await apiClient.get<User[]>(endpoints.user.all);
}

/**
 * Deletes a user by their unique identifier.
 *
 * @param id - The unique identifier of the user to be deleted.
 * @returns A promise that resolves to an AxiosResponse with no content (void) upon successful deletion.
 */
export async function blockUser(id: number): Promise<AxiosResponse<void>> {
    return await apiClient.post<void>(endpoints.auth.block.replace('{userId}', id.toString()));
}

/**
 * Deletes a user by their unique identifier.
 *
 * @param id - The unique identifier of the user to be deleted.
 * @returns A promise that resolves to an AxiosResponse with no content (void) upon successful deletion.
 */
export async function unblockUser(id: number): Promise<AxiosResponse<void>> {
    return await apiClient.post<void>(endpoints.auth.unblock.replace('{userId}', id.toString()));
}
