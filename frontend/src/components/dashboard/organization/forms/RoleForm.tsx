import { FormEvent, JSX } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Checkbox } from 'primereact/checkbox';
import { useForm } from '@/hooks/util/useForm';
import { Permissions } from '@/types/models/User.ts';
import { RoleRequest } from '@/types/schemas/Organization';
import { formatPermission } from '@/utils/permissionUtils';
import { FormProps } from '@/types/Form';
import { Message } from 'primereact/message';

export type CreateRoleFormProps = FormProps<RoleRequest>;

/**
 * RoleForm component
 *
 * This component renders a compact form for creating new user roles with specific permissions.
 *
 * @param {CreateRoleFormProps} props - The component props
 *
 * @returns {JSX.Element} The rendered RoleForm component
 */
export function RoleForm({
    onSubmit,
    error,
    isLoading,
    initial,
}: CreateRoleFormProps): JSX.Element {
    const { form, handleChange, setForm } = useForm({
        name: initial?.name ?? '',
        permissions: initial?.permissions ?? [],
    });

    const handlePermissionChange = (perm: string) => {
        setForm((prevForm) => {
            const updatedPermissions = prevForm.permissions.includes(perm)
                ? prevForm.permissions.filter((p) => p !== perm)
                : [...prevForm.permissions, perm];
            return { ...prevForm, permissions: updatedPermissions };
        });
    };

    const handleSubmit = async (e: FormEvent): Promise<void> => {
        e.preventDefault();
        await onSubmit(form);
    };

    return (
        <>
            {error && <Message className="mb-4 w-full" severity="error" text={error} />}

            <form onSubmitCapture={handleSubmit}>
                <div className="grid formgrid">
                    <div className="col-12 field">
                        <label htmlFor="name" className="block mb-2">
                            Role Name
                        </label>
                        <InputText
                            id="name"
                            name="name"
                            type="text"
                            placeholder="Enter role name"
                            value={form.name}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <div className="col-12 field">
                        <label className="mb-3">Permissions</label>
                        <div className="flex flex-column gap-3">
                            {Object.entries(Permissions).map(([key, value]) => (
                                <div key={key} className="flex gap-2 align-items-center">
                                    <Checkbox
                                        className="w-auto"
                                        inputId={key}
                                        name="permissions"
                                        value={key}
                                        onChange={() => handlePermissionChange(value)}
                                        checked={form.permissions.includes(value)}
                                    />
                                    <label htmlFor={key} className="ml-2 font-normal">
                                        {formatPermission(value)}
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="col-12 my-2">
                        <Button
                            type="submit"
                            className="w-full"
                            label={initial ? 'Edit Role' : 'Create Role'}
                            disabled={isLoading}
                            loading={isLoading}
                        />
                    </div>
                </div>
            </form>
        </>
    );
}
