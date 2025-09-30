import { describe, it, expect, beforeEach } from 'vitest';
import { SchemaBuilder } from '@/utils/schema/jsonSchemaBuilder';
import { JSONSchema, SchemaProperty } from '@/types/Schema';

/* helper */
const stringSchema: JSONSchema = { type: 'string' };
const numberSchema: JSONSchema = { type: 'number' };
const arrayOfStrings: JSONSchema = { type: 'array', items: { type: 'string' } };

describe('SchemaBuilder', () => {
    let base: JSONSchema;
    let builder: SchemaBuilder;

    beforeEach(() => {
        base = { type: 'object', properties: {}, required: [] };
        builder = new SchemaBuilder(base);
    });

    it('getSchema / setSchema round-trips', () => {
        expect(builder.getSchema()).toBe(base);
        const next: JSONSchema = { type: 'string' };
        const ret = builder.setSchema(next);
        expect(ret).toBe(builder);
        expect(builder.getSchema()).toBe(next);
    });

    it('addProperty adds root-level property and marks required', () => {
        builder.addProperty('name', stringSchema);
        const out = builder.getSchema();
        expect(out.properties?.name).toEqual(stringSchema);
        expect(out.required).toEqual(['name']);
    });

    it('addProperty supports deep paths & after-ordering', () => {
        builder
            .addProperty('address', { type: 'object', properties: {}, required: [] })
            .addProperty('address.street', stringSchema)
            .addProperty('address.number', numberSchema, 'address.street');
        const req = builder.getSchema().properties!.address.required;
        expect(req).toEqual(['street', 'number']);
    });

    it('addProperty with after-nonexistent appends to end', () => {
        builder.addProperty('a', stringSchema);
        builder.addProperty('b', stringSchema, 'nonexistent');
        expect(builder.getSchema().required).toEqual(['a', 'b']);
    });

    it('addProperty does not duplicate required entries', () => {
        builder.addProperty('x', numberSchema);
        builder.addProperty('x', numberSchema);
        expect(builder.getSchema().required).toEqual(['x']);
    });

    it('addProperty populates array.items when adding an array schema', () => {
        builder.addProperty('tags', arrayOfStrings);
        const tags = builder.getSchema().properties!.tags;
        expect(tags.type).toBe('array');
        expect(tags.items).toMatchObject({ type: 'string' });
    });

    it('addProperty allows nested inside array.items', () => {
        builder
            .addProperty('tags', {
                type: 'array',
                items: { type: 'object', properties: {}, required: [] },
            })
            .addProperty('tags.child', stringSchema);
        const child = (builder.getSchema().properties!.tags.items as JSONSchema).properties!.child;
        expect(child).toEqual(stringSchema);
    });

    it('hasSchemaProperty detects existing and non-existing paths', () => {
        builder.addProperty('title', stringSchema);
        expect(builder.hasSchemaProperty('title')).toBe(true);
        expect(builder.hasSchemaProperty('missing')).toBe(false);
    });

    it('hasSchemaProperty detects deep nested paths', () => {
        builder
            .addProperty('parent', { type: 'object', properties: {}, required: [] })
            .addProperty('parent.child', numberSchema);
        expect(builder.hasSchemaProperty('parent.child')).toBe(true);
    });

    it('updateProperty renames and mutates schema in-place', () => {
        builder.addProperty('age', numberSchema);
        const prop: SchemaProperty = { path: ['age'], key: 'age', schema: numberSchema };
        builder.updateProperty(prop, { key: 'years', schema: { minimum: 0 } });
        const out = builder.getSchema();
        expect(out.properties?.age).toBeUndefined();
        expect(out.properties?.years).toMatchObject({ type: 'number', minimum: 0 });
        expect(out.required).toContain('years');
    });

    it('updateProperty removes keys when newProperty.schema has undefined', () => {
        builder.addProperty('count', { type: 'number', minimum: 1, maximum: 10 });
        const prop: SchemaProperty = {
            path: ['count'],
            key: 'count',
            schema: { type: 'number', minimum: 1, maximum: 10 },
        };
        builder.updateProperty(prop, { schema: { maximum: undefined } });
        const out = builder.getSchema().properties!.count;
        expect(out.maximum).toBeUndefined();
        expect(out.minimum).toBe(1);
    });

    it('updateProperty without rename preserves type', () => {
        builder.addProperty('flag', { type: 'boolean' });
        const prop: SchemaProperty = { path: ['flag'], key: 'flag', schema: { type: 'boolean' } };
        builder.updateProperty(prop, { schema: { description: 'a flag' } });
        const out = builder.getSchema().properties!.flag;
        expect(out.type).toBe('boolean');
        expect(out.description).toBe('a flag');
    });

    it('updateProperty on missing property throws', () => {
        const prop: SchemaProperty = { path: ['nope'], key: 'nope', schema: {} };
        expect(() => builder.updateProperty(prop, {})).toThrow();
    });

    it('renameProperty convenience method works', () => {
        builder.addProperty('foo', stringSchema).renameProperty('foo', 'bar');
        const props = builder.getSchema().properties!;
        expect(props.bar).toBeDefined();
        expect(props.foo).toBeUndefined();
        expect(builder.getSchema().required).toContain('bar');
    });

    it('removeProperty deletes prop and required entry', () => {
        builder.addProperty('id', numberSchema);
        builder.removeProperty('id');
        const out = builder.getSchema();
        expect(out.properties?.id).toBeUndefined();
        expect(out.required).not.toContain('id');
    });

    it('removeProperty on non-existent path is no-op', () => {
        builder.addProperty('keep', stringSchema);
        expect(() => builder.removeProperty('nothing')).not.toThrow();
        expect(builder.getSchema().properties?.keep).toBeDefined();
    });

    it('multiple addProperty calls maintain required order', () => {
        builder.addProperty('one', stringSchema);
        builder.addProperty('two', numberSchema);
        builder.addProperty('three', stringSchema, 'one');
        expect(builder.getSchema().required).toEqual(['one', 'three', 'two']);
    });

    it('chainable interface returns same instance', () => {
        const chain = builder
            .addProperty('a', stringSchema)
            .updateProperty({ path: ['a'], key: 'a', schema: stringSchema }, {})
            .removeProperty('a');
        expect(chain).toBe(builder);
    });

    it('deeply nested add and remove works', () => {
        builder
            .addProperty('lvl1', { type: 'object', properties: {}, required: [] })
            .addProperty('lvl1.lvl2', { type: 'object', properties: {}, required: [] })
            .addProperty('lvl1.lvl2.lvl3', stringSchema);
        expect(builder.hasSchemaProperty('lvl1.lvl2.lvl3')).toBe(true);
        builder.removeProperty('lvl1.lvl2.lvl3');
        expect(builder.hasSchemaProperty('lvl1.lvl2.lvl3')).toBe(false);
    });

    it('setSchema replaces entire schema', () => {
        builder.addProperty('temp', stringSchema);
        builder.setSchema({ type: 'object', properties: {}, required: [] });
        expect(builder.hasSchemaProperty('temp')).toBe(false);
    });
});
