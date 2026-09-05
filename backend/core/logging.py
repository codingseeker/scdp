"""
core/logging.py — Structured JSON logging configuration.
Never logs passwords, API keys, JWTs, cookies, or authorization headers.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


SENSITIVE_KEYS = frozenset({
    "password", "secret", "token", "api_key", "apikey",
    "authorization", "cookie", "jwt", "refresh_token",
    "access_token", "neo4j_password", "redis_password",
    "gemini_api_key", "news_api_key", "weather_api_key",
})


def _redact_sensitive(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS else _redact_sensitive(v)
            for k, v in data.items()
        }
    if isinstance(data, (list, tuple)):
        return [_redact_sensitive(item) for item in data]
    return data


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record, "extra_data"):
            log_entry["data"] = _redact_sensitive(record.extra_data)

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    root.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    *,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    extra = {
        "extra_data": _redact_sensitive({
            "security_event": event_type,
            "ip_address": ip_address,
            **(details or {}),
        })
    }
    if request_id:
        extra["request_id"] = request_id
    if user_id:
        extra["user_id"] = user_id

    logger.warning(message, extra=extra)
