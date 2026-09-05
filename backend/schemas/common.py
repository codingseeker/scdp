"""
schemas/common.py — Common response schemas.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]


class ReadyResponse(BaseModel):
    status: str
    timestamp: str


class MetricsResponse(BaseModel):
    network_health_score: float
    active_threats: int
    high_risk_suppliers: int
    critical_suppliers: int
    average_risk_score: float
    disruption_probability_30d: float
    last_updated: str
    trend: str = Field(..., pattern=r"^(improving|stable|degrading)$")


class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    actor: str
    action: str
    resource: str
    resource_id: Optional[str] = None
    request_id: Optional[str] = None
    result: str
    details: Optional[Dict[str, Any]] = None
