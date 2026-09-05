"""
ai/validators.py — Validate Gemini responses against Pydantic schemas.

- Every response is validated before processing
- Malformed responses trigger fallback behavior
- Never executes commands from AI output
- Never allows AI to modify database directly
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from core.logging import get_logger

logger = get_logger(__name__)


class ThreatAnalysisResponse(BaseModel):
    risk_level: str = Field(..., pattern=r"^(LOW|MEDIUM|HIGH|CRITICAL)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    impact_summary: str = Field(..., max_length=2000)
    affected_areas: List[str] = Field(..., max_length=20)
    recommended_actions: List[str] = Field(..., max_length=10)
    time_sensitivity: str = Field(..., pattern=r"^(IMMEDIATE|DAYS|WEEKS|MONTHS)$")


class MitigationStrategyItem(BaseModel):
    name: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    priority: str = Field(..., pattern=r"^(HIGH|MEDIUM|LOW)$")
    estimated_cost_impact: str = Field(..., max_length=200)
    implementation_time: str = Field(..., max_length=200)


class MitigationResponse(BaseModel):
    strategies: List[MitigationStrategyItem] = Field(..., max_length=10)
    executive_summary: str = Field(..., max_length=3000)


def validate_ai_response(raw_text: str, schema_class: type[BaseModel]) -> Optional[BaseModel]:
    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        if isinstance(data, str):
            logger.warning("AI response was double-encoded string")
            return None

        if _contains_dangerous_content(data):
            logger.warning("AI response contains potentially dangerous content")
            return None

        return schema_class(**data)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        logger.warning(f"AI response validation failed: {type(e).__name__}: {e}")
        return None


def _contains_dangerous_content(data: Any) -> bool:
    dangerous = [
        "os.system", "subprocess", "exec(", "eval(",
        "import ", "__import__", "MATCH ", "CREATE ",
        "DELETE ", "DROP ", "curl ", "wget ",
        "<script", "javascript:",
    ]

    def check(obj: Any) -> bool:
        if isinstance(obj, str):
            return any(d in obj for d in dangerous)
        if isinstance(obj, dict):
            return any(check(v) for v in obj.values())
        if isinstance(obj, list):
            return any(check(v) for v in obj)
        return False

    return check(data)
