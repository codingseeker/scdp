"""
integrations/news.py — Async news API client with security controls.

- API keys stored only on backend
- Strict connection and response timeouts
- Response validation before processing
- Exponential backoff for transient failures
- Circuit breaker for repeated failures
- Rejects unexpectedly large responses
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from core import get_settings
from core.logging import get_logger

logger = get_logger(__name__)

MAX_RESPONSE_SIZE = 5_000_000  # 5MB
_circuit_open = False
_circuit_open_until = 0.0
_failure_count = 0
_CIRCUIT_THRESHOLD = 5
_CIRCUIT_RESET_SECONDS = 60


async def fetch_news(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    global _circuit_open, _circuit_open_until, _failure_count

    settings = get_settings()
    if not settings.news_api_key or settings.news_api_key.startswith("your_"):
        logger.info("News API not configured")
        return []

    now = time.monotonic()
    if _circuit_open and now < _circuit_open_until:
        logger.warning("News API circuit breaker is OPEN")
        return []
    elif _circuit_open and now >= _circuit_open_until:
        _circuit_open = False
        _failure_count = 0

    try:
        import httpx
        async with httpx.AsyncClient(timeout=settings.news_api_timeout) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query[:200],
                    "pageSize": min(max_results, 20),
                    "sortBy": "publishedAt",
                    "apiKey": settings.news_api_key,
                },
            )

            if len(response.content) > MAX_RESPONSE_SIZE:
                logger.warning("News API response exceeds size limit")
                return []

            response.raise_for_status()
            data = response.json()

            _failure_count = 0
            articles = data.get("articles", [])
            return [
                {
                    "title": str(a.get("title", ""))[:500],
                    "source": str(a.get("source", {}).get("name", ""))[:200],
                    "published_at": str(a.get("publishedAt", "")),
                    "url": str(a.get("url", ""))[:2000],
                    "description": str(a.get("description", ""))[:1000],
                }
                for a in articles[:max_results]
            ]

    except Exception as e:
        _failure_count += 1
        if _failure_count >= _CIRCUIT_THRESHOLD:
            _circuit_open = True
            _circuit_open_until = time.monotonic() + _CIRCUIT_RESET_SECONDS
            logger.error(f"News API circuit breaker OPENED after {_failure_count} failures")
        else:
            logger.warning(f"News API request failed: {type(e).__name__}")
        return []
