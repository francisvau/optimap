export interface Notification {
    id: number;
    userId: number;
    usageReport: UsageReportFrequency;
    emailNotifications: boolean;
}

export interface patchNotificationRequest {
    usageReport: UsageReportFrequency;
    emailNotifications: boolean;
}

export enum UsageReportFrequency {
    DAILY = 'DAILY',
    WEEKLY = 'WEEKLY',
    MONTHLY = 'MONTHLY',
    NEVER = 'NEVER',
}
