import { OutletProps, useLocation, useOutlet } from 'react-router';
import { SwitchTransition, Transition } from 'react-transition-group';
import { JSX, useEffect, useRef } from 'react';
import gsap from 'gsap';

/**
 * A React component that provides animated transitions for route outlets.
 *
 * This component uses `SwitchTransition` and `Transition` from the `react-transition-group`
 * library to handle animations when navigating between routes. It leverages GSAP for
 * smooth enter and exit animations.
 *
 * @param {OutletProps} props - The props for the `Outlet` component.
 * @param {any} props.context - The context passed to the `useOutlet` hook.
 *
 * @returns {JSX.Element} A container with animated transitions for the current route's outlet.
 */
export function Outlet({ context }: OutletProps): JSX.Element {
    const nodeRef = useRef<HTMLDivElement>(null);
    const location = useLocation();
    const outlet = useOutlet(context);

    const onEnter = () => {
        gsap.fromTo(
            nodeRef.current,
            { autoAlpha: 0, y: 20 },
            { autoAlpha: 1, y: 0, duration: 0.3 },
        );
    };

    const onExit = () => {
        gsap.to(nodeRef.current, {
            autoAlpha: 0,
            y: -20,
            duration: 0.3,
        });
    };

    useEffect(onEnter, []);

    return (
        <SwitchTransition>
            <Transition
                key={location.key}
                nodeRef={nodeRef}
                timeout={200}
                onEnter={onEnter}
                onExit={onExit}
            >
                <div ref={nodeRef}>{outlet}</div>
            </Transition>
        </SwitchTransition>
    );
}
