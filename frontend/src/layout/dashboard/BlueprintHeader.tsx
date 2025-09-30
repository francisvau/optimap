import { MappingBlueprint, InputDefinition } from '@/types/models/Blueprint';
import { InputDefinition as InputDefinitionItem } from '@/components/dashboard/blueprints/definition/InputDefinition';
import { PrimeIcons } from 'primereact/api';
import { Button } from 'primereact/button';
import { Skeleton } from 'primereact/skeleton';
import { JSX, useRef, useState } from 'react';
import { NavLink } from 'react-router';
import { gsap } from 'gsap';
import clsx from 'clsx';

type BlueprintHeaderProps = {
    blueprint: MappingBlueprint | null;
    definition: InputDefinition | null;
    versions?: InputDefinition[];
    onVersionClick?: (version: InputDefinition) => void;
    onVersionCreateClick?: (version: InputDefinition) => void;
    onDefinitionClick: () => void;
    onDeleteDefinitionClick: (definition: InputDefinition) => void;
};

/**
 * Renders the header section for a blueprint, including its name, description,
 * and an optional input definition. The component displays a skeleton loader
 * if the input definition is not available.
 *
 * @param {BlueprintHeaderProps} props - The properties for the BlueprintHeader component.
 *
 * @returns {JSX.Element} The rendered BlueprintHeader component.
 */
export function BlueprintHeader({
    blueprint,
    definition,
    versions,
    onVersionClick,
    onVersionCreateClick,
    onDefinitionClick,
    onDeleteDefinitionClick,
}: BlueprintHeaderProps): JSX.Element {
    const [collapsed, setCollapsed] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const toggleHeader = () => {
        const targets = [containerRef.current!];

        if (collapsed) {
            gsap.to(targets, {
                height: 'auto',
                duration: 0.3,
                opacity: 1,
            });
        } else {
            gsap.to(targets, {
                height: 0,
                duration: 0.3,
                opacity: 0,
            });
        }
        setCollapsed(!collapsed);
    };

    return (
        <>
            <div className="flex justify-content-between mb-2">
                <NavLink to="/dashboard/blueprints">
                    <Button
                        style={{ marginLeft: '-.5rem' }}
                        icon={PrimeIcons.ARROW_LEFT}
                        label="Back to blueprints"
                        link
                    />
                </NavLink>
                <Button
                    icon={collapsed ? PrimeIcons.CHEVRON_DOWN : PrimeIcons.CHEVRON_UP}
                    label={collapsed ? 'Expand Details' : 'Collapse Details'}
                    onClick={toggleHeader}
                    text
                />
            </div>

            <div
                className="flex justify-content-between align-items-center overflow-hidden"
                ref={containerRef}
            >
                <div className="w-12 lg:w-5">
                    {!blueprint ? (
                        <>
                            <Skeleton width="30rem" height="40px" />
                            <Skeleton width="20rem" height="22px" className="mt-4" />
                        </>
                    ) : (
                        <>
                            <div className="flex align-items-center justify-content-between w-full gap-3">
                                <h1 className="flex align-items-center gap-3 text-4xl my-4">
                                    <i className={clsx(PrimeIcons.MAP, 'text-primary text-3xl')} />
                                    <span>{blueprint.name}</span>
                                </h1>
                                <NavLink to={`/dashboard/blueprints/${blueprint.id}/edit`}>
                                    <Button
                                        icon={PrimeIcons.PENCIL}
                                        label="Edit Output Definition"
                                        outlined
                                    />
                                </NavLink>
                            </div>
                            <p>{blueprint.description}</p>
                        </>
                    )}
                </div>

                <div style={{ maxWidth: '550px' }} className="w-12 w:col-6 cursor-pointer">
                    <h4 className="mt-0">
                        <span>Selected Input Definition</span>
                    </h4>
                    <div onClick={onDefinitionClick}>
                        {!definition ? (
                            <Skeleton
                                className="flex align-items-center justify-content-center p-4"
                                height="120px"
                            >
                                <span className="text-sm text-center">
                                    Click to <b>select</b> or <b>create</b> an input definition
                                </span>
                            </Skeleton>
                        ) : (
                            <InputDefinitionItem
                                definition={definition}
                                versions={versions}
                                onVersionClick={onVersionClick}
                                onVersionCreateClick={onVersionCreateClick}
                                onClick={onDefinitionClick}
                                onDeleteClick={onDeleteDefinitionClick}
                                selected
                            />
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
