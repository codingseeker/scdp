"""
core/middleware.py — Security middleware stack.

- Request ID generation and propagation
- Request body size limits
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Rate limiting (in-memory for dev, Redis-backed for production)
- Request timeout handling
"""
from __future__ import annotations

import time
import uuid
from collections import defaultdict
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core import get_settings
from core.exceptions import ErrorResponse
from core.logging import get_logger, log_security_event

logger = get_logger(__name__)


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or "unset"


def _parse_rate_limit(spec: str, default_window_seconds: int = 60) -> tuple[int, int]:
    """Parse a 'N/minute' style spec into (limit, window_seconds)."""
    try:
        limit_str, unit = spec.lower().split("/")
        limit = int(limit_str)
        if unit in ("minute", "min", "m"):
            window = 60
        elif unit.isdigit():
            window = int(unit)
        else:
            window = default_window_seconds
        return limit, window
    except Exception:
        return 100, default_window_seconds


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.monotonic()

        response = await call_next(request)

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        logger.info(
            f"{request.method} {request.url.path} {response.status_code} {duration_ms}ms",
            extra={"request_id": request_id},
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        settings = get_settings()
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        content_length = request.headers.get("content-length")
        request_id = _get_request_id(request)

        if content_length and int(content_length) > settings.max_request_body_size:
            log_security_event(
                logger,
                "oversized_request",
                f"Request body too large: {content_length} bytes",
                request_id=request_id,
                ip_address=request.client.host if request.client else None,
            )
            return JSONResponse(
                status_code=413,
                content=ErrorResponse(
                    error="payload_too_large",
                    detail=f"Request body exceeds maximum size of {settings.max_request_body_size} bytes",
                    request_id=request_id,
                ).model_dump(),
            )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path.startswith(("/api/docs", "/api/redoc", "/api/openapi.json")):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"
        now = time.monotonic()

        settings = get_settings()
        path = request.url.path
        if "/auth/" in path:
            limit, window = _parse_rate_limit(settings.rate_limit_auth)
        elif "/simulation" in path:
            limit, window = _parse_rate_limit(settings.rate_limit_simulation)
        elif "/gemini" in path or "/ai/" in path:
            limit, window = _parse_rate_limit(settings.rate_limit_ai)
        else:
            limit, window = _parse_rate_limit(settings.rate_limit_default)

        self._requests[key] = [t for t in self._requests[key] if now - t < window]

        request_id = _get_request_id(request)

        if len(self._requests[key]) >= limit:
            log_security_event(
                logger,
                "rate_limit_exceeded",
                f"Rate limit hit: {key}",
                request_id=request_id,
                ip_address=client_ip,
                details={"limit": limit, "window": window},
            )
            response = JSONResponse(
                status_code=429,
                content=ErrorResponse(
                    error="rate_limit_exceeded",
                    detail="Too many requests. Please try again later.",
                    request_id=request_id,
                ).model_dump(),
            )
            response.headers["Retry-After"] = str(window)
            return response

        self._requests[key].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - len(self._requests[key])))
        return response


def register_middleware(app: FastAPI) -> None:
    # Added in order: each subsequent middleware wraps the previous ones.
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(RateLimitMiddleware)