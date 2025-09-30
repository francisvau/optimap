import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { OrganizationRole } from '@/types/models/User.ts';
import { Button } from 'primereact/button';
import { FormEvent, JSX, useState } from 'react';
import { InviteOrganizationRequest } from '@/types/schemas/Organization';
import { PrimeIcons } from 'primereact/api';
import { FormProps } from '@/types/Form';
import { Message } from 'primereact/message';

export type InviteOrganizationProps = FormProps<InviteOrganizationRequest> & {
    roles: OrganizationRole[];
};

/**
 * InviteOrganizationForm component provides a form for inviting a new member to an organization.
 *
 * @param {InviteOrganizationProps} props - The props for the component.
 * @returns {JSX.Element} The rendered InviteOrganizationForm component.
 */
export function InviteOrganizationForm({
    onSubmit,
    isLoading,
    error,
    roles,
}: InviteOrganizationProps): JSX.Element {
    const [newMember, setNewMember] = useState<InviteOrganizationRequest>({
        email: '',
        userRole: null,
    });

    const handleAddMember = (e: FormEvent) => {
        e.preventDefault();
        onSubmit(newMember);
    };

    return (
        <>
            {error && <Message className="w-full mb-4" severity="error" text={error} />}
            <form onSubmitCapture={handleAddMember}>
                <div className="grid formgrid">
                    <div className="col-12 field">
                        <label>Email</label>
                        <InputText
                            type={'email'}
                            placeholder={'Email'}
                            required
                            value={newMember.email || ''}
                            onChange={(e) => setNewMember({ ...newMember, email: e.target.value })}
                        />
                    </div>
                    <div className="col-12 field">
                        <label>Role in organization</label>
                        <Dropdown
                            required
                            value={newMember.userRole}
                            options={roles}
                            optionLabel="name"
                            onChange={(e) => setNewMember({ ...newMember, userRole: e.value })}
                            placeholder="Select a Role"
                        />
                    </div>
                    <div className="col-12 my-2">
                        <Button
                            icon={PrimeIcons.CHECK}
                            label="Save"
                            type={'submit'}
                            loading={isLoading}
                        />
                    </div>
                </div>
            </form>
        </>
    );
}
