import { OrganizationRole, User } from '@/types/models/User.ts';

export interface Organization {
    id: number;
    name: string;
    address: string | null;
    description: string | null;
    systemPrompt: string | null;
    branch: string | null;
    modelIds: string[];
}

export interface OrganizationStats {
    userCount: number;
    roleCount: number;
    pendingInviteCount: number;
    adminUserCount: number;
    bytes: number;
    jobCount: number;
    minExecutionTime: number;
    maxExecutionTime: number;
    avgExecutionTime: number;
}

export interface OrganizationUser {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    isVerified: boolean;
    userId: number;
    user?: User;
    organizationId: number;
    organization?: Organization;
    role?: OrganizationRole;
    createdAt: Date;
}

export interface PendingUser {
    email: string;
    expiresAt: Date;
    joinedAt: Date | null;
}
