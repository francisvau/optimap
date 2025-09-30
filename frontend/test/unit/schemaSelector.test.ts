import { describe, expect, it, beforeEach } from 'vitest';
import { SchemaSelector } from '@/utils/schema/jsonSchemaSelector';
import { JSONSchema, SubSchemaSelection } from '@/types/Schema';

const flatSchema: JSONSchema = {
    type: 'object',
    properties: {
        userId: { type: 'string' },
        userName: { type: 'string' },
        userAddress: { type: 'string' },
        orders: {
            type: 'array',
            items: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    orderId: { type: 'string' },
                    item: { type: 'string' },
                    subtotal: { type: 'number' },
                },
                required: ['userId', 'orderId', 'item', 'subtotal'],
            },
        },
    },
    required: ['userId', 'userName', 'userAddress', 'orders'],
};

const nestedSchema: JSONSchema = {
    type: 'object',
    required: ['userId', 'userName', 'userEmail', 'orders'],
    properties: {
        userId: { type: 'string', description: 'The ID of the user.' },
        userName: { type: 'string', description: 'The name of the user.' },
        userEmail: { type: 'string', description: 'The email of the user.' },
        orders: {
            type: 'array',
            items: {
                type: 'object',
                properties: {
                    orderId: { type: 'string', description: 'The ID of the order.' },
                    orderDate: {
                        type: 'string',
                        format: 'date-time',
                        description: 'The date of the order.',
                    },
                    orderAmount: { type: 'number', description: 'The amount of the order.' },
                    items: {
                        type: 'array',
                        items: {
                            type: 'object',
                            properties: {
                                itemId: { type: 'string', description: 'The ID of the item.' },
                                itemName: { type: 'string', description: 'The name of the item.' },
                                itemPrice: {
                                    type: 'number',
                                    description: 'The price of the item.',
                                },
                            },
                            required: ['itemId', 'itemName', 'itemPrice'],
                        },
                    },
                },
                required: ['orderId', 'orderDate', 'orderAmount', 'items'],
            },
        },
    },
};

const propKeys = (s: JSONSchema) =>
    s.type === 'object' ? Object.keys(s.properties!) : Object.keys(s.items.properties!);

// ------------------ flat schema tests ------------------
describe('SchemaSelector - flat schema', () => {
    let sel: SchemaSelector;
    beforeEach(() => {
        sel = new SchemaSelector(flatSchema);
    });

    it('initial state: no selection', () => {
        expect(sel.sessionPaths).toEqual([]);
        expect(sel.getSelection()).toBeUndefined();
        expect(sel.isComplete()).toBe(false);
    });

    it('root selection prunes nested array prop', () => {
        sel.select('');
        const result = sel.getSelection()!;
        expect(result.jsonSchema.required).toEqual(['userId', 'userName', 'userAddress']);
    });

    it('incomplete after root only', () => {
        sel.select('');
        expect(sel.isComplete()).toBe(false);
    });

    it('root then array makes complete', () => {
        sel.select('');
        sel.select('orders');
        expect(sel.isComplete()).toBe(true);
    });

    it('complete selection returns nested props for orders', () => {
        sel.select('');
        sel.select('orders');
        const selObj = sel.getSelection()!.jsonSchema;
        expect(propKeys(selObj)).toEqual(['userId', 'userName', 'userAddress', 'orders']);
        const ordersSchema = selObj.properties!.orders;
        expect(propKeys(ordersSchema)).toEqual(['userId', 'orderId', 'item', 'subtotal']);
    });

    it('selecting array alone returns primitive children', () => {
        sel.select('orders');
        const arrSchema = sel.getSelection()!;
        expect(arrSchema.jsonSchema.type).toBe('array');
        expect(propKeys(arrSchema.jsonSchema)).toEqual(['userId', 'orderId', 'item', 'subtotal']);
    });

    it('duplicate selection does not break and returns full schema', () => {
        sel.select('');
        sel.select('orders');
        sel.select('orders');
        expect(sel.isComplete()).toBe(true);
        expect(sel.getSelection()!.jsonSchema).toEqual(flatSchema);
    });

    it('clear resets coverage', () => {
        sel.select('');
        sel.select('orders');
        expect(sel.isComplete()).toBe(true);
        sel.clear();
        expect(sel.isComplete()).toBe(false);
        expect(sel.getSelection()).toBeUndefined();
    });

    it('primitive path selection throws', () => {
        expect(() => sel.select('userId')).toThrow();
    });

    it('invalid nested path throws', () => {
        expect(() => sel.select('does.not.exist')).toThrow();
    });

    it('deselect on existing selection works', () => {
        sel.select('orders');
        expect(sel.sessionPaths).toContain('orders');
        sel.deselect('orders');
        expect(sel.sessionPaths).not.toContain('orders');
    });

    it('deselect invalid path throws', () => {
        expect(() => sel.deselect('orders')).toThrow();
    });

    it('toggle flips selection state', () => {
        sel.toggle('orders');
        expect(sel.sessionPaths).toContain('orders');
        sel.toggle('orders');
        expect(sel.sessionPaths).not.toContain('orders');
    });

    it('hasSelectedInSession and hasSelectedBefore behave correctly', () => {
        sel.select('orders');
        expect(sel.hasSelectedInSession('orders')).toBe(true);
        const init: SubSchemaSelection = {
            jsonSchema: flatSchema.properties.orders!,
            targetPath: 'orders',
        };
        const sel2 = new SchemaSelector(flatSchema, [init]);
        expect(sel2.hasSelectedBefore('orders')).toBe(true);
    });
});

