import { PrimeIcons } from 'primereact/api';

export type SupportedDataType = 'CSV' | 'SQL' | 'XML' | 'JSON';

export const supportedDataTypes: SupportedDataType[] = ['CSV', 'SQL', 'XML', 'JSON'];

export const dataTypeIcons: Record<SupportedDataType, string> = {
    CSV: PrimeIcons.FILE_EXCEL,
    SQL: PrimeIcons.DATABASE,
    XML: PrimeIcons.FILE,
    JSON: PrimeIcons.FILE,
};

export const exampleDataIcons: Record<SupportedDataType, string> = {
    CSV: PrimeIcons.FILE_EXCEL,
    SQL: PrimeIcons.DATABASE,
    XML: PrimeIcons.FILE,
    JSON: PrimeIcons.FILE,
};

/**
 * Downloads a JSON object as a file.
 *
 * This function converts the provided data into a JSON string, creates a Blob object,
 * and triggers a download in the browser with the specified filename.
 *
 * @param data - The data to be converted to JSON and downloaded.
 * @param filename - The name of the file to be downloaded. Defaults to 'data.json'.
 */
export function downloadJSON(data: unknown, filename = 'data.json'): void {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();

    URL.revokeObjectURL(url);
}

/**
 * Uploads and parses a JSON file, invoking the appropriate callback based on the result.
 *
 * @param file - The file to be uploaded and parsed. Must be a valid JSON file.
 * @param onSuccess - A callback function that is invoked with the parsed JSON data
 *                    if the file is successfully read and parsed.
 * @param onError - A callback function that is invoked with an error message
 *                  if the file cannot be read or contains invalid JSON.
 */
export async function uploadJSON(
    file: File,
    onSuccess: (data: unknown) => void,
    onError: (e?: SyntaxError) => void,
): Promise<void> {
    const reader = new FileReader();

    reader.onload = async (event) => {
        try {
            const data = await JSON.parse(event.target?.result as string);
            onSuccess(data);
        } catch (e) {
            onError(e);
        }
    };

    reader.onerror = () => {
        onError();
    };

    reader.readAsText(file);
}
