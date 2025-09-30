import { JSX, useCallback, useEffect, useRef } from 'react';
import { Toast, ToastMessageOptions } from 'primereact/toast';
import { ToastContext } from './ToastContext';
import { useSearchParams } from 'react-router';
import { capitalize } from '@/utils/stringUtils';

/**
 * Provides a context for displaying toast notifications across the application.
 *
 * This component uses PrimeReact's `Toast` to show notifications and makes the `showToast`
 * function available via context, allowing any component within the provider to trigger a toast.
 *
 * @param {Object} props - The component props.
 * @param {React.ReactNode} props.children - The child components wrapped by the provider.
 * @returns {JSX.Element} The `ToastProvider` component that wraps the application.
 */
export function ToastProvider({ children }: { children: React.ReactNode }): JSX.Element {
    const toastRef = useRef(null);
    const [params, setParams] = useSearchParams();

    const showToast = useCallback((params: ToastMessageOptions) => {
        const summary = capitalize(params.summary ?? params.severity);
        toastRef.current?.show({ summary, ...params });
    }, []);

    useEffect(() => {
        const warn = params.get('warn');
        const error = params.get('error');
        const success = params.get('success');
        const info = params.get('info');
        if (warn) {
            showToast({
                severity: 'warn',
                summary: 'Warning',
                detail: warn,
            });
            setParams({});
        }
        if (error) {
            showToast({
                severity: 'error',
                summary: 'Error',
                detail: error,
            });
            setParams({});
        }
        if (success) {
            showToast({
                severity: 'success',
                summary: 'Success',
                detail: success,
            });
            setParams({});
        }
        if (info) {
            showToast({
                severity: 'info',
                summary: 'Info',
                detail: info,
            });
            setParams({});
        }
    }, [params, setParams, showToast]);

    return (
        <ToastContext.Provider value={showToast}>
            <Toast ref={toastRef} />
            {children}
        </ToastContext.Provider>
    );
}
