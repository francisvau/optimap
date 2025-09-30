import React, { FormEvent, JSX } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Card } from 'primereact/card';
import { type ForgotPasswordRequest } from '@/types/schemas/Auth';
import { useForm } from '@/hooks/util/useForm';
import { Message } from 'primereact/message';

export type ForgotPasswordFormProps = {
    error: string | null;
    isLoading: boolean;
    onSubmit: (email: ForgotPasswordRequest) => Promise<unknown>;
};

/**
 * ForgotPasswordForm component
 *
 * This component renders a form for users to request a password reset link.
 *
 * @param {Object} props - The component props
 * @param {string | null} props.error - The error message to display, if any
 * @param {boolean} props.isLoading - Indicates if the form is in a loading state
 * @param {Function} props.onSubmit - Function to handle form submission
 *
 * @returns {JSX.Element} The rendered ForgotPasswordForm component
 */
export function ForgotPasswordForm({
    onSubmit,
    error,
    isLoading,
}: ForgotPasswordFormProps): JSX.Element {
    const { form, handleChange } = useForm({
        email: '',
    });

    const handleSubmit = async (e: FormEvent): Promise<void> => {
        e.preventDefault();
        await onSubmit(form);
    };

    return (
        <>
            <div className="flex align-items-center justify-content-center">
                <Card className="inline-block" style={{ maxWidth: '600px' }}>
                    <h1 className="m-0">Reset your password</h1>
                    <p className="my-4">
                        Enter your email address to receive a password reset link.
                    </p>
                    {error && (
                        <Message
                            severity="error"
                            text={error}
                            className="mb-4 w-full text-center"
                        />
                    )}
                    <form onSubmitCapture={handleSubmit}>
                        <div className="grid formgrid">
                            <div className="field col-12">
                                <label htmlFor="email">Email</label>
                                <InputText
                                    id="email"
                                    name="email"
                                    type="email"
                                    placeholder="Email address"
                                    value={form.email}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="field col-12">
                                <Button
                                    className="mt-4 w-full"
                                    iconPos="right"
                                    label="Send Reset Link"
                                    disabled={isLoading}
                                    loading={isLoading}
                                ></Button>
                            </div>
                        </div>
                    </form>
                </Card>
            </div>
        </>
    );
}
