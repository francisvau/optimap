from app.service.upload.handlers.utils import StreamFileHandler


class JSONStreamFileHandler(StreamFileHandler):
    """
    Handles JSON file streaming.
    """

    def __init__(self, filename: str, file_type: str = "json"):
        super().__init__(file_type=file_type, filename=filename)
