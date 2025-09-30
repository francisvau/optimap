import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';
import { useToast } from '@/hooks/context/ToastProvider/ToastContext';
import { PrimeIcons } from 'primereact/api';
import { Avatar } from 'primereact/avatar';
import { Button } from 'primereact/button';
import { Menu } from 'primereact/menu';
import { Skeleton } from 'primereact/skeleton';
import { JSX, useRef } from 'react';
import { useNavigate } from 'react-router';

/**
 * UserMenu component displays a user avatar and a dropdown menu with user-related actions.
 *
 * @component
 *
 * @returns {JSX.Element} The rendered UserMenu component.
 */
export function UserMenu(): JSX.Element {
    const { user, isLoading, logout } = useAuth();

    const menuRef = useRef<Menu>(null);
    const navigate = useNavigate();
    const toast = useToast();

    const menuItems = user
        ? [
              {
                  label: `${user.firstName} ${user.lastName}`,
                  icon: PrimeIcons.USER,
                  disabled: true,
              },
              {
                  label: 'Settings',
                  icon: PrimeIcons.COG,
                  command: async () => {
                      await navigate('/auth/me');
                  },
              },
              {
                  label: 'Logout',
                  icon: PrimeIcons.LOCK,
                  command: async () => {
                      await logout();
                      navigate('/auth/login');
                      toast({ severity: 'info', detail: 'Logged out successfully' });
                  },
              },
          ]
        : [];

    const initials = `${user?.firstName?.[0] ?? ''}${user?.lastName?.[0] ?? ''}`;

    return user ? (
        <>
            <Avatar
                shape="circle"
                label={initials}
                onClick={(event) => menuRef.current?.toggle(event)}
            />
            <Menu
                model={menuItems}
                ref={menuRef}
                style={{ background: 'var(--surface-100)' }}
                popup
            />
        </>
    ) : isLoading ? (
        <Skeleton shape="circle" width="2rem" height="2rem" />
    ) : (
        <Button
            label="Login"
            icon={PrimeIcons.SIGN_IN}
            onClick={() => navigate('/auth/login')}
            rounded
            outlined
        />
    );
}
