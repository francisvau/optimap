import { JSX } from 'react';
import { AnimatedBackground } from '@/components/shared/AnimatedBackground';
import { Outlet } from 'react-router';
import { AppBar } from '@/layout/navigation/AppBar';

/**
 * BaseLayout component that manages user authentication and navigation.
 *
 * @returns {JSX.Element} The layout component containing the AppBar and Outlet.
 *
 * This component uses the `useLoaderData` hook to retrieve user data.
 *
 * If the user is logged in, the AppBar component is rendered.
 *
 * The Outlet component is rendered to display the child routes.
 *
 * @component
 *
 * @name BaseLayout
 *
 * The BaseLayout component contains the AppBar and Outlet components.
 */
export function WideLayout(): JSX.Element {
    return (
        <div className="relative">
            <div className="relative px-3 mx-auto w-12 ">
                <AnimatedBackground />
                <div className="my-5">
                    <AppBar />
                </div>
                <Outlet />
            </div>
        </div>
    );
}

export default WideLayout;
