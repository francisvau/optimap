import { useEffect, useState } from 'react';

/**
 * A custom hook that retains the latest non-undefined value of the provided loader.
 * This is useful for preserving data across renders when the loader value might temporarily
 * become undefined or null.
 *
 * @template T - The type of the loader data.
 * @param loader - The current value of the loader data.
 * @returns The latest non-undefined value of the loader data.
 */
export function useStickyLoaderData<T>(loader: T): T {
    const [data, setData] = useState(loader);

    useEffect(() => {
        if (loader) {
            setData(loader);
        }
    }, [loader]);

    return data;
}
