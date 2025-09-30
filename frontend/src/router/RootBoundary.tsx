import React from 'react';
import { useNavigate } from 'react-router';
import { isRouteErrorResponse } from 'react-router';
import { useRouteError } from 'react-router';
import { JSX } from 'react';

import { NotFound } from '@/pages/errors/NotFound';
import { UnexpectedError } from '@/pages/errors/UnexpectedError';

/**
 * RootBoundary component that handles route errors and redirects.
 *
 * @returns {JSX.Element} The rendered RootBoundary component.
 *
 * This component uses the `useRouteError` hook to retrieve route errors.
 * If the error is a RouteErrorResponse, it checks the status code and redirects accordingly.
 * If the error is not a RouteErrorResponse, it renders an UnexpectedError component.
 *
 * @component
 *
 * @name RootBoundary
 */
export function RootBoundary(): JSX.Element {
    const error = useRouteError();
    const navigate = useNavigate();

    if (isRouteErrorResponse(error)) {
        switch (error.status) {
            case 401:
                navigate('/login', { replace: true });
                return null;
            case 404:
                return <NotFound />;
            default:
                return <UnexpectedError />;
        }
    }

    return <UnexpectedError />;
}
