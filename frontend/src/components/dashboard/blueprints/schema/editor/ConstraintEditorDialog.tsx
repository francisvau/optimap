import { JSX, useEffect, useState } from 'react';
import { Dialog } from 'primereact/dialog';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';
import { TypeConstraintForm } from '@/components/dashboard/forms/TypeConstraintForm';
import { TypeTooltip } from '@/components/dashboard/blueprints/schema/editor/TypeTooltip';
import { SchemaBuilderActions } from '@/utils/schema/jsonSchemaBuilder';
import type { JSONSchema, SchemaProperty } from '@/types/Schema';
import { PrimeIcons } from 'primereact/api';

import './ConstraintEditorDialog.scss';

export type ConstraintEditorDialogProps = {
    property?: SchemaProperty;
    builder: SchemaBuilderActions;
    show?: boolean;
    onHide: () => void;
};

/**
 * A React component that renders a dialog for editing constraints on a schema property.
 *
 * @param {ConstraintEditorDialogProps} props - The props for the component.
 * @param {boolean} [props.show=false] - Determines whether the dialog is visible.
 * @param {Property} props.property - The schema property being edited.
 * @param {SchemaBuilder} props.builder - The schema builder instance used to update the property.
 * @param {() => void} props.onHide - Callback function triggered when the dialog is closed.
 * @param {(schema: Schema) => void} props.onSchemaUpdate - Callback function triggered when the schema is updated.
 *
 * @returns {JSX.Element} The rendered ConstraintEditorDialog component.
 */
export function ConstraintEditorDialog({
    show = false,
    property,
    builder,
    onHide,
}: ConstraintEditorDialogProps): JSX.Element {
    const [updatedProperty, setUpdatedProperty] = useState(property);

    useEffect(() => {
        setUpdatedProperty(property);
    }, [property]);

    const handleUpdateConstraints = (updatedSchema: JSONSchema) => {
        setUpdatedProperty({
            ...updatedProperty,
            schema: {
                ...updatedProperty.schema,
                ...updatedSchema,
            },
        });
    };

    const handleSave = () => {
        if (!property || !updatedProperty) return;
        builder.updateProperty(property, updatedProperty);
        onHide();
    };

    if (!property) return <></>;

    return (
        <Dialog
            className="schema-dialog"
            visible={show}
            onHide={onHide}
            draggable={false}
            header={
                <div className="flex gap-2 align-items-center">
                    <span>Constraints for</span>
                    <Tag
                        severity="contrast"
                        value={
                            <div className="flex align-items-center gap-1">
                                <TypeTooltip type={property.schema.type} />
                                <span>{property.path.join('.')}</span>
                            </div>
                        }
                    />
                </div>
            }
            footer={<Button icon={PrimeIcons.CHECK} label="Save" onClick={handleSave} outlined />}
        >
            <TypeConstraintForm
                constraints={updatedProperty.schema}
                onEditConstraints={handleUpdateConstraints}
            />
        </Dialog>
    );
}
