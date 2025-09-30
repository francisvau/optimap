import { me, login as apiLogin, logout as apiLogout } from '@/services/authenticationService';
import { User } from '@/types/models/User';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { JSX } from 'react';
import { ApiError } from '@/services/client';
import { AuthContext } from '@/hooks/context/AuthProvider/AuthContext';

/**
 * Provides authentication context to the application.
 *
 * This component wraps its children with an `AuthContext.Provider` that supplies
 * authentication-related state and functions, such as the current user, login, and logout.
 *
 * @param {Object} props - The props for the AuthProvider component.
 * @param {React.ReactNode} props.children - The child components to be wrapped by the provider.
 *
 * @returns {JSX.Element} The `AuthContext.Provider` wrapping the children.
 *
 */
export function AuthProvider({ children }: { children: React.ReactNode }): JSX.Element {
    const queryClient = useQueryClient();

    const user = useQuery<User | null, ApiError>({
        queryKey: ['user'],
        queryFn: me,
    });

    const loginMutation = useMutation({
        mutationFn: apiLogin,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user'] }),
    });

    const logoutMutation = useMutation({
        mutationFn: apiLogout,
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['user'] });
            await queryClient.setQueryData(['user'], null);
            void localStorage.clear();
        },
    });

    return (
        <AuthContext.Provider
            value={{
                user: user.data,
                isLoggedIn: user.isSuccess,
                isLoading: user.isFetching,
                error: user.error,
                reload: user.refetch,
                login: loginMutation.mutateAsync,
                logout: logoutMutation.mutateAsync,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}
