import { JSX } from 'react';
import { AppBar } from '@/layout/navigation/AppBar';
import { AnimatedBackground } from '@/components/shared/AnimatedBackground';
import { Outlet } from '@/router/Outlet.tsx';
import { Footer } from '@/layout/navigation/Footer';

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
export function BaseLayout(): JSX.Element {
    return (
        <div className="relative min-h-screen flex flex-column">
            <AnimatedBackground />
            <div className="relative px-3 mx-auto w-12 md:w-10 xl:w-8 flex-1">
                <div className="pt-5">
                    <AppBar />
                </div>
                <div className="py-5">
                    <Outlet />
                </div>
            </div>
            <div className="mt-auto">
                <Footer />
            </div>
        </div>
    );
}

export default BaseLayout;
