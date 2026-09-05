"""
core/exceptions.py — Centralized exception handling with consistent error responses.
Never exposes internal implementation details in error messages.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.logging import get_logger

logger = get_logger(__name__)


def _request_id(request: Request) -> Optional[str]:
    return (
        getattr(request.state, "request_id", None)
        or request.headers.get("X-Request-ID")
        or "unset"
    )


class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: Optional[str] = None


class AppException(Exception):
    def __init__(
        self,
        status_code: int = 500,
        error: str = "internal_error",
        detail: str = "An unexpected error occurred",
    ):
        self.status_code = status_code
        self.error = error
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource", identifier: str = ""):
        super().__init__(
            status_code=404,
            error="not_found",
            detail=f"{resource} not found" + (f": {identifier}" if identifier else ""),
        )


class ValidationError(AppException):
    def __init__(self, detail: str = "Invalid input"):
        super().__init__(status_code=422, error="validation_error", detail=detail)


class AuthenticationError(AppException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(status_code=401, error="authentication_error", detail=detail)


class AuthorizationError(AppException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, error="authorization_error", detail=detail)


class RateLimitError(AppException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, error="rate_limit_exceeded", detail=detail)


class ExternalServiceError(AppException):
    def __init__(self, service: str = "external service"):
        super().__init__(
            status_code=503,
            error="service_unavailable",
            detail=f"The {service} is temporarily unavailable",
        )


class DatabaseError(AppException):
    def __init__(self):
        super().__init__(
            status_code=503,
            error="database_error",
            detail="Database operation failed",
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = _request_id(request)
        errors = exc.errors()
        detail = errors[0]["msg"] if errors else "Invalid request"
        logger.warning(
            f"ValidationError: {detail}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="validation_error",
                detail=detail,
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = _request_id(request)
        logger.warning(
            f"AppException: {exc.error} - {exc.detail}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error,
                detail=exc.detail,
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id(request)
        logger.error(
            f"Unhandled exception: {type(exc).__name__}",
            exc_info=True,
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                detail="Internal server error",
                request_id=request_id,
            ).model_dump(),
        )
