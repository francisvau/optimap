import { gsap } from 'gsap/gsap-core';

export type AnimationOptions = {
    duration?: number;
    ease?: string;
    expandTweenVars?: gsap.TweenVars;
    collapseTweenVars?: gsap.TweenVars;
};

/**
 * Animates the expansion or collapse of an HTML element using GSAP.
 *
 * @param {HTMLElement|null} element - The HTML element to animate. If `null`, the function will return early.
 * @param {bool} isExpanded - A boolean indicating whether the element should expand (`true`) or collapse (`false`).
 * @param {AnimationOptions} options - Optional configuration for the animation.
 *
 * @returns A cleanup function that, when called, will kill the GSAP timeline and stop the animation.
 */
export async function animateExpandCollapse(
    element: HTMLElement | null,
    isExpanded: boolean,
    options?: AnimationOptions,
) {
    if (!element) return;

    const tl = gsap.timeline({
        defaults: {
            duration: options?.duration ?? 0.3,
            ease: options?.ease ?? 'power2.inOut',
        },
    });

    if (isExpanded) {
        await tl.to(element, {
            height: 'auto',
            opacity: 1,
            ...(options?.expandTweenVars || {}),
        });
    } else {
        await tl.to(element, {
            height: 0,
            opacity: 0,
            ...(options?.collapseTweenVars || {}),
        });
    }

    return () => void tl.kill();
}
