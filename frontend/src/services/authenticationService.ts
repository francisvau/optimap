import { apiClient } from '@/services/client';
import { endpoints } from '@/services/endpoints';
import {
    ChangeSettingRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
} from '@/types/schemas/Auth';
import { User } from '@/types/models/User';
import { AxiosResponse } from 'axios';

/**
 * Authenticates a user by sending their login form data to the server.
 *
 * @param form - The login form data containing user credentials.
 * @returns A promise that resolves to the Axios response from the server.
 */
export async function login(form: LoginRequest): Promise<User> {
    const { data } = await apiClient.post<User>(endpoints.auth.login, form);
    return data;
}

/**
 * Registers a new user by sending the provided registration form data to the server.
 *
 * @param form - The registration form data containing user details.
 * @returns A promise that resolves to the AxiosResponse from the server.
 */
export async function register(form: RegisterRequest): Promise<unknown> {
    if (form.token) {
        return await apiClient.post(endpoints.auth.register, {
            password: form.password,
            firstName: form.firstName,
            lastName: form.lastName,
            token: form.token,
            email: form.email,
        });
    } else {
        return await apiClient.post(endpoints.auth.register, {
            email: form.email,
            password: form.password,
            firstName: form.firstName,
            lastName: form.lastName,
        });
    }
}

/**
 * Logs out the currently authenticated user by clearing the user state
 * and sending a logout request to the server.
 *
 * @returns {Promise<AxiosResponse>} A promise that resolves with the server's response to the logout request.
 */
export async function logout(): Promise<unknown> {
    return await apiClient.post(endpoints.auth.logout);
}

/**
 * Fetches the authenticated user's information from the server.
 *
 * @returns {Promise<AxiosResponse>} A promise that resolves to the Axios response containing the user's data.
 */
export async function me(): Promise<User> {
    const { data } = await apiClient.get<User>(endpoints.auth.me);
    return data;
}

/**
 * Sends a request to initiate the forgot password process for a user.
 *
 * @param form - An object containing the necessary data for the forgot password request.
 * @returns A promise that resolves to the Axios response of the API call.
 */
export async function forgotPassword(form: ForgotPasswordRequest): Promise<AxiosResponse> {
    return await apiClient.post(endpoints.auth.forgotPassword, form);
}

/**
 * Sends a request to reset the user's password.
 *
 * @param form - An object containing the reset password form data.
 * @returns A promise that resolves to the Axios response of the reset password request.
 */
export async function resetPassword(form: ResetPasswordRequest): Promise<AxiosResponse> {
    return await apiClient.post(endpoints.auth.resetPassword, form);
}

/**
 * Sends a verification request to the authentication service.
 *
 * @param email - The email address to be verified.
 * @returns A promise that resolves to the Axios response of the verification request.
 */
export async function verifyRequest(email: string): Promise<AxiosResponse> {
    return await apiClient.post(endpoints.auth.verifyRequest, { email });
}

/**
 * Verifies the user's account using a verification token.
 *
 * @param token - The verification token to be used for account verification.
 * @returns A promise that resolves to the Axios response of the verification request.
 */
export async function verify(token: string): Promise<AxiosResponse> {
    return await apiClient.post(endpoints.auth.verify.replace('{token}', token));
}

/**
 * Updates the authenticated user's information.
 *
 * @param form - The user data to be updated.
 * @returns A promise that resolves to the Axios response containing the updated user data.
 */
export async function updateUser(form: ChangeSettingRequest): Promise<User> {
    const { data } = await apiClient.patch<User>(endpoints.auth.me, form);
    return data;
}
