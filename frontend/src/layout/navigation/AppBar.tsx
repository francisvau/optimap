import { Menubar } from 'primereact/menubar';
import { NavLink, useNavigate } from 'react-router';
import { UserMenu } from './UserMenu';
import { JSX } from 'react';
import { PrimeIcons } from 'primereact/api';
import { MenuItem } from 'primereact/menuitem';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import LogoImage from '@/assets/img/logo/logo-rect-white.png';

/**
 * AppBar component renders a navigation bar with menu items and a user menu.
 *
 * @param root0
 * @param root0
 * @returns {JSX.Element} The rendered AppBar component.
 */
export function AppBar({ ...props }): JSX.Element {
    const { user } = useAuth();
    const navigate = useNavigate();

    // Base menu items for all authenticated users
    const baseMenuItems: MenuItem[] = [
        {
            label: 'Dashboard',
            icon: PrimeIcons.SITEMAP,
            command: () => {
                navigate('/dashboard');
            },
        },
    ];

    // Additional menu items for admin users
    const adminMenuItems: MenuItem[] = [
        {
            label: 'Logs',
            icon: PrimeIcons.BOOK,
            command: () => {
                navigate('/admin');
            },
        },
        {
            label: 'Users',
            icon: PrimeIcons.USER,
            command: () => {
                navigate('/admin/users');
            },
        },
        {
            label: 'Organizations',
            icon: PrimeIcons.BUILDING,
            command: () => {
                navigate('/admin/organizations');
            },
        },
        {
            label: 'System Monitoring',
            icon: PrimeIcons.COG,
            command: () => {
                window.open(
                    'https://admin.optimaprime.be/d/rYdddlPWk/node-exporter-full?orgId=1&refresh=1m',
                    '_blank',
                );
            },
        },
    ];

    const items: MenuItem[] = user
        ? user.isAdmin
            ? [...baseMenuItems, ...adminMenuItems]
            : [...baseMenuItems]
        : [];

    return (
        <Menubar
            {...props}
            model={items}
            start={
                <div className="flex h-full align-items-center">
                    <NavLink to="/">
                        <img className="mr-3" src={LogoImage} style={{ height: '50px' }} />
                    </NavLink>
                </div>
            }
            end={<UserMenu />}
        ></Menubar>
    );
}
