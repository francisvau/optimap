import { Outlet } from '@/router/Outlet';
import { JSX } from 'react';
import { AppBar } from './navigation/AppBar';

/**
 * The `AdminLayout` component serves as the main layout for the admin dashboard.
 * It includes the application bar and a content area for nested routes.
 *
 *
 * @returns {JSX.Element} The rendered dashboard layout component.
 *
 * @remarks
 *
 * @component
 */
export function AdminLayout(): JSX.Element {
    return (
        <div className="relative flex">
            <div className="w-full min-h-screen" style={{ padding: '0 2rem 5rem' }}>
                <div className="mx-auto h-full w-12 lg:w-10">
                    <div style={{ margin: '2rem 0rem' }}>
                        <AppBar />
                    </div>
                    <Outlet />
                </div>
            </div>
        </div>
    );
}

export default AdminLayout;
