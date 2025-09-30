import jsonataConfigFile from './jsonata-configuration.json';
import { editor, languages } from 'monaco-editor';
import { JSONSchema7 } from 'json-schema';
import CompletionItem = languages.CompletionItem;
import CompletionItemKind = languages.CompletionItemKind;
import { Monaco } from '@monaco-editor/react';
import { JSONSchema } from '@/types/Schema';
import { formatJsonataSync } from '@stedi/prettier-plugin-jsonata/dist/lib';

export const jsonataFunctions = [
    '$sum',
    '$count',
    '$max',
    '$min',
    '$average',
    '$string',
    '$number',
    '$boolean',
    '$exists',
    '$length',
    '$keys',
    '$lookup',
    '$append',
    '$error',
    '$distinct',
];

const keywords = ['and', 'or', 'not', 'true', 'false', 'null'];

export const registerJSONataLanguage = (monaco: Monaco, input?: JSONSchema | null) => {
    // Register the language if not already registered
    if (!monaco.languages.getLanguages().some((lang) => lang.id === 'jsonata')) {
        console.log('Registering JSONata language and formatting provider');
        monaco.languages.register({ id: 'jsonata' });

        // @ts-expect-error configuration typing mismatch
        monaco.languages.setLanguageConfiguration('jsonata', jsonataConfigFile);

        monaco.languages.registerDocumentFormattingEditProvider('jsonata', {
            provideDocumentFormattingEdits: async (model) => {
                const expression = model.getValue();
                const formatted = formatJsonataSync(expression);
                return [
                    {
                        range: model.getFullModelRange(),
                        text: formatted,
                    },
                ];
            },
        });

        monaco.languages.setMonarchTokensProvider('jsonata', {
            defaultToken: '',
            tokenPostfix: '.jsonata',

            keywords: ['and', 'or', 'in', 'not', 'as', 'to'],

            functions: jsonataFunctions,

            operators: [
                '+',
                '-',
                '*',
                '/',
                '%',
                '&',
                '|',
                '^',
                '~',
                '<',
                '>',
                '=',
                '!',
                '?',
                '??',
                'in',
                'as',
                'to',
            ],

            symbols: /[=><!~?:&|+\-*/^%]+/,
            escapes: /\\(?:["\\/bfnrt]|u[0-9A-Fa-f]{4})/,

            tokenizer: {
                root: [
                    // Comments (aligned with TextMate grammar)
                    [/\/\/.*$/, 'comment'],
                    [/\/\*/, 'comment', '@comment'],

                    // Strings (double-quoted)
                    [/"([^"\\]|\\.)*$/, 'string.invalid'],
                    [/"/, 'string.quote', '@string_double'],

                    // Numbers (same regex as TextMate)
                    [/-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/, 'number'],

                    // Keywords and functions
                    [
                        /\b(and|or|in|not|as|to)\b/,
                        { cases: { '@keywords': 'keyword', '@default': 'identifier' } },
                    ],
                    [
                        /\$([a-zA-Z_][\w$]*)\b/,
                        {
                            cases: {
                                '@functions': 'function',
                                '@default': 'variable',
                            },
                        },
                    ],

                    [/\$[a-zA-Z_][\w$]*/, 'variable'],

                    [
                        /[=><!~?:&|+\-*\\^%]+/,
                        { cases: { '@operators': 'operator', '@default': '' } },
                    ],

                    [/[{}()[\]]/, '@brackets'],
                    [/[,;.]/, 'delimiter'],

                    [/\s+/, 'white'],
                ],

                string_double: [
                    [/[^\\"]+/, 'string'],
                    [/@escapes/, 'string.escape'],
                    [/\\./, 'string.escape.invalid'],
                    [/"/, 'string.quote', '@pop'],
                ],

                comment: [
                    [/[^/*]+/, 'comment'],
                    [/\*\//, 'comment', '@pop'],
                    [/[/*]/, 'comment'],
                ],
            },
        });

        // Completion provider
        monaco.languages.registerCompletionItemProvider('jsonata', {
            triggerCharacters: ['$', ' '],
            provideCompletionItems: (model, position) => {
                const lineContent = model.getLineContent(position.lineNumber);
                const textUntilPosition = lineContent.substring(0, position.column - 1);
                const wordUntilPosition = model.getWordUntilPosition(position);
                const currentWord = wordUntilPosition.word;

                const suggestions: CompletionItem[] = [];

                if (/\$$/.test(textUntilPosition)) {
                    suggestions.push(
                        ...jsonataFunctions.map((f) => ({
                            label: `${f}`,
                            kind: monaco.languages.CompletionItemKind.Function,
                            documentation: `JSONata function: $${f}`,
                            insertText: `${f}()`,
                            range: new monaco.Range(
                                position.lineNumber,
                                position.column - 1,
                                position.lineNumber,
                                position.column,
                            ),
                        })),
                    );
                }

                if (currentWord.length > 0 || /\s$/.test(textUntilPosition)) {
                    suggestions.push(
                        ...keywords.map((keyword) => ({
                            label: keyword,
                            kind: monaco.languages.CompletionItemKind.Keyword,
                            documentation: `JSONata keyword: ${keyword}`,
                            insertText: keyword,
                            range: new monaco.Range(
                                position.lineNumber,
                                wordUntilPosition.startColumn,
                                position.lineNumber,
                                wordUntilPosition.endColumn,
                            ),
                        })),
                    );
                }

                const schemaPaths = getSchemaPaths(input);
                const schemaSuggestions = getSchemaSuggestionsFromPaths(schemaPaths).map(
                    (item) => ({
                        ...item,
                        range: new monaco.Range(
                            position.lineNumber,
                            wordUntilPosition.startColumn,
                            position.lineNumber,
                            wordUntilPosition.endColumn,
                        ),
                    }),
                );

                suggestions.push(...schemaSuggestions);

                return { suggestions };
            },
        });
    }
};

/**
 * Gets paths from JSON schema for auto-completion
 * @param schema JSONSchema to extract paths from
 * @param prefix Current path prefix
 * @returns Array of path strings
 */
function getSchemaPaths(schema?: JSONSchema7 | null, prefix: string = ''): string[] {
    if (!schema || typeof schema !== 'object') return [];

    if (schema.type === 'object' && schema.properties) {
        return Object.entries(schema.properties).flatMap(([key, propSchema]) =>
            getSchemaPaths(propSchema as JSONSchema7, prefix ? `${prefix}.${key}` : key),
        );
    }

    if (schema.type === 'array' && schema.items && typeof schema.items === 'object') {
        return getSchemaPaths(schema.items as JSONSchema7, `${prefix}[]`);
    }

    return [prefix];
}

/**
 * Creates completion suggestions from schema paths
 * @param paths Array of schema paths
 * @returns Array of CompletionItems
 */
function getSchemaSuggestionsFromPaths(paths: string[]): CompletionItem[] {
    return paths.map((path) => ({
        label: path,
        kind: CompletionItemKind.Property,
        documentation: `Path from JSON schema`,
        insertText: path,
        range: undefined, // set in provideCompletionItems
    }));
}

export const darkTheme: editor.IStandaloneThemeData = {
    base: 'vs-dark',
    inherit: true,
    rules: [
        { token: 'comment', foreground: '84848b' }, // grey
        { token: 'keyword', foreground: '569CD6', fontStyle: 'bold' }, // and, or not, as, to
        { token: 'function', foreground: '76acd5' }, // ← test with bright green
        { token: 'string', foreground: '3bb85c' },
        { token: 'number', foreground: '7b58ab', fontStyle: 'bold' },
        { token: 'operator', foreground: 'FF9D45', fontStyle: 'bold' }, // + - * / % & | ^ ~
        { token: 'variable', foreground: 'FF9EC8', fontStyle: 'italic' },
        { token: 'delimiter', foreground: '6e6e6e' }, // ; , , .
    ],
    colors: {
        'editor.background': '#060922',
    },
};