describe('SchemaSelector - nested schema', () => {
    let sel: SchemaSelector;
    beforeEach(() => {
        sel = new SchemaSelector(nestedSchema);
    });

    it('root selection prunes deeper arrays', () => {
        sel.select('');
        const root = sel.getSelection()!;
        expect(root.jsonSchema.required).toEqual(['userId', 'userName', 'userEmail']);
    });

    it('select nested items without parent', () => {
        sel.select('orders.items');
        const arr = sel.getSelection()!;
        expect(arr.jsonSchema.type).toBe('array');
        expect(propKeys(arr.jsonSchema)).toEqual(['itemId', 'itemName', 'itemPrice']);
    });

    it('then selecting parent keeps correct structure', () => {
        sel.select('orders.items');
        sel.select('orders');
        const arr = sel.getSelection()!;
        expect(arr.jsonSchema.type).toBe('array');
        expect(propKeys(arr.jsonSchema)).toEqual(['orderId', 'orderDate', 'orderAmount', 'items']);
    });

    it('full depth then root yields complete object', () => {
        sel.select('orders.items');
        sel.select('orders');
        sel.select('');
        expect(sel.isComplete()).toBe(true);
        const full = sel.getSelection()!;
        expect(full.jsonSchema.type).toBe('object');
        expect(propKeys(full.jsonSchema)).toEqual(['userId', 'userName', 'userEmail', 'orders']);
    });

    it('nested duplicate selection no error', () => {
        sel.select('orders.items');
        sel.select('orders.items');
        expect(sel.sessionPaths.filter((p) => p === 'orders.items').length).toBe(1);
    });

    it('deselect nested works only if not common parent', () => {
        sel.select('orders.items');
        sel.select('orders');
        sel.deselect('orders');
        expect(sel.sessionPaths).not.toContain('orders');
        expect(sel.getSelection().targetPath).toEqual('orders.items');
        expect(sel.getSelection().jsonSchema.type).toBe('array');
    });

    it('toggle nested and parent', () => {
        sel.toggle('orders.items');
        expect(sel.sessionPaths).toContain('orders.items');
        sel.toggle('orders.items');
        expect(sel.sessionPaths).not.toContain('orders.items');
    });

    it('initial selection via constructor on nested', () => {
        const init: SubSchemaSelection = {
            jsonSchema: nestedSchema.properties.orders!,
            targetPath: 'orders',
        };
        const s2 = new SchemaSelector(nestedSchema, [], init);
        expect(s2.getSelection()).toEqual(init);
    });
});
