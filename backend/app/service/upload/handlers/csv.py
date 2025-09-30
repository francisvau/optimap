import csv
import json
from io import StringIO
from typing import Any, Dict, List, Tuple

from app.service.upload.handlers.utils import StreamFileHandler


class CSVStreamFileHandler(StreamFileHandler):
    """
    Handles CSV file streaming.
    """

    def __init__(self, filename: str, file_type: str = "csv"):
        super().__init__(file_type=file_type, filename=filename)
        self.csv_headers: list[str] = []

    async def create_file(self, extension: str = "json") -> None:
        await super().create_file()
        await self.file_info.handle.write("[")

    async def write_data(self, data: list[str]) -> None:
        if not self.csv_headers:
            self.csv_headers, chunk = self.extract_headers_and_data(data)
        else:
            _, chunk = self.extract_headers_and_data(data)

        if chunk.strip():
            json_entities = self.process_csv_chunk(self.csv_headers, chunk)

            for entity in json_entities:
                if self.file_info.count > 0:
                    await self.file_info.handle.write(",")

                # Write the JSON object to the file
                await self.file_info.handle.write(
                    json.dumps(entity, ensure_ascii=False)
                )

                self.file_info.count += 1

    async def finalize(self) -> None:
        await self.file_info.handle.write("]")
        await self.file_info.handle.close()

    def extract_headers_and_data(self, entities: Any) -> Tuple[List[str], str]:
        """
        Extract headers and data from CSV input.
        """
        if isinstance(entities, list):
            lines = entities
        else:
            lines = entities.split("\n")

        headers = []
        data_lines = []
        header_found = False

        for line in lines:
            if not line.strip():
                continue

            if not header_found:
                headers = next(csv.reader([line]))
                header_found = True
            else:
                data_lines.append(line)

        return headers, "\n".join(data_lines)

    def process_csv_chunk(self, headers: List[str], chunk: str) -> List[Dict[str, Any]]:
        """Process a chunk of CSV data into JSON objects"""
        json_data = []
        csv_file = StringIO(chunk)
        reader = csv.DictReader(csv_file, fieldnames=headers)

        for row in reader:
            clean_row = {
                k: v.strip() if isinstance(v, str) else v for k, v in row.items()
            }
            json_data.append(clean_row)

        return json_data
