from fastapi import status


class OptimapApiError(Exception):
    """Base exception class"""

    def __init__(self, message: str, status_code: int = 500, status: str | None = None):
        """
        Initialize a custom exception instance.

        Args:
            message (str): The error message describing the exception.
            status_code (int, optional): The HTTP status code associated with the exception. Defaults to 500.
            message_code (str, optional): A custom code representing the exception. Defaults to None.
        """
        self.message = message
        self.status_code = status_code
        self.status = status
        super().__init__(self.message)


class ValueError(OptimapApiError):
    """Exception raised when the input is invalid"""

    def __init__(self, message: str):
        super().__init__(message)


class DuplicateEntity(OptimapApiError):
    """Exception raised when a user is already registered"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)


class EntityNotPresent(OptimapApiError):
    """Exception raised when a user is not in the database with an email"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class Unauthorized(OptimapApiError):
    """Exception raised when a user is not authenticated"""

    def __init__(self, message: str, status: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(message, status)


class Forbidden(OptimapApiError):
    """Exception raised when a user is not authorized to perform an action"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class FileUploadFailed(OptimapApiError):
    """Exception raised when a file upload fails"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class BadRequest(OptimapApiError):
    """Exception raised when metadata is invalid"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ExpiredEntity(OptimapApiError):
    """Exception thrown when encrypted token is expired"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_410_GONE)


class EngineError(OptimapApiError):
    """Exception raised when the engine responds with an exception"""

    def __init__(
        self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(message, status_code, status="ENGINE_ERROR")


class InvalidConfiguration(Exception):
    """Exception raised when the configuration is invalid"""

    def __init__(self, message: str):
        super().__init__(message)
