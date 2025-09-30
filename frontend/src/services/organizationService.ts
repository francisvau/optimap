import { apiClient } from '@/services/client';
import {
    Organization,
    OrganizationStats,
    OrganizationUser,
    PendingUser,
} from '@/types/models/Organization';
import {
    OrganizationRequest,
    EditMemberRoleRequest,
    InviteOrganizationRequest,
    InviteOrganizationResponse,
    JoinOrganizationRequest,
    JoinOrganizationResponse,
    RoleRequest,
} from '@/types/schemas/Organization';
import { OrganizationRole } from '@/types/models/User.ts';
import { endpoints } from '@/services/endpoints';
import { ModelRequest } from '@/types/schemas/Model';
import { Model } from '@/types/models/Model';

/**
 * Fetches an organization by its ID.
 *
 * @param id - The unique identifier of the organization to retrieve.
 * @returns A promise that resolves to an AxiosResponse containing the organization data.
 */
export async function getOrganizationById(id: number): Promise<Organization> {
    const endpoint = endpoints.organization.get.replace('{orgId}', id.toString());
    const response = await apiClient.get<Organization>(endpoint);
    return response.data;
}

/**
 * Fetches the list of organizations associated with a specific user.
 *
 * @returns A promise that resolves to an AxiosResponse containing an array of `Organization` objects.
 */
export async function getUserOrganizations(): Promise<Organization[]> {
    const endpoint = endpoints.organization.all;
    const response = await apiClient.get<Organization[]>(endpoint);
    return response.data;
}

/**
 * Fetches the list of organizations associated with a specific user.
 *
 * @param orgId - The unique identifier of the user whose organizations are to be retrieved.
 * @returns A promise that resolves to an AxiosResponse containing an array of `Organization` objects.
 */
export async function getOrganizationUsers(orgId: number): Promise<OrganizationUser[]> {
    const endpoint = endpoints.organization.users.replace('{orgId}', orgId.toString());
    const response = await apiClient.get<OrganizationUser[]>(endpoint);
    return response.data;
}

/**
 * Adds a new organization.
 *
 * @param organization - The organization data to add.
 * @param form
 * @returns A promise that resolves to an AxiosResponse containing the added organization data.
 */
export async function createOrganization(form: OrganizationRequest): Promise<Organization> {
    const endpoint = endpoints.organization.create;
    const response = await apiClient.post<Organization>(endpoint, form);
    return response.data;
}

/**
 * Invite an organization.
 *
 * @param organizationId
 * @param form
 * @returns A promise that resolves to an AxiosResponse containing the updated organization data.
 */
export async function inviteOrganization(
    organizationId: number,
    form: InviteOrganizationRequest,
): Promise<InviteOrganizationResponse> {
    const endpoint = endpoints.organization.invite.replace('{orgId}', organizationId.toString());
    const response = await apiClient.post<InviteOrganizationResponse>(endpoint, {
        userEmail: form.email,
        userRole: form.userRole.name,
        roleId: form.userRole.id,
    });
    return response.data;
}

/**
 * Invite an organization.
 *
 * @param organizationId - The organization data to update.
 * @param userId - The user data to update.
 * @returns A promise that resolves to an AxiosResponse containing the updated organization data.
 */
export async function blacklistFromOrganization(
    organizationId: number,
    userId: number,
): Promise<void> {
    const endpoint = endpoints.organization.blacklist
        .replace('{orgId}', organizationId.toString())
        .replace('{userId}', userId.toString());
    await apiClient.delete<void>(endpoint);
}

/**
 * Fetches statistics for a specific organization.
 * @param organizationId
 * @returns A promise that resolves to an AxiosResponse containing the organization statistics.
 */
export async function organizationStats(organizationId: number): Promise<OrganizationStats> {
    const endpoint = endpoints.organization.stats.replace('{orgId}', organizationId.toString());
    const response = await apiClient.get<OrganizationStats>(endpoint);
    return response.data;
}

/**
 * Invite an organization.
 *
 * @param organizationId - The organization data to update.
 * @param userId - The user data to update.
 * @returns A promise that resolves to an AxiosResponse containing the updated organization data.
 */
