import React, { CSSProperties, JSX, useState } from 'react';

export type AnimatedImageProps = {
    src: string;
    maxTilt?: number;
};

/**
 * Component that renders an image with a 3D tilt effect based on mouse movement.
 *
 * @param {Object} props - The properties object.
 * @param {string} props.src - The source URL of the image.
 * @param {number} [props.maxTilt=15] - The maximum tilt angle in degrees.
 * @returns {JSX.Element} The rendered AnimatedImage component.
 *
 */
export function AnimatedImage({ src, maxTilt = 10 }: AnimatedImageProps): JSX.Element {
    const [transformStyle, setTransformStyle] = useState<string>(
        'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)',
    );

    const handleMouseMove = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
        const element = event.currentTarget;
        const rect = element.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const halfWidth = rect.width / 2;
        const halfHeight = rect.height / 2;

        const rotateY = ((x - halfWidth) / halfWidth) * maxTilt;
        const rotateX = -((y - halfHeight) / halfHeight) * maxTilt;

        setTransformStyle(
            `perspective(${rect.width}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
        );
    };

    const handleMouseLeave = () => {
        setTransformStyle('perspective(1000px) rotateX(0deg) rotateY(0deg)');
    };

    return (
        <div onMouseLeave={handleMouseLeave} className="relative">
            <img
                src={src}
                onMouseMove={handleMouseMove}
                alt="Animated"
                style={{ ...imageStyle, transform: transformStyle }}
            />
            <div className="radar" />
        </div>
    );
}

const imageStyle: CSSProperties = {
    width: '100%',
    height: 'auto',
    willChange: 'transform',
    transition: 'transform 0.1s ease-out',
};
