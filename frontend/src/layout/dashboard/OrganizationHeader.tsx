import { Organization } from '@/types/models/Organization';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBuildingUser } from '@fortawesome/free-solid-svg-icons';
import { JSX } from 'react';
import { Button } from 'primereact/button';
import { PrimeIcons } from 'primereact/api';

import './OrganizationHeader.scss';

export type OrganizationHeaderProps = {
    organization: Organization;
    onDeselectOrganization: () => void;
};

/**
 * A functional component that renders the header for an organization.
 *
 * @param {OrganizationHeaderProps} props - The properties for the OrganizationHeader component.
 * @param {object} props.organization - The organization data to be displayed in the header.
 * @returns {JSX.Element} The rendered JSX element for the organization header.
 */
export function OrganizationHeader({
    organization,
    onDeselectOrganization,
}: OrganizationHeaderProps): JSX.Element {
    return (
        <div id="dashboard-organization-header">
            <div className="flex align-items-center gap-2">
                <FontAwesomeIcon id="icon" icon={faBuildingUser} />
                <span className="text-100">
                    Viewing as a member of <b></b>
                    {organization.name}
                </span>
            </div>
            <Button
                icon={PrimeIcons.USER}
                label="Open personal view"
                onClick={onDeselectOrganization}
                text
            />
        </div>
    );
}
