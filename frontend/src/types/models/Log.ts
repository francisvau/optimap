import { User } from '@/types/models/User.ts';
import { Organization } from '@/types/models/Organization.ts';

export interface Log {
    level: logLevel;
    action?: logAction;
    type?: logType;
    context?: { string: unknown };
    message: string;
    createdAt: Date;
    user?: User;
    organization?: Organization;
}

export enum logLevel {
    DEBUG = 'DEBUG',
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR',
    CRITICAL = 'CRITICAL',
}

export enum logType {
    DEFAULT = 'DEFAULT',
    LIMITER = 'LIMITER',
    UNAUTHORIZED = 'UNAUTHORIZED',
}

export enum logAction {
    CREATE = 'CREATE',
    UPDATE = 'UPDATE',
    DELETE = 'DELETE',
    READ = 'READ',
}
