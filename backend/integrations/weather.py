"""
integrations/weather.py — Async weather API client with security controls.

Same security patterns as news.py:
- Backend-only API keys
- Timeouts, size limits, circuit breaker
- Response validation
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from core import get_settings
from core.logging import get_logger

logger = get_logger(__name__)

MAX_RESPONSE_SIZE = 5_000_000
_circuit_open = False
_circuit_open_until = 0.0
_failure_count = 0
_CIRCUIT_THRESHOLD = 5
_CIRCUIT_RESET_SECONDS = 60


async def fetch_weather_alerts(lat: float, lng: float) -> List[Dict[str, Any]]:
    global _circuit_open, _circuit_open_until, _failure_count

    settings = get_settings()
    if not settings.weather_api_key or settings.weather_api_key.startswith("your_"):
        logger.info("Weather API not configured")
        return []

    now = time.monotonic()
    if _circuit_open and now < _circuit_open_until:
        logger.warning("Weather API circuit breaker is OPEN")
        return []
    elif _circuit_open and now >= _circuit_open_until:
        _circuit_open = False
        _failure_count = 0

    try:
        import httpx
        async with httpx.AsyncClient(timeout=settings.weather_api_timeout) as client:
            response = await client.get(
                "https://api.openweathermap.org/data/3.0/onecall",
                params={
                    "lat": lat,
                    "lon": lng,
                    "exclude": "minutely,hourly,daily",
                    "appid": settings.weather_api_key,
                },
            )

            if len(response.content) > MAX_RESPONSE_SIZE:
                logger.warning("Weather API response exceeds size limit")
                return []

            response.raise_for_status()
            data = response.json()

            _failure_count = 0
            alerts = data.get("alerts", [])
            return [
                {
                    "event": str(a.get("event", ""))[:200],
                    "sender_name": str(a.get("sender_name", ""))[:200],
                    "start": a.get("start"),
                    "end": a.get("end"),
                    "description": str(a.get("description", ""))[:1000],
                }
                for a in alerts[:10]
            ]

    except Exception as e:
        _failure_count += 1
        if _failure_count >= _CIRCUIT_THRESHOLD:
            _circuit_open = True
            _circuit_open_until = time.monotonic() + _CIRCUIT_RESET_SECONDS
            logger.error(f"Weather API circuit breaker OPENED after {_failure_count} failures")
        else:
            logger.warning(f"Weather API request failed: {type(e).__name__}")
        return []
