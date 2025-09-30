import { OrganizationRole } from '@/types/models/User.ts';

export interface OrganizationRequest {
    name?: string;
    address?: string;
    branch?: string;
    systemPrompt?: string;
}

export interface InviteOrganizationRequest {
    email: string;
    userRole: OrganizationRole;
}

export interface JoinOrganizationRequest {
    token: string;
}

export interface RoleRequest {
    id?: number;
    name: string;
    permissions: string[];
}

export interface InviteOrganizationResponse {
    message: string;
    email: string;
    organizationId: number;
}

export interface JoinOrganizationResponse {
    organizationId: number;
}

export interface EditMemberRoleRequest {
    role: number;
}
