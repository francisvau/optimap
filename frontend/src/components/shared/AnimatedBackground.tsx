import wallpaper from '@/assets/img/wallpaper.jpg';
import { CSSProperties, JSX } from 'react';

/**
 * AnimatedBackground component renders a background with an overlay and an image.
 *
 * @returns {JSX.Element} The JSX code for rendering the animated background.
 */
export function AnimatedBackground(): JSX.Element {
    const positionStyles: CSSProperties = {
        position: 'absolute',
        width: '100vw',
        height: '100%',
        minHeight: '100vh',
        top: '0',
        left: '0',
    };

    const overlayStyles: CSSProperties = {
        opacity: 0.25,
        inset: 0,
        backgroundImage: 'radial-gradient(var(--primary-color) 1px, transparent 1px)',
        backgroundSize: '1.25rem 1.25rem',
    };

    const imageStyles: CSSProperties = {
        objectFit: 'cover',
        objectPosition: 'center',
        opacity: 0.1,
    };

    return (
        <div
            style={{
                pointerEvents: 'none',
                zIndex: -1,
                height: '100%',
            }}
        >
            <div
                style={{
                    ...positionStyles,
                    ...overlayStyles,
                }}
            ></div>
            <img
                style={{
                    ...positionStyles,
                    ...imageStyles,
                }}
                src={wallpaper}
            ></img>
        </div>
    );
}
