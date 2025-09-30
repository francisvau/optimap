import json
import os
import uuid
from typing import Any, Dict

import aiofiles
from lxml import etree

from app.config import UPLOAD_DIR
from app.service.upload.handlers.utils import StreamFileHandler


class XMLStreamFileHandler(StreamFileHandler):
    def __init__(self, filename: str, file_type: str = "xml"):
        super().__init__(file_type=file_type, filename=filename)

    async def create_file(self, extension: str = "xml") -> None:
        await super().create_file(extension=extension)

    async def write_data(self, data: list[str]) -> None:
        await super().write_data(data)

    async def finalize(self) -> None:
        # Parse the XML file to JSON
        await self.file_info.handle.close()
        xml_file_path = self.file_info.path
        json_result = self.parse_xml_to_json(xml_file_path)

        json_file_path = UPLOAD_DIR / f"{str(uuid.uuid4())}.json"

        async with aiofiles.open(json_file_path, "w", encoding="utf-8") as json_file:
            # Write the JSON object to the file
            await json_file.write(json.dumps(json_result, ensure_ascii=False, indent=4))

        self.file_info.path = str(json_file_path)

        # Delete the original XML file
        os.remove(xml_file_path)

    def parse_xml_to_json(self, file_path: str) -> Any:
        """
        Parse an XML file into a list of dictionaries (JSON-like).
        Supports nested XML structures, and if an element's children all
        have the same tag, returns a list of those children directly.
        """

        def element_to_dict(elem: etree._Element) -> Any:
            children = list(elem)
            # leaf node → text
            if not children:
                return elem.text.strip() if elem.text else ""

            tags = [child.tag for child in children]

            # flatten any element whose children all share the same tag
            if len(set(tags)) == 1:
                return [element_to_dict(child) for child in children]

            # otherwise build an object, merging repeated tags into lists
            result: Dict[str, Any] = {}
            for child in children:
                val = element_to_dict(child)
                if child.tag in result:
                    # already have one → turn into a list (or append)
                    if isinstance(result[child.tag], list):
                        result[child.tag].append(val)
                    else:
                        result[child.tag] = [result[child.tag], val]
                else:
                    result[child.tag] = val

            return result

        tree = etree.parse(file_path)
        root = tree.getroot()
        data = element_to_dict(root)

        # always return a list of dicts
        if isinstance(data, dict) or isinstance(data, str):
            return [data]

        return data
