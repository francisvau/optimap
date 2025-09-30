import { JSX } from 'react';
import React from 'react';
import { Button } from 'primereact/button';
import { useNavigate } from 'react-router';
import { Panel } from 'primereact/panel';
import { PrimeIcons } from 'primereact/api';

/**
 * NotFound component that renders a 404 error page.
 * @returns {JSX.Element} The rendered NotFound component.
 */
export function NotFound(): JSX.Element {
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
                    404
                </h1>
                <h3
                    style={{
                        color: 'white',
                        fontSize: '35px',
                        marginBottom: '30px',
                    }}
                >
                    NOT FOUND
                </h3>
                <p style={{ color: 'white', marginLeft: '50px', marginRight: '50px' }}>
                    The requested page was not found. Please check the URL or return to the
                    homepage.
                </p>
                <Button
                    label="Back to homepage"
                    icon={PrimeIcons.HOME}
                    onClick={() => navigate('/')}
                    style={{ marginTop: '30px', marginBottom: '30px' }}
                />
            </Panel>
        </div>
    );
}
