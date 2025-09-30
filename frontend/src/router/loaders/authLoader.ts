import { me } from '@/services/authenticationService';
import { queryClient } from '@/services/client';
import { redirect } from 'react-router';

/**
 * Loader function to handle authentication and redirection for the dashboard route.
 *
 * This function checks the authentication status of the user by fetching the user data
 * using a query client. Based on the user's authentication and verification status, it
 * redirects to the appropriate route:
 *
 * - If the user is not authenticated, redirects to the login page (`/auth/login`).
 * - If the user is authenticated but not verified, redirects to the verification page (`/auth/verify`).
 *
 * @returns A `Promise<Response>` that resolves to a redirection response if the user is
 *          not authenticated or not verified.
 */
export async function authLoader(): Promise<Response> {
    try {
        const user = await queryClient.fetchQuery({
            queryKey: ['user'],
            queryFn: me,
        });

        if (user && !user.isVerified) {
            return redirect('/auth/verify?warn=Please verify your account.');
        }

        if (user && user.blockedAt !== null) {
            return redirect('/auth/login?error=Your account is blocked.');
        }
    } catch {
        return redirect('/auth/login?warn=Please login to continue.');
    }
}
