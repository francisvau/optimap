import { InputDefinition, SourceMapping, MappingBlueprint } from '@/types/models/Blueprint';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { JSX, useMemo, useState } from 'react';
import { NavLink } from 'react-router';
import { DataList } from '@/components/shared/data/DataList';
import { SortOption } from '@/types/Filter';
import { TreeNode, TreeNodeComponent } from '@/components/shared/data/tree/Tree';
import { dataTypeIcons } from '@/utils/fileUtils';

export type BlueprintProps = {
    blueprint: MappingBlueprint;
    onDeleteClick?: (blueprint: MappingBlueprint) => Promise<unknown>;
};

/**
 * Represents a blueprint component that renders details of a blueprint.
 *
 * @param {BlueprintProps} props - The props for the component.
 *
 * @returns A JSX element representing the blueprint.
 */
export function Blueprint({ blueprint, onDeleteClick }: BlueprintProps): JSX.Element {
    const tree = useMemo<TreeNode>(() => {
        return {
            icon: 'pi pi-bullseye',
            children: blueprint.inputDefinitions.slice(0, 3).map((schema: InputDefinition) => ({
                icon: PrimeIcons.CLOUD_DOWNLOAD,
                tooltip: schema.name,
                children: schema.sourceMappings.map((mapping: SourceMapping) => ({
                    icon: dataTypeIcons[mapping.fileType ?? 'JSON'],
                    tooltip: mapping.name,
                })),
            })),
        };
    }, [blueprint]);

    return (
        <div className="grid align-items-center">
            <div className="col-12 md:col-4">
                <TreeNodeComponent node={tree} />
            </div>
            <div className="col-12 md:col-8 text-200">
                <h2 className="flex align-items-center justify-content-between mt-0">
                    {blueprint.name}
                    <Button
                        onClick={() => onDeleteClick(blueprint)}
                        icon={PrimeIcons.TRASH}
                        tooltip="Delete blueprint"
                        severity="danger"
                        outlined
                    />
                </h2>
                <div className="flex align-items-center gap-2 mb-4">
                    <Tag value={`${blueprint.usageCount} usage(s)`} severity="contrast" />
                    <Tag
                        value={`Created on ${new Date(blueprint.createdAt).toLocaleDateString()}`}
                        severity="contrast"
                    />
                </div>
                <p className="mb-4">{blueprint.description}</p>
                <NavLink to={`/dashboard/blueprints/${blueprint.id}?select`}>
                    <Button label="Open editor" icon={PrimeIcons.SLIDERS_H} />
                </NavLink>
            </div>
        </div>
    );
}

export type BlueprintListProps = {
    blueprints?: MappingBlueprint[];
    isLoading: boolean;
    isError: boolean;
    onDeleteClick?: (blueprint: MappingBlueprint) => Promise<unknown>;
};

/**
 * A React component that displays a list of mapping blueprints in a structured format.
 * It uses a callback to render each blueprint item and handles loading and error states.
 *
 * @param {BlueprintListProps} props - The props for the component.
 *
 * @returns {JSX.Element} The rendered BlueprintList component.
 *
 */
export function BlueprintList({
    blueprints,
    isLoading,
    onDeleteClick,
}: BlueprintListProps): JSX.Element {
    const [search, setSearch] = useState<string>('');

    const sortOptions = useMemo<SortOption<MappingBlueprint>[]>(
        () => [
            { label: 'Name', value: 'name' },
            { label: 'Creation Date', value: 'createdAt' },
            { label: 'Usage Count', value: 'usageCount' },
        ],
        [],
    );

    const items = useMemo<MappingBlueprint[]>(
        () =>
            blueprints?.filter((blueprint) =>
                blueprint.name.toLowerCase().includes(search.toLowerCase()),
            ),
        [blueprints, search],
    );

    return (
        <DataList<MappingBlueprint>
            value={items}
            loading={isLoading}
            onSearch={setSearch}
            itemTemplate={(blueprint) => (
                <Blueprint blueprint={blueprint} onDeleteClick={onDeleteClick} />
            )}
            sortOptions={sortOptions}
            rows={4}
            paginator
        />
    );
}
