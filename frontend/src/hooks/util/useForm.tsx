import { useState, useCallback } from 'react';

export type UseForm<T extends Record<string, unknown>> = {
    form: T;
    updateForm: <K extends keyof T>(field: K, value: T[K]) => void;
    handleChange: (e: React.ChangeEvent<{ name: string; value: string | number }>) => void;
    resetForm: () => void;
    setForm: React.Dispatch<React.SetStateAction<T>>;
};

/**
 * A custom hook for managing form state in a React component.
 *
 * @template T - The shape of the form state, extending a record of string keys to any values.
 * @param {T} initialState - The initial state of the form.
 * @returns {UseForm<T>} An object containing form state and methods for updating and resetting the form.
 */
export function useForm<T extends Record<string, unknown>>(initialState: T): UseForm<T> {
    const [form, setForm] = useState<T>(initialState);

    const updateForm = useCallback(<K extends keyof T>(field: K, value: T[K]) => {
        setForm((prev) => ({
            ...prev,
            [field]: value,
        }));
    }, []);

    const handleChange = useCallback(
        (e: React.ChangeEvent<{ name: string; value: string | number }>) => {
            const { name, value } = e.target;
            setForm((prev) => ({
                ...prev,
                [name]: value,
            }));
        },
        [],
    );

    const resetForm = useCallback(() => {
        setForm(initialState);
    }, [initialState]);

    return {
        form,
        updateForm,
        handleChange,
        resetForm,
        setForm,
    };
}
