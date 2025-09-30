import { JSX } from 'react';
import { Panel } from 'primereact/panel';
import { NavLink } from 'react-router';
import logo from '@/assets/img/logo/logo-rect-white.png';
import { PrimeIcons } from 'primereact/api';
import clsx from 'clsx';

/**
 * Footer component that renders a button.
 * @returns {JSX.Element} The rendered footer component.
 */
export function Footer(): JSX.Element {
    return (
        <Panel>
            <div className="px-3 py-4 w-12 md:w-10 mx-auto grid">
                <div className="col-12 md:col-4 flex justify-content-center">
                    <img
                        src={logo}
                        style={{
                            maxWidth: '175px',
                            height: 'auto',
                            objectFit: 'contain',
                        }}
                    />
                </div>

                <div className="col-12 md:col-4 flex justify-content-center align-items-center">
                    <p className="text-md">
                        Tired of manual, time-consuming data mapping? <br />
                        Our solution automates the process using AI, making data integration
                        seamless, accurate, and adaptable—no technical expertise required.
                    </p>
                </div>

                <div className="col-12 md:col-4 flex justify-content-center">
                    <div className="flex flex-column gap-3 align-items-start">
                        <NavLink
                            to={'/auth/login'}
                            className="flex align-items-center text-white no-underline mr-4"
                        >
                            <i className={clsx(PrimeIcons.USER, 'text-400', 'mr-2', 'text-xl')} />
                            <span>Login</span>
                        </NavLink>

                        <NavLink
                            to={'/auth/register'}
                            className="flex align-items-center text-white no-underline mr-4"
                        >
                            <i
                                className={clsx(
                                    PrimeIcons.USER_PLUS,
                                    'text-400',
                                    'mr-2',
                                    'text-xl',
                                )}
                            />
                            <span>Register</span>
                        </NavLink>

                        <NavLink
                            to={'/dashboard/blueprints'}
                            className="flex align-items-center text-white no-underline"
                        >
                            <i
                                className={clsx(
                                    PrimeIcons.PLUS_CIRCLE,
                                    'text-400',
                                    'mr-2',
                                    'text-xl',
                                )}
                            />
                            <span>Manage Blueprints</span>
                        </NavLink>
                    </div>
                </div>
            </div>
        </Panel>
    );
}
