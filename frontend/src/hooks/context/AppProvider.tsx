import { Outlet } from 'react-router';
import { JSX } from 'react';
import { compose } from '@/helpers';
import { APIOptions, PrimeReactProvider } from 'primereact/api';
import { QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/hooks/context/AuthProvider/AuthProvider.tsx';
import { ToastProvider } from '@/hooks/context/ToastProvider/ToastProvider.tsx';
import { queryClient } from '@/services/client';

const primeReactConfig: Partial<APIOptions> = {
    ripple: true,
};

/**
 * BaseLayout component that manages user authentication and navigation.
 *
 * This component uses the `useLoaderData` hook to retrieve user data and the `useNavigate` and `useLocation` hooks
 * from React Router to handle navigation and location state.
 *
 * If the user is not logged in and tries to access a route other than '/login', they will be redirected to the login page
 * with a `redirect` query parameter indicating the original path they attempted to access.
 *
 * @returns {JSX.Element} The layout component containing the AppBar and Outlet wrapped in a UserProvider.
 */
export function AppProvider(): JSX.Element {
    const AppProvider = compose([AuthProvider, ToastProvider]);

    return (
        <PrimeReactProvider value={primeReactConfig}>
            <QueryClientProvider client={queryClient}>
                <AppProvider>
                    <Outlet />
                </AppProvider>
            </QueryClientProvider>
        </PrimeReactProvider>
    );
}
