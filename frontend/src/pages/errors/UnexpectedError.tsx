import { JSX } from 'react';
import { Button } from 'primereact/button';
import { Panel } from 'primereact/panel';
import { useNavigate } from 'react-router';
import { PrimeIcons } from 'primereact/api';

/**
 * UnexpectedError component that renders an unexpected error page.
 * @returns {JSX.Element} The rendered UnexpectedError component.
 */
export function UnexpectedError(): JSX.Element {
    const navigate = useNavigate();

    return (
        <div
            className="relative justify-content-center flex align-items-center"
            style={{ minHeight: '100vh' }}
        >
            <Panel className="p-shadow-2" style={{ textAlign: 'center' }}>
                <h1
                    style={{
                        fontSize: '150px',
                        color: 'white',
                        marginBottom: '10px',
                        marginTop: '30px',
                    }}
                >
                    500
                </h1>
                <h3
                    style={{
                        color: 'white',
                        fontSize: '35px',
                        marginBottom: '30px',
                    }}
                >
                    UNEXPECTED ERROR
                </h3>
                <p style={{ color: 'white', marginLeft: '200px', marginRight: '200px' }}>
                    Something went wrong.
                </p>
                <Button
                    label="Retry"
                    onClick={() => navigate(0)}
                    icon={PrimeIcons.REPLAY}
                    iconPos="right"
                    className="my-4"
                />
            </Panel>
        </div>
    );
}
