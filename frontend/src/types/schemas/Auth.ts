export interface RegisterRequest {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    token?: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface ForgotPasswordRequest {
    email: string;
}

export interface ResetPasswordRequest {
    token: string;
    newPassword: string;
    confirmPassword: string;
}

export interface ChangeSettingRequest {
    firstName: string;
    lastName: string;
}
