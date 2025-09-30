import { useEffect, useState } from 'react';

/**
 * A custom React hook that debounces a value. It delays updating the returned value
 * until after a specified delay has passed since the last change to the input value.
 *
 * @template T - The type of the value to debounce.
 * @param value - The input value to debounce.
 * @param delay - The debounce delay in milliseconds.
 *
 * @returns The debounced value, which updates only after the specified delay.
 */
export function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]);

    return debouncedValue;
}
