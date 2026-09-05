"""
ai/gemini_client.py — Gemini API client with security controls.

- Request rate limiting and timeout enforcement
- Token and cost tracking
- Fallback handling for unavailable/invalid responses
- Model version metadata stored with predictions
- Never executes commands from Gemini output
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from core import get_settings
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GeminiUsageTracker:
    total_requests: int = 0
    total_tokens: int = 0
    failed_requests: int = 0
    invalid_responses: int = 0
    total_cost_estimate: float = 0.0
    last_request_time: float = 0.0
    requests_this_minute: int = 0
    minute_window_start: float = 0.0


_usage = GeminiUsageTracker()


def get_usage_stats() -> Dict[str, Any]:
    return {
        "total_requests": _usage.total_requests,
        "total_tokens": _usage.total_tokens,
        "failed_requests": _usage.failed_requests,
        "invalid_responses": _usage.invalid_responses,
        "total_cost_estimate": round(_usage.total_cost_estimate, 4),
    }


def _check_rate_limit() -> bool:
    settings = get_settings()
    now = time.monotonic()

    if now - _usage.minute_window_start > 60:
        _usage.minute_window_start = now
        _usage.requests_this_minute = 0

    if _usage.requests_this_minute >= settings.gemini_rate_limit_rpm:
        logger.warning("Gemini rate limit reached")
        return False

    _usage.requests_this_minute += 1
    return True


async def call_gemini(
    system_instruction: str,
    user_prompt: str,
    max_output_tokens: Optional[int] = None,
) -> Optional[str]:
    settings = get_settings()

    if not settings.gemini_api_key or settings.gemini_api_key.startswith("your_"):
        logger.info("Gemini API key not configured — skipping AI enrichment")
        return None

    if not _check_rate_limit():
        _usage.failed_requests += 1
        return None

    _usage.total_requests += 1

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            settings.gemini_model,
            system_instruction=system_instruction,
        )

        response = model.generate_content(
            user_prompt,
            generation_config={
                "max_output_tokens": max_output_tokens or settings.gemini_max_tokens,
                "temperature": 0.3,
            },
            request_options={"timeout": settings.gemini_timeout},
        )

        if response and response.text:
            if hasattr(response, "usage_metadata"):
                tokens = getattr(response.usage_metadata, "total_token_count", 0)
                _usage.total_tokens += tokens
                _usage.total_cost_estimate += tokens * 0.000001

            return response.text

        _usage.invalid_responses += 1
        logger.warning("Gemini returned empty response")
        return None

    except Exception as e:
        _usage.failed_requests += 1
        logger.error(f"Gemini API call failed: {type(e).__name__}")
        return None


def get_model_version() -> str:
    settings = get_settings()
    return settings.gemini_model
