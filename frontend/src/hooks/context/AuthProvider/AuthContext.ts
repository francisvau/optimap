import { ApiError } from '@/services/client';
import { LoginRequest } from '@/types/schemas/Auth';
import { User } from '@/types/models/User';
import { createContext, useContext } from 'react';

export type AuthContext = {
    user?: User | null;
    isLoggedIn: boolean;
    isLoading: boolean;
    error: ApiError | null;
    reload: () => Promise<unknown>;
    logout: () => Promise<unknown>;
    login: (profile: LoginRequest) => Promise<User>;
};

export const AuthContext = createContext<AuthContext>(null);

export const useAuth = () => useContext(AuthContext);
