import { useRef, useState, useEffect } from 'react';
import { FileUpload } from 'primereact/fileupload';
import { Toast } from 'primereact/toast';

interface FileUploadProgress {
    [key: string]: number;
}

interface FileMetadata {
    filename: string;
    file_size: number;
    file_type: string;
}

interface ServerResponse {
    status: 'success' | 'error';
    message?: string;
}

interface ProcessedChunk {
    processedData: string[];
    remaining: string;
}

/**
 * Stream component for uploading files with WebSocket support.
 * This component allows users to upload multiple files
 * and tracks the upload progress for each file.
 * It uses WebSocket to send file data in chunks
 * and provides real-time feedback on the upload status.
 * @returns {JSX.Element} The Miauw component.
 */
export function Stream() {
    const toast = useRef<Toast>(null);
    const [uploadProgress, setUploadProgress] = useState<FileUploadProgress>({});
    const [isUploading, setIsUploading] = useState(false);
    const socketRef = useRef<WebSocket | null>(null);
    const filesQueueRef = useRef<File[]>([]);
    const currentFileIndexRef = useRef(0);
    const [allFilesUploaded, setAllFilesUploaded] = useState(false);

    const uploadFiles = async (files: File[]): Promise<void> => {
        if (!files.length) return;

        initializeUpload(files);
        setupWebSocket(files);
    };

    const initializeUpload = (files: File[]): void => {
        setIsUploading(true);
        setAllFilesUploaded(false);
        filesQueueRef.current = [...files];
        currentFileIndexRef.current = 0;
        setUploadProgress(Object.fromEntries(files.map((file) => [file.name, 0])));
    };

    const setupWebSocket = (files: File[]): void => {
        socketRef.current = new WebSocket('wss://optimap.local/api/upload_files_ws');
        const socket = socketRef.current;

        socket.onopen = () => startFileUpload(socket, files);
        socket.onmessage = handleServerResponse;
        socket.onerror = handleError;
        socket.onclose = handleClose;
    };

    const startFileUpload = (socket: WebSocket, files: File[]): void => {
        const fileMetadata: FileMetadata[] = files.map(({ name, size }) => ({
            filename: name,
            file_size: size,
            file_type: getFileExtension(name),
        }));

        socket.send(
            JSON.stringify({
                action: 'start_upload',
                files: fileMetadata,
            }),
        );
        processFile(socket, files[0]);
    };

    const processFile = async (socket: WebSocket, file: File): Promise<void> => {
        const CHUNK_SIZE = 10 * 1024 * 1024;
        let offset = 0;
        let remainingData = '';
        const fileType = getFileExtension(file.name);
        const fileReader = new FileReader();

        return new Promise<void>((resolve) => {
            fileReader.onload = async (e) => {
                try {
                    const content = remainingData + (e.target?.result as string);
                    const { processedData, remaining } = processContentChunk(content, fileType);
                    remainingData = remaining;

                    if (processedData.length) {
                        await sendEntitiesInBatches(socket, processedData, file.name, fileType);
                    }

                    offset += CHUNK_SIZE;
                    if (offset < file.size) {
                        readNextChunk();
                    } else {
                        await finalizeFileProcessing(socket, file.name, fileType, remainingData);
                        resolve();
                    }
                } catch (error) {
                    console.error('Error processing file:', error);
                    handleError();
                    resolve();
                }
            };

            const readNextChunk = () => {
                fileReader.readAsText(file.slice(offset, offset + CHUNK_SIZE));
            };
            readNextChunk();
        }).then(() => moveToNextFile(socket));
    };

    const finalizeFileProcessing = async (
        socket: WebSocket,
        filename: string,
        fileType: string,
        remainingData: string,
    ): Promise<void> => {
        if (remainingData.trim()) {
            const entities = parseEntities(remainingData, fileType);
            await sendEntitiesInBatches(socket, entities, filename, fileType);
        }
    };

    const moveToNextFile = (socket: WebSocket): void => {
        currentFileIndexRef.current++;
        if (currentFileIndexRef.current < filesQueueRef.current.length) {
            processFile(socket, filesQueueRef.current[currentFileIndexRef.current]);
        } else {
            socket.send(JSON.stringify({ action: 'upload_complete' }));
            setAllFilesUploaded(true);
        }
    };

    const parseEntities = (content: string, fileType: string): string[] => {
        if (fileType === 'csv') return content.split('\n').filter(Boolean);
        if (fileType === 'json') return [content];
        if (fileType === 'xml') return [content];
        throw new Error('Unsupported file type');
    };

    const processContentChunk = (content: string, fileType: string): ProcessedChunk => {
        if (fileType === 'csv') {
            const lines = content.split('\n');
            return { processedData: lines.slice(0, -1), remaining: lines.at(-1) || '' };
        } else if (fileType === 'json') {
            return {
                processedData: [content],
                remaining: '',
            };
        } else if (fileType === 'xml') {
            // Find last complete closing tag
            const lastCloseTagIndex = content.lastIndexOf('</');
            if (lastCloseTagIndex === -1) {
                return { processedData: [], remaining: content };
            }

            const endOfTagIndex = content.indexOf('>', lastCloseTagIndex);
            if (endOfTagIndex === -1) {
                return { processedData: [], remaining: content };
            }

            const splitIndex = endOfTagIndex + 1;
            const safeChunk = content.slice(0, splitIndex);
            const remaining = content.slice(splitIndex);

            return { processedData: [safeChunk], remaining };
        }

        throw new Error('Unsupported file type');
    };

    const sendEntitiesInBatches = async (
        socket: WebSocket,
        entities: string[],
        filename: string,
        fileType: string,
    ): Promise<void> => {
        const BATCH_SIZE = 10000;
        for (let i = 0; i < entities.length; i += BATCH_SIZE) {
            if (socket.readyState !== WebSocket.OPEN) throw new Error('WebSocket closed');

            const batch = entities.slice(i, i + BATCH_SIZE);

            socket.send(
                JSON.stringify({
                    action: 'send_entities',
                    entities: formatPayload(batch, fileType),
                    filename,
                    file_type: fileType,
                    batch_index: i / BATCH_SIZE,
                    total_batches: Math.ceil(entities.length / BATCH_SIZE),
                }),
            );

            setUploadProgress((prev) => ({
                ...prev,
                [filename]: Math.round(((i + BATCH_SIZE) / entities.length) * 100),
            }));
            await new Promise((res) => setTimeout(res, 20));
        }
    };

    const formatPayload = (batch: string[], fileType: string): string | string[] => {
        if (fileType === 'csv') return batch.join('\n');
        if (fileType === 'json') return batch;
        // if (fileType === 'xml') return batch;
        return batch[0];
    };

    const getFileExtension = (filename: string): string => {
        return filename.split('.').pop()?.toLowerCase() || '';
    };

    const handleServerResponse = (event: MessageEvent): void => {
        try {
            const response: ServerResponse = JSON.parse(event.data);
            if (response.status === 'success') {
                toast.current?.show({
                    severity: 'success',
                    summary: 'Upload Complete',
                    detail: `${filesQueueRef.current.length} files uploaded successfully!`,
                });
                socketRef.current?.close(1000, 'Upload complete');
            } else if (response.status === 'error') {
                toast.current?.show({
                    severity: 'error',
                    summary: 'Upload Failed',
                    detail: response.message || 'Unknown error',
                });
                socketRef.current?.close(1000, 'Upload failed');
            }
        } catch (error) {
            console.error('Error parsing server response:', error);
        }
    };

    const cancelUpload = (): void => {
        if (socketRef.current) {
            socketRef.current.close(1000, 'User cancelled');
        }
        setIsUploading(false);
        setUploadProgress({});
        toast.current?.show({
            severity: 'info',
            summary: 'Upload Cancelled',
            detail: 'Upload was cancelled.',
        });
    };

    const handleError = (): void => {
        toast.current?.show({
            severity: 'error',
            summary: 'Upload Failed',
            detail: 'WebSocket error occurred.',
        });
        setIsUploading(false);
    };

    const handleClose = (event: CloseEvent): void => {
        setIsUploading(false);
        if (event.code !== 1000) {
            toast.current?.show({
                severity: 'warn',
                summary: 'Upload Interrupted',
                detail: 'Upload was interrupted.',
            });
        }
    };

    const customUploader = (event: { files: File[] }): void => {
        const files = Array.from(event.files);
        const validTypes = ['.csv', '.json', '.xml'];
        const invalidFiles = files.filter((file) => {
            const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
            return !validTypes.includes(ext);
        });

        if (invalidFiles.length > 0) {
            toast.current?.show({
                severity: 'error',
                summary: 'Invalid Files',
                detail: 'Please upload only CSV, JSON, or XML files',
            });
            return;
        }

        uploadFiles(files);
    };

    const overallProgress =
        filesQueueRef.current.length > 0
            ? Math.round(
                  Object.values(uploadProgress).reduce((sum, progress) => sum + progress, 0) /
                      filesQueueRef.current.length,
              )
            : 0;

    useEffect(() => {
        return () => {
            if (socketRef.current) {
                socketRef.current.close(1000, 'Component unmounted');
            }
        };
    }, []);

    return (
        <div className="card flex flex-col items-center justify-center">
            <Toast ref={toast} />
            <FileUpload
                mode="advanced"
                name="files"
                accept=".csv,.json,.xml"
                multiple
                customUpload
                uploadHandler={customUploader}
                chooseLabel="Select Files"
                className="w-full"
                disabled={isUploading}
                maxFileSize={10000000000}
                emptyTemplate={<p className="m-0">Drag and drop files here to upload.</p>}
            />

            {isUploading && (
                <div className="mt-4 w-full max-w-md">
                    <div className="flex justify-between mb-2">
                        <span>
                            Uploading{' '}
                            {Math.min(
                                currentFileIndexRef.current + 1,
                                filesQueueRef.current.length,
                            )}
                            /{filesQueueRef.current.length} files...
                        </span>
                        {!allFilesUploaded && <span>{overallProgress}%</span>}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                            className="bg-blue-600 h-2.5 rounded-full"
                            style={{ width: `${overallProgress}%` }}
                        ></div>
                    </div>

                    <div className="mt-4 space-y-2">
                        {filesQueueRef.current.map((file, index) => (
                            <div
                                key={file.name}
                                className={`${index >= currentFileIndexRef.current ? 'opacity-100' : 'opacity-50'}`}
                            >
                                <div className="flex justify-between text-sm">
                                    <span className="truncate max-w-xs">{file.name}</span>
                                    <span>{uploadProgress[file.name] || 0}%</span>
                                </div>
                                <div className="w-full bg-gray-100 rounded-full h-1.5">
                                    <div
                                        className="bg-blue-400 h-1.5 rounded-full"
                                        style={{ width: `${uploadProgress[file.name] || 0}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <button
                        onClick={cancelUpload}
                        className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                        Cancel Upload
                    </button>
                </div>
            )}
        </div>
    );
}
