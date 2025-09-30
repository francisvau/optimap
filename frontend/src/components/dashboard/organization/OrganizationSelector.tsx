import { Organization } from '@/types/models/Organization';
import { faBuildingUser } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { JSX } from 'react';

import './OrganizationSelector.scss';

export type OrganizationSelectorProps = {
    organization: Organization | null;
    organizations: Organization[];
    onChangeOrganization: (organization: Organization | null) => void;
    onAddOrganizationClick: () => void;
};

/**
 * A component that renders a dropdown for selecting an organization from a list of available organizations.
 * It also provides options to deselect the current organization or create a new one.
 *
 * @param {OrganizationSelectorProps} props - The props for the OrganizationSelector component.
 *
 * @returns {JSX.Element} The rendered OrganizationSelector component.
 */
export function OrganizationSelector({
    organization,
    organizations,
    onChangeOrganization,
    onAddOrganizationClick,
}: OrganizationSelectorProps): JSX.Element {
    const emptyTemplate = () => (
        <div className="flex flex-column gap-2">
            <span className="text-300 p-2">You're not in any organization.</span>
        </div>
    );

    const selectTemplate = (option: Organization | null) => {
        return (
            <div className="flex align-items-center gap-2">
                <FontAwesomeIcon className="text-300" icon={faBuildingUser} />
                <span className="text-100">{option.name}</span>
            </div>
        );
    };

    const valueTemplate = (option: Organization | null) => {
        return option ? (
            <div className="flex gap-2">
                <FontAwesomeIcon className="text-300" icon={faBuildingUser} />
                <span className="text-100">{option.name}</span>
            </div>
        ) : (
            'No organization selected'
        );
    };

    const footerTemplate = (
        <Button
            className="organization-dropdown-add"
            label="Create New"
            icon={PrimeIcons.PLUS}
            onClick={() => onAddOrganizationClick()}
            text
        />
    );

    return (
        <>
            <Dropdown
                className="organization-dropdown"
                pt={{
                    panel: { className: 'organization-dropdown-panel' },
                }}
                placeholder={'Select an organization'}
                options={organizations}
                value={organization}
                onChange={(e) => onChangeOrganization(e.value)}
                emptyMessage={emptyTemplate}
                itemTemplate={selectTemplate}
                valueTemplate={valueTemplate}
                panelFooterTemplate={footerTemplate}
            />
        </>
    );
}
