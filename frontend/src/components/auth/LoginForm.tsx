import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Password } from 'primereact/password';
import { FormEvent, JSX, useState } from 'react';
import { Message } from 'primereact/message';
import type { LoginRequest } from '@/types/schemas/Auth';
import { FormProps } from '@/types/Form';
import { NavLink } from 'react-router';

/**
 * LoginForm component renders a login form with email and password fields.
 * It allows users to sign in to their Optimap Prime account.
 *
 * @param {LoginFormProps} props - The properties for the LoginForm component.
 * @param {function} props.onSubmit - The function to call when the form is submitted.
 *
 * @returns {JSX.Element} The rendered login form component.
 */
export function LoginForm({ onSubmit, error, isLoading }: FormProps<LoginRequest>): JSX.Element {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        void onSubmit({ email, password });
    };

    return (
        <Card className="inline-block w-full" style={{ maxWidth: '600px' }}>
            <h1 className="m-0">Sign in to your account</h1>
            <p className="my-4">
                Sign in to your Optimap Prime account to access your data mapping jobs.
            </p>
            {error && <Message severity="error" text={error} className="mb-4 w-full text-center" />}
            <form onSubmitCapture={handleSubmit}>
                <div className="formgrid grid">
                    <div className="field col-12">
                        <label htmlFor="email">Email</label>
                        <InputText
                            id="email"
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        ></InputText>
                    </div>
                    <div className="field col-12">
                        <label htmlFor="password">Password</label>
                        <Password
                            inputId="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Password"
                            toggleMask
                            feedback={false}
                            required
                        ></Password>
                        <NavLink to="/auth/password/forgot" className="mt-3 mb-1 block text-left">
                            Forgot password? Reset it here.
                        </NavLink>
                    </div>
                </div>
                <Button
                    className="mt-3 w-full"
                    label="Submit"
                    loading={isLoading}
                    iconPos="right"
                ></Button>
            </form>

            <NavLink to="/auth/register" className="block mt-4 text-center">
                No account yet? Register here.
            </NavLink>
        </Card>
    );
}
