import React, { FormEvent, JSX } from 'react';
import { InputText } from 'primereact/inputtext';
import { NavLink, useSearchParams } from 'react-router';
import { Card } from 'primereact/card';
import { Password } from 'primereact/password';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { type RegisterRequest } from '@/types/schemas/Auth';
import { useForm } from '@/hooks/util/useForm';
import { usePasswordValidation } from '@/hooks/util/usePasswordValidation';
import { PasswordValidationMessage } from '@/components/auth/PasswordValidation';

export type RegisterFormProps = {
    error: string | null;
    isLoading: boolean;
    onSubmit: (profile: RegisterRequest) => Promise<unknown>;
};

/**
 * A React component that renders a registration form for creating a new account.
 * The form includes fields for first name, last name, email, and password, and
 * provides validation for required fields. It also displays an error message if
 * provided and shows a loading state during form submission.
 *
 * @param {RegisterFormProps} props - The props for the RegisterForm component.
 *
 * @returns {JSX.Element} The rendered RegisterForm component.
 */
export function RegisterForm({ onSubmit, error, isLoading }: RegisterFormProps): JSX.Element {
    const { form, handleChange } = useForm({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        token: '',
    });

    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const email = searchParams.get('email');
    if (token) {
        form.token = token;
    }
    console.log(token);
    if (email) {
        form.email = email;
    }
    const { feedbackMessages, validatePassword } = usePasswordValidation();

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        handleChange(e);
        validatePassword(e.target.value);
    };
    const handleSubmit = async (e: FormEvent): Promise<void> => {
        e.preventDefault();
        if (feedbackMessages.length === 0) {
            await onSubmit(form);
        }
    };

    return (
        <Card className="inline-block" style={{ maxWidth: '600px' }}>
            <h1 className="m-0">Create your account</h1>
            <p className="my-4">
                Create your Optimap Prime account and start your first data mapping job within 5
                minutes.
            </p>
            {form.password.length > 0 && (
                <PasswordValidationMessage feedbackMessages={feedbackMessages} />
            )}
            {error && <Message severity="error" text={error} className="mb-4 w-full text-center" />}
            <form onSubmitCapture={handleSubmit}>
                <div className="formgrid grid">
                    <div className="field col-6">
                        <label htmlFor="firstName">First Name</label>
                        <InputText
                            id="firstName"
                            name="firstName"
                            placeholder="First Name"
                            value={form.firstName}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <div className="field col-6">
                        <label htmlFor="lastName">Last Name</label>
                        <InputText
                            id="lastName"
                            name="lastName"
                            placeholder="Last Name"
                            value={form.lastName}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    {!token && (
                        <div className="field col-12">
                            <label htmlFor="email">Email</label>
                            <InputText
                                id="email"
                                name="email"
                                type="email"
                                placeholder="Email"
                                value={form.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    )}

                    <div className="field col-12">
                        <label htmlFor="password">Password</label>
                        <Password
                            inputId="password"
                            name="password"
                            value={form.password}
                            onChange={handlePasswordChange}
                            placeholder="Password"
                            toggleMask
                            feedback={false}
                            required
                        />
                    </div>
                </div>
                <Button
                    className="mt-4 w-full"
                    iconPos="right"
                    label="Submit"
                    loading={isLoading}
                    disabled={feedbackMessages.length > 0}
                />
            </form>

            <NavLink to="/auth/login" className="block mt-4 w-full text-center">
                Already have an account? Login Instead
            </NavLink>
        </Card>
    );
}
