import { QueryClient } from '@tanstack/react-query';
import axios, { AxiosError, AxiosResponse } from 'axios';

export type ApiError = AxiosError<{
    detail: string;
    status: ErrorStatus | null;
}>;

export enum ErrorStatus {
    USER_UNVERIFIED = 'USER_UNVERIFIED',
}

export enum HttpStatus {
    OK = 200,
    CREATED = 201,
    ACCEPTED = 202,
    NO_CONTENT = 204,
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    CONFLICT = 409,
    UNPROCESSABLE_ENTITY = 422,
    LOCKED = 423,
    INTERNAL_SERVER_ERROR = 500,
}

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: false,
            refetchOnReconnect: true,
            staleTime: 1000,
        },
    },
});

export const apiClient = axios.create({
    withCredentials: true,
});

apiClient.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError) => {
        const data = error.response?.data;

        if (data && typeof data === 'object' && 'detail' in data) {
            const { detail } = data as { detail: unknown };

            if (typeof detail === 'string') {
                error.message = detail;
            } else if (Array.isArray(detail)) {
                error.message = detail
                    .map((err) => {
                        const loc = Array.isArray(err.loc) ? err.loc.join('.') : err.loc;
                        return `${loc}: ${err.msg}`;
                    })
                    .join(', ');
            } else if (typeof detail === 'object' && detail !== null) {
                error.message = Object.entries(detail)
                    .map(([field, val]) => {
                        const msg = Array.isArray(val) ? val.join(', ') : val.toString();
                        return `${field}: ${msg}`;
                    })
                    .join(', ');
            }
        }

        throw error;
    },
);
