import { createContext, useContext } from 'react';
import { ToastMessageOptions } from 'primereact/toast';

export type ToastContext = (params: ToastMessageOptions) => void | null;

export const ToastContext = createContext<ToastContext>(null);

/**
 * Custom hook to access the ToastContext.
 *
 * This hook provides access to the ToastContext, allowing components
 * to interact with the toast notification system. It must be used
 * within a component that is a descendant of a `ToastProvider`.
 *
 * @returns {ToastContext} The context value for managing toast notifications.
 *
 * @throws {Error} If the hook is used outside of a `ToastProvider`.
 */
export function useToast(): ToastContext {
    return useContext(ToastContext);
}
