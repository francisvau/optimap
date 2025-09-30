import jsonata, { ExprNode } from 'jsonata';

// const input = {
//     users: [
//         {
//             active: true,
//             name: 'Alice Smith',
//             birthdate: '1985-04-12',
//             scores: [10, 20, 30],
//             address: { city: 'London', zip: '10001' },
//             tags: 'admin,user',
//         },
//         {
//             active: false,
//             name: 'Bob Jones',
//             birthdate: '1990-07-21',
//             scores: [5, 15],
//             address: { city: 'Paris', zip: '75001' },
//             tags: 'editor',
//         },
//     ],
//     metadata: {
//         generated: '2025-05-09T14:23:00Z',
//     },
// };

// const expected = {
//     activeUsers: [
//         {
//             firstName: 'Alice',
//             lastName: 'Smith',
//             birthDateFormatted: '12/04/1985',
//             averageScore: 20,
//             scoreCount: 3,
//             scoresScaled: [100, 200, 300],
//             statusLabel: 'Active',
//             cityUpper: 'LONDON',
//             zipNumeric: 10001,
//             tags: ['admin', 'user'],
//         },
//     ],
//     reportDate: '2025-05-09',
// };

// const jsonataExpression = `{
//     "activeUsers": $map(
//       $filter(users, function($u){ $u.active }),
//       function($u){
//         {
//           "firstName": $split($u.name, " ")[0],
//           "lastName":  $split($u.name, " ")[1],
//           "birthDateFormatted":
//             $fromMillis(
//               $toMillis($u.birthdate, "[Y0001]-[M01]-[D01]"),
//               "[D01]/[M01]/[Y0001]"
//             ),
//           "averageScore": $round($average($u.scores), 1),
//           "scoreCount":   $count($u.scores),
//           "scoresScaled": $map($u.scores, function($s){ $s * 10 }),
//           "statusLabel":  $u.active ? "Active" : "Inactive",
//           "cityUpper":    $uppercase($u.address.city),
//           "zipNumeric":   $number($u.address.zip),
//           "tags":         $split($u.tags, ",")
//         }
//       }
//     ),
//     "reportDate":
//       $fromMillis(
//         $toMillis(metadata.generated, "[Y0001]-[M01]-[D01]T[H01]:[m01]:[s01]Z"),
//         "[Y0001]-[M01]-[D01]"
//       )
// }`;

// const jsonataExpression2 = `{
//     "activeUsers": {
//         "firstName": "hellaur!"
//     }
// }`;

// const ast = deserialize(jsonataExpression);
// console.log(ast);
// const raw = serialize(ast);
// console.log(raw);

// console.log(jsonataExpression2, raw);

// const result1 = await jsonata(jsonataExpression2).evaluate(input);
// const result2 = await jsonata(raw).evaluate(input);

// console.log('Original:', input);
// console.log('Mapped:', result1, result2);

/**
 * Serializes a JSONata Abstract Syntax Tree (AST) node into its string representation.
 *
 * @param node - The JSONata AST node to serialize.
 *
 * @returns The string representation of the given JSONata AST node.
 *
 * @throws {Error} If the node type is unsupported.
 *
 * Supported node types:
 * - `number`: Serializes the numeric value.
 * - `string`: Serializes the string value.
 * - `variable`: Serializes a variable, prefixing it with `$`.
 * - `path`: Serializes a path expression (e.g., `a.b.c` or `a[0]`).
 * - `function`: Serializes a function call with its arguments (e.g., `func(arg1, arg2)`).
 * - `lambda`: Serializes a lambda function (e.g., `function($x, $y) { ... }`).
 * - `condition`: Serializes a conditional expression (e.g., `cond ? thenExpr : elseExpr`).
 * - `binary`: Serializes a binary operation (e.g., `left + right`).
 * - `unary`: Serializes unary expressions, including object literals (`{}`) and array literals (`[]`).
 */
export function serialize(node?: ExprNode | null): string {
    if (!node) return '';

    switch (node.type) {
        case 'number': {
            // numeric literal
            return JSON.stringify(node.value);
        }

        case 'string': {
            // string literal
            return JSON.stringify(node.value);
        }

        case 'value': {
            // null/true/false
            const v = node.value;
            if (v === null) return 'null';
            if (v === true) return 'true';
            if (v === false) return 'false';

            // If ever something else, fall back to JSON
            return JSON.stringify(v);
        }

        case 'variable': {
            // e.g. $u  or $count
            return '$' + node.value;
        }

        case 'name': {
            // unprefixed identifier (object key in path step)
            return node.value;
        }

        case 'function': {
            // procedure(args…)
            const args = (node.arguments || []).map(serialize).join(', ');
            return `${serialize(node.procedure)}(${args})`;
        }

        case 'binary': {
            // lhs OP rhs
            const expr = node as ExprNode & {
                lhs: ExprNode;
            };
            return `${serialize(expr.lhs)} ${node.value} ${serialize(node.rhs)}`;
        }

        case 'condition': {
            // cond ? then : else
            const cn = node as ExprNode & {
                condition: ExprNode;
                then: ExprNode;
                else: ExprNode;
            };
            return `${serialize(cn.condition)} ? ${serialize(cn.then)} : ${serialize(cn.else)}`;
        }

        case 'lambda': {
            // function( arg1, arg2 ) { body }
            const ln = node as ExprNode & { arguments?: ExprNode[]; body: ExprNode };
            const args = (ln.arguments || []).map((arg) => serialize(arg)).join(', ');
            return `function(${args}) { ${serialize(ln.body!)} }`;
        }

        case 'unary': {
            // object or array literal
            const un = node as ExprNode & {
                value: '{' | '[';
                lhs?: ExprNode[][];
                expressions?: ExprNode[];
            };

            if (un.value === '{' && Array.isArray(un.lhs)) {
                // object: lhs is [ [keyNode, valNode], … ]
                const props = un.lhs.map(([keyNode, valNode]) => {
                    return `${serialize(keyNode)}: ${serialize(valNode)}`;
                });
                return `{ ${props.join(', ')} }`;
            }

            if (un.value === '[') {
                // array: try 'expressions' first, then fallback to lhs
                const items = un.expressions || un.lhs?.map((pair) => pair[0]) || [];
                return `[${items.map(serialize).join(', ')}]`;
            }

            throw new Error(`Unhandled unary node value: ${un.value}`);
        }

        // case 'path': {
        //     // A path is just an ordered list of “steps” (identifiers, indexes, filters, etc).
        //     // For simple dotted names we can just join on “.”:
        //     const p = node as ExprNode & { steps: ExprNode[] };
        //     return p.steps.map(serialize).join('.');
        // }

        default: {
            throw new Error(`Unhandled node type: ${node.type}`);
        }
    }
}

/**
 * Deserializes a JSONata expression string into its abstract syntax tree (AST) representation.
 *
 * @param expr - The JSONata expression string to be deserialized.
 * @returns The root node of the abstract syntax tree (AST) representing the JSONata expression.
 */
export function deserialize(expr: string): ExprNode {
    return jsonata(expr).ast();
}
