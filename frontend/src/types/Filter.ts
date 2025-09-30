export type SortOption<T> = {
    label: string;
    value: keyof T;
};

export type SortField<T> = keyof T;
export type SortOrder = -1 | 0 | 1;

export type OnSearch = (query: string) => void;
export type OnSort<T> = (field: keyof T, order: SortOrder) => void;
