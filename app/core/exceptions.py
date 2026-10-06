"""Application Exception Handlers and Definitions."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class PdsException(Exception):
    """Base class for all application-level errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationFailedException(PdsException):
    """Exception raised when credential validation fails."""

    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class InvalidClientException(PdsException):
    """Exception raised when an invalid client_id requests authorization."""

    def __init__(self, message: str = "Client application not authorized"):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


async def pds_exception_handler(request: Request, exc: PdsException) -> JSONResponse:
    """Render structured JSON response for application-level errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "detail": exc.message},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fail closed. Conceal internal tracebacks to prevent information disclosure."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "detail": "An internal error occurred."},
    )