export async function deleteFromOrganization(
    organizationId: number,
    userId: number,
): Promise<void> {
    const endpoint = endpoints.organization.deleteUser
        .replace('{orgId}', organizationId.toString())
        .replace('{userId}', userId.toString());
    await apiClient.delete<void>(endpoint);
}

/**
 * Deletes an organization.
 * @param id - The unique identifier of the organization to delete.
 * @returns A promise that resolves to an AxiosResponse containing the deleted organization data.
 */
export async function deleteOrganization(id: number): Promise<void> {
    await apiClient.delete<void>(endpoints.organization.delete.replace('{orgId}', id.toString()));
}

/**
 * Deletes an organization.
 * @param id - The unique identifier of the organization to delete.
 * @param form - The unique identifier of the organization to delete.
 * @returns A promise that resolves to an AxiosResponse containing the deleted organization data.
 */
export async function editOrganization(
    id: number,
    form: OrganizationRequest,
): Promise<Organization> {
    const endpoint = endpoints.organization.edit.replace('{orgId}', id.toString());
    const response = await apiClient.patch<Organization>(endpoint, form);
    return response.data;
}

/**
 * Gets all pending invitations from an organization
 * @param organizationId - The unique identifier of the organization to delete.
 * @returns A promise that resolves to an AxiosResponse containing a list
 */
export async function getPendingInvitations(organizationId: number): Promise<PendingUser[]> {
    const endpoint = endpoints.organization.pendingInvites.replace(
        '{orgId}',
        organizationId.toString(),
    );
    const response = await apiClient.get<PendingUser[]>(endpoint);
    return response.data;
}

/**
 * Gets all pending invitations from an organization
 * @param form - The unique identifier of the organization to delete.
 * @returns A promise that resolves to an AxiosResponse containing a list
 */
export async function joinOrganization(
    form: JoinOrganizationRequest,
): Promise<JoinOrganizationResponse> {
    const endpoint = endpoints.organization.join;
    const response = await apiClient.post<JoinOrganizationResponse>(endpoint, form);
    return response.data;
}

/**
 * Deletes an organization.
 * @returns A promise that resolves to an AxiosResponse containing tall the organizations.
 */
export async function getOrganizations(): Promise<Organization[]> {
    const endpoint = endpoints.organization.all;
    const response = await apiClient.get<Organization[]>(endpoint);
    return response.data;
}

/**
 * Edits a role inside an organization
 *
 * @param {number} organizationId - The ID of the organization where the role exists.
 * @param {number} roleId
 * @param {RoleRequest} form
 * @returns {Promise<OrganizationRole>} - A promise that resolves to the API response containing the updated role data.
 */
export async function editOrganizationRole(
    organizationId: number,
    roleId: number,
    form: RoleRequest,
): Promise<OrganizationRole> {
    const endpoint = endpoints.organization.role.edit
        .replace('{orgId}', organizationId.toString())
        .replace('{roleId}', roleId.toString());
    const response = await apiClient.patch<OrganizationRole>(endpoint, form);
    return response.data;
}

/**
 * Creates a new role inside an organization.
 *
 * @param {RoleRequest} role - The role object that contains the details of the new role to be created.
 * @param {number} organizationId - The ID of the organization where the role will be created.
 *
 * @returns {Promise<OrganizationRole>} - A promise that resolves to the API response containing the newly created role data.
 */
export async function createOrganizationRole(
    role: RoleRequest,
    organizationId: number,
): Promise<OrganizationRole> {
    const endpoint = endpoints.organization.role.create.replace(
        '{orgId}',
        organizationId.toString(),
    );
    const response = await apiClient.post<OrganizationRole>(endpoint, role);
    return response.data;
}

/**
 * Deletes a role from an organization.
 *
 * @param {number} roleId - The ID of the role to be deleted.
 * @param {number} organizationId - The ID of the organization from which the role will be deleted.
 *
 * @returns {Promise<void>} - A promise that resolves to the API response indicating the deletion success.
 */
export async function deleteOrganizationRole(
    roleId: number,
    organizationId: number,
): Promise<void> {
    const endpoint = endpoints.organization.role.delete
        .replace('{orgId}', organizationId.toString())
        .replace('{roleId}', roleId.toString());
    await apiClient.delete<void>(endpoint);
}

