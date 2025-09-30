import { JSX, ReactNode } from 'react';

export type DashboardHeaderProps = {
    title: string;
    end?: ReactNode;
};

/**
 * Represents the header component for the dashboard layout.
 *
 * @component
 *
 * @param {DashboardHeaderProps} props - The props for the DashboardHeader component.
 *
 * @returns {JSX.Element} The rendered DashboardHeader component.
 */
export function DashboardHeader({ title, end }: DashboardHeaderProps): JSX.Element {
    return (
        <div className="flex justify-content-between align-items-center my-6">
            <h1>{title}</h1>
            <div>{end}</div>
        </div>
    );
}
