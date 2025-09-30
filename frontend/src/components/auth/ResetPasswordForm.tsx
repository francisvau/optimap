import React, { FormEvent, JSX } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { Password } from 'primereact/password';
import { type ResetPasswordRequest } from '@/types/schemas/Auth';
import { useForm } from '@/hooks/util/useForm';
import { usePasswordValidation } from '@/hooks/util/usePasswordValidation';
import { PasswordValidationMessage } from '@/components/auth/PasswordValidation';

export type ResetPasswordFormProps = {
    error: string | null;
    isLoading: boolean;
    onSubmit: (password: ResetPasswordRequest) => Promise<void>;
};
/**
 * ResetPasswordForm component
 *
 * This component renders a form for users to reset their password.
 *
 * @param {Object} props - The component props
 * @param {string | null} props.error - The error message to display, if any
 * @param {boolean} props.isLoading - Indicates if the form is in a loading state
 * @param {Function} props.onSubmit - Function to handle form submission
 *
 * @returns {JSX.Element} The rendered ResetPasswordForm component
 */
export function ResetPasswordForm({
    onSubmit,
    error,
    isLoading,
}: ResetPasswordFormProps): JSX.Element {
    const { form, handleChange } = useForm({
        newPassword: '',
        confirmPassword: '',
        token: '',
    });

    const { feedbackMessages, validatePassword } = usePasswordValidation();
    const passwordsMatch = form.newPassword === form.confirmPassword && form.newPassword.length > 0;
    const canSubmit = passwordsMatch && feedbackMessages.length === 0;

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        handleChange(e);
        validatePassword(e.target.value);
    };
    const handleSubmit = async (e: FormEvent): Promise<void> => {
        e.preventDefault();
        if (canSubmit) {
            await onSubmit(form);
        }
    };

    return (
        <div className="flex align-items-center justify-content-center">
            <Card className="inline-block" style={{ maxWidth: '600px' }}>
                <h1 className="m-0">Reset your password</h1>
                <p className="my-4">Enter your new password </p>
                {form.newPassword.length > 0 && (
                    <PasswordValidationMessage feedbackMessages={feedbackMessages} />
                )}
                {error && (
                    <Message severity="error" text={error} className="mb-4 w-full text-center" />
                )}
                <form onSubmit={handleSubmit}>
                    <div className="grid formgrid">
                        <div className="field col-12">
                            <label htmlFor="newPassword">New Password</label>
                            <Password
                                id="newPassword"
                                name="newPassword"
                                placeholder="Enter new password"
                                toggleMask
                                value={form.newPassword}
                                onChange={handlePasswordChange}
                                required
                                feedback={false}
                            />
                        </div>
                        <div className="field col-12">
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <Password
                                id="confirmPassword"
                                name="confirmPassword"
                                toggleMask
                                feedback={false}
                                placeholder="Confirm new password"
                                value={form.confirmPassword}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className={`field col-12 mt-4`}>
                            <Button
                                type={'submit'}
                                className="w-full block transition-all"
                                iconPos="right"
                                label="Reset Password"
                                loading={isLoading}
                                disabled={!canSubmit}
                            />
                        </div>
                    </div>
                </form>
            </Card>
        </div>
    );
}