/**
 * Deletes a role from an organization.
 *
 * @param {number} organizationId - The ID of the organization from which the role will be deleted.
 *
 * @returns {Promise<Role[]>} - A promise that resolves to the API response indicating the deletion success.
 */
export async function getOrganizationRoles(organizationId: number): Promise<OrganizationRole[]> {
    const endpoint = endpoints.organization.role.all.replace('{orgId}', organizationId.toString());
    const response = await apiClient.get<OrganizationRole[]>(endpoint);
    return response.data;
}

/**
 * Deletes a role from an organization.
 *
 * @param {number} organizationId
 * @param {number} userId
 * @param {EditMemberRoleRequest} form - The ID of the organization from which the role will be deleted.
 * @returns {Promise<OrganizationUser>} - A promise that resolves to the API response indicating the deletion success.
 */
export async function updateOrganizationUserRole(
    organizationId: number,
    userId: number,
    form: EditMemberRoleRequest,
): Promise<OrganizationUser> {
    const endpoint = endpoints.organization.userRole
        .replace('{orgId}', organizationId.toString())
        .replace('{userId}', userId.toString());
    const response = await apiClient.patch<OrganizationUser>(endpoint, {
        roleId: form.role,
    });
    return response.data;
}

/**
 * Deletes a role from an organization.
 *
 * @param {number} organizationId
 * @param {number} userId
 * @returns {Promise<OrganizationUser>} - A promise that resolves to the API response indicating the deletion success.
 */
export async function getOrganizationUser(
    userId: number,
    organizationId: number,
): Promise<OrganizationUser> {
    const endpoint = endpoints.organization.getUser
        .replace('{orgId}', organizationId.toString())
        .replace('{userId}', userId.toString());
    const response = await apiClient.get<OrganizationUser>(endpoint);
    return response.data;
}

/**
 * Fetches all models associated with a specific organization.
 *
 * @param organizationId - The unique identifier of the organization.
 * @returns A promise that resolves to an array of `Model` objects.
 */
export async function getModelsForOrganization(organizationId: number): Promise<Model[]> {
    const endpoint = endpoints.organization.models.all.replace(
        '{orgId}',
        organizationId.toString(),
    );
    const response = await apiClient.get<Model[]>(endpoint);
    return response.data;
}

/**
 * Creates a new model for a specified organization.
 *
 * @param organizationId - The unique identifier of the organization.
 * @param form - The data required to create the model, adhering to the `CreateModelRequest` structure.
 * @returns A promise that resolves to the created `Model` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function createModelForOrganization(
    organizationId: number,
    form: ModelRequest,
): Promise<Model> {
    const endpoint = endpoints.organization.models.create.replace(
        '{orgId}',
        organizationId.toString(),
    );
    const response = await apiClient.post<Model>(endpoint, form);
    return response.data;
}

/**
 * Updates a model for a specific organization.
 *
 * @param organizationId - The unique identifier of the organization.
 * @param modelId - The unique identifier of the model to be updated.
 * @param form - The data to update the model with, adhering to the `UpdateModelRequest` structure.
 * @returns A promise that resolves to the updated `Model` object.
 *
 * @throws Will throw an error if the API request fails.
 */
export async function updateModelForOrganization(
    organizationId: number,
    modelId: string,
    form: ModelRequest,
): Promise<Model> {
    const endpoint = endpoints.organization.models.edit
        .replace('{orgId}', organizationId.toString())
        .replace('{modelId}', modelId.toString());
    const response = await apiClient.patch<Model>(endpoint, form);
    return response.data;
}

/**
 * Deletes a specific model associated with an organization.
 *
 * @param organizationId - The unique identifier of the organization.
 * @param modelId - The unique identifier of the model to be deleted.
 * @returns A promise that resolves when the model is successfully deleted.
 *
 * @throws An error if the API request fails.
 */
export async function deleteModelForOrganization(
    organizationId: number,
    modelId: string,
): Promise<void> {
    const endpoint = endpoints.organization.models.delete
        .replace('{orgId}', organizationId.toString())
        .replace('{modelId}', modelId.toString());
    await apiClient.delete<void>(endpoint);
}
