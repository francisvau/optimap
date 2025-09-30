export type FormProps<T> = {
    isLoading: boolean;
    error?: string | null;
    initial?: T;
    onSubmit: (form: T) => Promise<unknown>;
};
