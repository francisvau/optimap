import { JSX, useEffect, useRef, useState } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import { darkTheme, registerJSONataLanguage } from './monacoJsonataConfig';
import * as monacoEditor from 'monaco-editor';
import { Button } from 'primereact/button';
import { PrimeIcons } from 'primereact/api';
import { SaveMappingButton } from '@/components/shared/SaveMappingButton.tsx';
import { GenerateRulesButton } from '@/components/shared/GenerateRulesButton.tsx';
import { JSONSchema } from '@/types/Schema';

export interface JSONataEditorProps {
    inputSchema?: JSONSchema | null;
    mapping?: string | null;
    disableSave?: boolean;
    loadingSave?: boolean;
    saveSuccess?: boolean;
    generatingSuccess?: boolean;
    disableGenerate?: boolean;
    loadingGenerate?: boolean;
    readOnly?: boolean;
    onChange?: (value: string | undefined) => void;
    onSave?: (value: string) => void;
    onGenerate?: () => Promise<unknown>;
}

/**
 * Props for the JSONataEditor component.
 *
 * @param {JSONataEditorProps} root0 - The props object.
 *
 * @returns {JSX.Element} The rendered JSONataEditor component.
 */
export function JSONataEditor({
    inputSchema,
    mapping,
    onChange,
    disableSave,
    loadingSave,
    onSave,
    saveSuccess,
    disableGenerate,
    loadingGenerate,
    onGenerate,
    generatingSuccess,
    readOnly,
}: JSONataEditorProps): JSX.Element {
    const editorRef = useRef<monacoEditor.editor.IStandaloneCodeEditor | null>(null);
    const monacoRef = useRef<typeof monacoEditor | null>(null);
    const containerRef = useRef<HTMLDivElement | null>(null);
    const [isFullscreen, setIsFullscreen] = useState(false);

    const disableSaveRef = useRef(disableSave);

    useEffect(() => {
        disableSaveRef.current = disableSave;
    }, [disableSave]);

    const handleEditorDidMount: OnMount = (
        editor: monacoEditor.editor.IStandaloneCodeEditor,
        monaco: typeof monacoEditor,
    ): void => {
        editorRef.current = editor;
        monacoRef.current = monaco;

        registerJSONataLanguage(monaco, inputSchema);
        monaco.editor.defineTheme('jsonata-dark', darkTheme);
        monaco.editor.setTheme('jsonata-dark');

        editor.addAction({
            id: 'format-doc',
            label: 'Format Document',
            keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF],
            run: () => {
                editor.getAction('editor.action.formatDocument')?.run();
            },
        });

        editor.addAction({
            id: 'save-mapping',
            label: 'Save Mapping',
            keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS],
            run: () => {
                if (!disableSaveRef.current) {
                    const currentValue = editor.getValue();
                    onSave?.(currentValue);
                }
            },
        });
    };

    const goFullscreen = async () => {
        await containerRef.current?.requestFullscreen();
        setIsFullscreen(true);
        editorRef.current?.layout();
    };

    // resize the editor when the container is resized
    // useful when the container is e.g. a splitter component
    useEffect(() => {
        if (!containerRef.current) return;

        const ro = new ResizeObserver(() => {
            editorRef.current?.layout();
        });

        ro.observe(containerRef.current);

        return () => {
            ro.disconnect();
        };
    }, []);

    // update the layout when the editor is set to fullscreen
    useEffect(() => {
        const onFs = () => {
            if (!document.fullscreenElement) {
                setIsFullscreen(false);
                editorRef.current?.layout();
            }
        };

        document.addEventListener('fullscreenchange', onFs);

        return () => document.removeEventListener('fullscreenchange', onFs);
    }, []);

    return (
        <div ref={containerRef} className="relative w-full h-full">
            {!isFullscreen && !readOnly && (
                <Button
                    label="Fullscreen"
                    icon={PrimeIcons.EXTERNAL_LINK}
                    size="small"
                    severity={'contrast'}
                    style={{
                        position: 'absolute',
                        top: 8,
                        right: 6,
                        zIndex: 2,
                    }}
                    onClick={goFullscreen}
                />
            )}
            {isFullscreen && !readOnly && (
                <>
                    <SaveMappingButton
                        disabled={disableSave}
                        loading={loadingSave}
                        onClick={() => {
                            onSave?.(mapping ?? '');
                        }}
                        success={saveSuccess}
                        style={{
                            position: 'absolute',
                            top: 25,
                            right: 10,
                            zIndex: 10,
                        }}
                    />
                    <GenerateRulesButton
                        disabled={disableGenerate}
                        loading={loadingGenerate}
                        onClick={onGenerate}
                        success={generatingSuccess}
                        style={{
                            position: 'absolute',
                            top: 25,
                            right: 70,
                            zIndex: 10,
                        }}
                    />
                </>
            )}
            <Editor
                language="jsonata"
                defaultLanguage="jsonata"
                value={mapping}
                onChange={onChange}
                onMount={handleEditorDidMount}
                options={{
                    readOnly: readOnly,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: readOnly ?? false,
                    fontSize: 15,
                    stickyScroll: {
                        enabled: false,
                    },
                    fontFamily: 'Consolas, "Courier New", monospace',
                    automaticLayout: true,
                    theme: 'jsonata-dark',
                    padding: {
                        top: 30,
                        bottom: 30,
                    },
                    renderLineHighlight: 'none',
                    scrollbar: {
                        vertical: 'hidden',
                        horizontal: 'hidden',
                    },
                }}
            />
        </div>
    );
}

export default JSONataEditor;
