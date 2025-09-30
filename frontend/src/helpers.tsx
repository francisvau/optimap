import { FC } from 'react';
import { JSX } from 'react/jsx-runtime';

/**
 * Composes multiple React functional components (providers) into a single component.
 * This allows you to nest multiple providers together in a clean and reusable way.
 *
 * @param providers - An array of React functional components to be composed.
 * Each component is expected to accept a `children` prop and render it within its context.
 *
 * @returns A single React functional component that nests all the provided components.
 * The resulting component will render the `children` prop within the nested providers.
 *
 * @example
 * ```tsx
 * const AppProviders = compose([AuthProvider, ToastProvider, ThemeProvider]);
 * ```
 */
export function compose(providers: Array<FC<{ children: JSX.Element | JSX.Element[] }>>) {
    return providers.reduce((Prev, Curr) => {
        const Composed: FC<{ children: JSX.Element | JSX.Element[] }> = ({ children }) => (
            <Prev>
                <Curr>{children}</Curr>
            </Prev>
        );
        return Composed;
    });
}
