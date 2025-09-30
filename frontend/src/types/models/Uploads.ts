export interface FileUploadResponse {
    fileId: number;
    fileName: string;
    uploadStatus: string;
    message?: string;
}

export interface BulkFileUploadResponse {
    successfulUploads: FileUploadResponse[];
    failedUploads: FileUploadResponse[];
}
