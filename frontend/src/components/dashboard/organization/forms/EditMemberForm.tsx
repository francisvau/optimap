import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { FormEvent, JSX, useState } from 'react';
import { EditMemberRoleRequest } from '@/types/schemas/Organization';
import { OrganizationRole } from '@/types/models/User';
import { PrimeIcons } from 'primereact/api';
import { FormProps } from '@/types/Form';
import { OrganizationUser } from '@/types/models/Organization';

export type EditMemberFormProps = Omit<FormProps<EditMemberRoleRequest>, 'initial'> & {
    roles: OrganizationRole[];
    initial: OrganizationUser;
};

/**
 * InviteOrganizationForm component provides a form for inviting a new member to an organization.
 *
 * @param {InviteOrganizationProps} props - The props for the component.
 * @returns {JSX.Element} The rendered InviteOrganizationForm component.
 */
export function EditMemberForm({ onSubmit, roles, initial }: EditMemberFormProps): JSX.Element {
    const [updatedMember, setUpdatedMember] = useState<EditMemberRoleRequest>({
        role: initial?.role.id ?? null,
    });

    const handleEditMember = (e: FormEvent) => {
        e.preventDefault();
        onSubmit(updatedMember);
    };

    return (
        <form onSubmitCapture={handleEditMember}>
            <div className="grid formgrid">
                <div className="col-12 field">
                    <label>Organization User Role</label>
                    <Dropdown
                        required
                        value={updatedMember.role}
                        onChange={(e) => {
                            setUpdatedMember({
                                ...updatedMember,
                                role: e.value,
                            });
                        }}
                        options={roles.map((role) => ({ label: role.name, value: role.id }))}
                        placeholder="Select a Role"
                    />
                </div>
                <div className="col-12 my-2">
                    <Button icon={PrimeIcons.CHECK} label="Save User Role" type={'submit'} />
                </div>
            </div>
        </form>
    );
}
