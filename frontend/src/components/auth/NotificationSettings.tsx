import React, { useEffect, useState } from 'react';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { Divider } from 'primereact/divider';
import {
    UsageReportFrequency,
    Notification,
    patchNotificationRequest,
} from '@/types/models/Notification.ts';
import {
    getNotificationPreferences,
    patchNotificationPreferences,
} from '@/services/notificationService.ts';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext.ts';
import { ApiError } from '@/services/client.ts';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext.ts';

/**
 * SettingsPage allows a user to view and edit their first and last name.
 *
 * This component fetches the user's current first and last name from the authentication context
 * and allows them to edit these fields. When the user clicks the "Save" button,
 * it updates the user's information in the backend and shows a success or error message.
 * @returns {React.JSX.Element} The SettingsPage component.
 */
export function NotificationSettings(): React.JSX.Element {
    const [isEditing, setIsEditing] = useState(false);
    const { user } = useAuth();
    const toast = useToast();

    const { data, isSuccess } = useQuery({
        queryKey: ['preferences', user?.id],
        queryFn: async () => await getNotificationPreferences(),
    });

    const [metricsReportFrequency, setMetricsReportFrequency] = useState<UsageReportFrequency>(
        UsageReportFrequency.NEVER,
    );
    const [emailNotifications, setEmailNotifications] = useState(false);

    const frequencyOptions = [
        { label: 'Never', value: UsageReportFrequency.NEVER },
        { label: 'Daily', value: UsageReportFrequency.DAILY },
        { label: 'Weekly', value: UsageReportFrequency.WEEKLY },
        { label: 'Monthly', value: UsageReportFrequency.MONTHLY },
    ];

    const editMutation = useMutation<Notification, ApiError, patchNotificationRequest>({
        mutationFn: patchNotificationPreferences,
        onSuccess: async () => {
            void toast({ severity: 'success', detail: 'Notification settings have been updated' });
        },
        onError: (error) => {
            void toast({
                severity: 'error',
                summary: 'Failed to update notification settings',
                detail: error.message,
            });
        },
    });

    useEffect(() => {
        if (data) {
            setEmailNotifications(data.emailNotifications);
            setMetricsReportFrequency(data.usageReport);
        }
    }, [data, isSuccess]);

    const handleSave = () => {
        editMutation.mutateAsync({
            usageReport: metricsReportFrequency,
            emailNotifications: emailNotifications,
        });
        setIsEditing(false);
    };

    return (
        <Card
            title={
                <div className="flex items-center gap-2 align-items-center">
                    <i className="pi pi-envelope" />
                    <span>Notification Settings</span>
                </div>
            }
            className="mx-auto mt-5"
            style={{ maxWidth: '650px' }}
        >
            <div className="grid formgrid">
                <div className="col-12">
                    <h3 className="text-xl font-medium mt-0 mb-4">Usage Metrics Reports</h3>

                    <div className="field col-12 mb-4">
                        <label htmlFor="metricsFrequency" className="font-medium mb-2 block">
                            Receive reports on dynamic pipeline usage:
                        </label>
                        <Dropdown
                            id="metricsFrequency"
                            value={metricsReportFrequency}
                            options={frequencyOptions}
                            onChange={(e) =>
                                setMetricsReportFrequency(e.value as UsageReportFrequency)
                            }
                            className="w-full md:w-64"
                            disabled={!isEditing}
                        />

                        <small className="text-gray-500 block mt-1">
                            Reports include: data processed, average/min/max mapping times
                        </small>
                    </div>
                </div>

                <Divider className="col-12 my-3" />

                <div className="col-12">
                    <h3 className="text-xl font-medium mt-0 mb-4">Delivery Methods</h3>

                    <div className="field-checkbox mb-2">
                        <Checkbox
                            inputId="emailNotifications"
                            checked={emailNotifications}
                            onChange={(e) => setEmailNotifications(e.checked)}
                            disabled={!isEditing}
                        />
                        <label htmlFor="emailNotifications" className="ml-2">
                            Email notifications
                        </label>
                    </div>
                </div>
            </div>

            <div className="field col-12 flex justify-content-end mt-5">
                <Button
                    label={isEditing ? 'Save' : 'Edit'}
                    icon={isEditing ? 'pi pi-save' : 'pi pi-pencil'}
                    onClick={isEditing ? handleSave : () => setIsEditing(true)}
                    className="p-button-raised"
                />
            </div>
        </Card>
    );
}
