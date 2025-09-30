export interface User {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    isVerified: boolean;
    isAdmin: boolean;
    isBlocked: boolean;
    blockedAt: Date | null;
}

export type OrganizationRole = {
    id: number;
    name: string;
    permissions: Permissions[];
};

export enum Permissions {
    VIEW_BLUEPRINT = 'view_blueprint',
    MANAGE_BLUEPRINT = 'manage_blueprint',
    MANAGE_USERS = 'manage_users',
    MANAGE_ROLES = 'manage_roles',
    CREATE_STATIC_JOBS = 'create_static_job',
    VIEW_STATIC_JOBS = 'view_static_job',
    MANAGE_ORGANIZATION = 'manage_organization',
}

export interface UserData {
    isLoggedIn: boolean;
    userData: User;
}
