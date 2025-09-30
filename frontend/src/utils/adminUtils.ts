import { logAction, logLevel, logType } from '@/types/models/Log.ts';

export const getLogLevelSeverity = (
    level: logLevel,
): 'success' | 'info' | 'warning' | 'danger' | undefined => {
    switch (level) {
        case logLevel.DEBUG:
            return 'info';
        case logLevel.INFO:
            return 'success';
        case logLevel.WARNING:
            return 'warning';
        case logLevel.ERROR:
        case logLevel.CRITICAL:
            return 'danger';
        default:
            return undefined;
    }
};

export const getLogTypeSeverity = (type: logType): 'info' | 'warning' | 'danger' | undefined => {
    switch (type) {
        case logType.DEFAULT:
            return 'info';
        case logType.LIMITER:
            return 'warning';
        case logType.UNAUTHORIZED:
            return 'danger';
        default:
            return undefined;
    }
};

export const getLogActionSeverity = (
    action: logAction,
): 'success' | 'warning' | 'danger' | 'info' | undefined => {
    switch (action) {
        case logAction.CREATE:
            return 'success';
        case logAction.UPDATE:
            return 'info';
        case logAction.DELETE:
            return 'danger';
        case logAction.READ:
            return 'warning';
        default:
            return undefined;
    }
};
