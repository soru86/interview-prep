"""Global exception handlers registered on the FastAPI app."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception carrying an HTTP status code."""

    def __init__(self, status_code: int = 400, detail: str = "An error occurred"):
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedException(AppException):
    """Authentication failure (401)."""

    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail)


# ---------------------------------------------------------------------------
# Handler to register with ``app.add_exception_handler``
# ---------------------------------------------------------------------------

async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Convert an ``AppException`` into a JSON error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
