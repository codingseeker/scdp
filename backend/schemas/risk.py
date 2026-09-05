"""
schemas/risk.py — Risk and threat-related schemas.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ThreatItem(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    title: str
    source: str
    severity: str = Field(..., pattern=r"^(LOW|MEDIUM|HIGH|CRITICAL)$")
    published_at: str
    risk_relevance: float = Field(..., ge=0.0, le=1.0)


class ThreatListResponse(BaseModel):
    threats: List[ThreatItem]
    total: int
