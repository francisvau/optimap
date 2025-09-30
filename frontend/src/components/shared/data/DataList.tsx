import { useState, useMemo, JSX } from 'react';
import { DataView, DataViewProps } from 'primereact/dataview';
import { Dropdown, DropdownChangeEvent } from 'primereact/dropdown';
import { InputText } from 'primereact/inputtext';
import { InputIcon } from 'primereact/inputicon';
import { IconField } from 'primereact/iconfield';
import { OnSort, OnSearch, SortOption, SortField } from '@/types/Filter';
import { SortOrder } from 'primereact/datatable';

export type DataListProps<T> = Omit<DataViewProps, 'value' | 'sortField'> & {
    value?: T[];
    onSearch?: OnSearch;
    onSort?: OnSort<T>;
    sortOptions: SortOption<T>[];
    sortField?: SortField<T>;
    searchQuery?: string;
};

/**
 * A generic, reusable component for displaying a list of data with sorting, searching, and pagination capabilities.
 *
 * @template T - The type of the data items in the list.
 *
 * @param {props} props - The properties for the DataList component.
 *
 * @returns {JSX.Element} A `DataView` component with a header for sorting and searching, and a customizable list template.
 */
export function DataList<T>({
    value,
    onSearch,
    onSort,
    sortOptions,
    sortField: initialSortField,
    searchQuery = '',
    itemTemplate,
    ...props
}: DataListProps<T>): JSX.Element {
    const [sortField, setSortField] = useState(initialSortField ?? sortOptions[0]?.value);
    const [sortOrder, setSortOrder] = useState<SortOrder>(1);
    const [localSearch, setLocalSearch] = useState(searchQuery);

    const sortDirectionOptions = useMemo(
        () => [
            { label: 'Ascending', value: 1 },
            { label: 'Descending', value: -1 },
        ],
        [],
    );

    const handleSortChange = (field: SortField<T>) => {
        setSortField(field);
        onSort?.(field, sortOrder);
    };

    const handleOrderChange = (order: SortOrder) => {
        setSortOrder(order);
        onSort?.(sortField, order);
    };

    const handleSearch = (query: string) => {
        setLocalSearch(query);
        onSearch?.(query);
    };

    const listTemplate = useMemo(
        () =>
            value
                ? (items: T[]) => (
                      <div className="grid p-4 gap-4">
                          {items.map((item, index) => (
                              <div className="col-12" key={index}>
                                  {itemTemplate?.(item)}
                              </div>
                          ))}
                      </div>
                  )
                : undefined,
        [itemTemplate, value],
    );

    const header = (
        <div className="flex flex-wrap align-items-center justify-content-between gap-4 p-4">
            <p className="m-0">{props.totalRecords ?? value?.length ?? 0} items found</p>
            <div className="flex align-items-center gap-3">
                <div className="flex align-items-center flex-wrap gap-2">
                    <Dropdown
                        value={sortField}
                        options={sortOptions}
                        onChange={(e: DropdownChangeEvent) => handleSortChange(e.value)}
                        placeholder="Sort by"
                        className="w-10rem"
                    />
                    <Dropdown
                        value={sortOrder}
                        options={sortDirectionOptions}
                        onChange={(e: DropdownChangeEvent) => handleOrderChange(e.value)}
                        className="w-10rem"
                    />
                    {onSearch && (
                        <IconField iconPosition="left">
                            <InputIcon className="pi pi-search" />
                            <InputText
                                value={localSearch}
                                onChange={(e) => handleSearch(e.target.value)}
                                placeholder="Search items"
                            />
                        </IconField>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <DataView
            {...props}
            header={header}
            value={value}
            listTemplate={listTemplate}
            sortField={!props.lazy && sortField?.toString()}
            sortOrder={!props.lazy && sortOrder}
        />
    );
}
