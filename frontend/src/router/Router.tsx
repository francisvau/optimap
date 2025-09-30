import React, { lazy } from 'react';
import { createBrowserRouter, createRoutesFromElements, Route } from 'react-router';
import { AppProvider } from '@/hooks/context/AppProvider';
import { authLoader } from '@/router/loaders/authLoader';
import { blueprintLoader, jobLoader, organizationLoader } from '@/router/loaders/dataLoader';
import { BlueprintLayout } from '@/layout/dashboard/BlueprintLayout';
import { OrganizationProvider } from '@/hooks/context/OrganizationProvider/OrganizationProvider';
import CleanLayout from '@/layout/CleanLayout';
import BaseLayout from '@/layout/BaseLayout';
import DashboardLayout from '@/layout/dashboard/DashboardLayout';
import { RootBoundary } from '@/router/RootBoundary';
import { NotFound } from '@/pages/errors/NotFound';
import AdminLayout from '@/layout/AdminLayout';

/**
 * A utility function to create a lazily-loaded route component.
 * This function wraps a dynamically imported component with React's `Suspense`
 * to provide a fallback UI while the component is being loaded.
 *
 * @param importFn - A function that returns a promise resolving to a module
 *                   with a default export of a React component.
 * @returns A JSX element that renders the lazily-loaded component wrapped in a `Suspense` fallback.
 *
 */
function lazyRoute(importFn: () => Promise<{ default: React.ComponentType }>) {
    const Component = lazy(importFn);
    return <Component />;
}

export const router = createBrowserRouter(
    createRoutesFromElements(
        <Route element={<AppProvider />} errorElement={<RootBoundary />}>
            {/* Public routes */}
            <Route element={<CleanLayout />}>
                <Route index element={lazyRoute(() => import('@/pages/home/HomePage'))} />
            </Route>

            {/* Auth routes */}
            <Route path="auth" element={<BaseLayout />}>
                <Route path="login" element={lazyRoute(() => import('@/pages/auth/LoginPage'))} />
                <Route
                    path="register"
                    element={lazyRoute(() => import('@/pages/auth/RegisterPage'))}
                />
                <Route
                    path="verify/:token?"
                    element={lazyRoute(() => import('@/pages/auth/VerifyPage'))}
                />
                <Route
                    path="password/forgot"
                    element={lazyRoute(() => import('@/pages/auth/ForgotPasswordPage'))}
                />
                <Route
                    path="password/reset/:token"
                    element={lazyRoute(() => import('@/pages/auth/ResetPasswordPage'))}
                />
                <Route
                    path="me"
                    element={lazyRoute(() => import('@/pages/auth/UserSettingsPage'))}
                />
            </Route>

            {/* Admin routes */}
            <Route path="admin" element={<AdminLayout />}>
                <Route element={<OrganizationProvider />}>
                    <Route index element={lazyRoute(() => import('@/pages/admin/AdminPage'))} />
                    <Route
                        path="logs/users/:id"
                        element={lazyRoute(() => import('@/pages/admin/UserLogPage'))}
                    />
                    <Route
                        path="logs/organizations/:id"
                        element={lazyRoute(() => import('@/pages/admin/OrganizationLogPage'))}
                    />
                    <Route
                        path="users"
                        element={lazyRoute(() => import('@/pages/admin/AdminUsersPage'))}
                    />
                    <Route
                        path="organizations"
                        element={lazyRoute(() => import('@/pages/admin/AdminOrganizationPage'))}
                    />
                </Route>
            </Route>

            {/* Protected dashboard routes */}
            <Route path="dashboard" loader={authLoader} shouldRevalidate={() => true}>
                <Route element={<OrganizationProvider />}>
                    <Route element={<DashboardLayout />}>
                        <Route
                            index
                            element={lazyRoute(() => import('@/pages/dashboard/DashboardPage'))}
                        />
                        <Route
                            path="profile"
                            element={lazyRoute(() => import('@/pages/auth/ProfilePage'))}
                        />

                        {/* Organizations */}
                        <Route path="organizations">
                            <Route
                                path=":organizationId/:tabView?"
                                loader={organizationLoader}
                                id="organization"
                            >
                                <Route
                                    index
                                    loader={organizationLoader}
                                    element={lazyRoute(
                                        () =>
                                            import(
                                                '@/pages/dashboard/organizations/OrganizationPage'
                                            ),
                                    )}
                                />
                                <Route
                                    path="users"
                                    element={lazyRoute(
                                        () =>
                                            import(
                                                '@/pages/dashboard/organizations/OrganizationUsersPage'
                                            ),
                                    )}
                                />
                                <Route
                                    path="roles"
                                    element={lazyRoute(
                                        () =>
                                            import(
                                                '@/pages/dashboard/organizations/OrganizationRolesPage'
                                            ),
                                    )}
                                />
                                <Route
                                    path="invites"
                                    element={lazyRoute(
                                        () =>
                                            import(
                                                '@/pages/dashboard/organizations/OrganizationInvitesPage'
                                            ),
                                    )}
                                />
                            </Route>
                            <Route
                                path="join/:token"
                                element={lazyRoute(
                                    () =>
                                        import(
                                            '@/pages/dashboard/organizations/JoinOrganizationPage'
                                        ),
                                )}
                            />
                        </Route>

                        {/* Blueprints list */}
                        <Route path="blueprints">
                            <Route
                                index
                                element={lazyRoute(
                                    () => import('@/pages/dashboard/blueprints/ListBlueprintPage'),
                                )}
                            />
                        </Route>

                        {/* Jobs */}
                        <Route path="jobs">
                            <Route
                                index
                                element={lazyRoute(
                                    () => import('@/pages/dashboard/jobs/ListJobPage'),
                                )}
                            />
                            <Route
                                loader={jobLoader}
                                path=":jobId"
                                element={lazyRoute(() => import('@/pages/dashboard/jobs/JobPage'))}
                            />
                        </Route>
                    </Route>

                    {/* Blueprint detail */}
                    <Route
                        path="blueprints/:blueprint"
                        loader={blueprintLoader}
                        element={<BlueprintLayout />}
                    >
                        <Route
                            path=":definition?/:mapping?"
                            element={lazyRoute(
                                () => import('@/pages/dashboard/blueprints/SourceMappingPage'),
                            )}
                        />
                        <Route
                            path="edit"
                            element={lazyRoute(
                                () => import('@/pages/dashboard/blueprints/EditBlueprintPage'),
                            )}
                        />
                    </Route>
                </Route>
            </Route>
            <Route path="*" element={<NotFound />} />
        </Route>,
    ),
);
