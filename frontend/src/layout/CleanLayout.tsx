import { Outlet } from '@/router/Outlet';
import { JSX } from 'react';

/**
 * A layout component that serves as a placeholder for rendering child routes.
 *
 * @returns {JSX.Element} The rendered child route component.
 */
export function CleanLayout(): JSX.Element {
    return <Outlet />;
}

export default CleanLayout;
