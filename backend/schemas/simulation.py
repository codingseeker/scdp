"""
schemas/simulation.py — Simulation request/response schemas with strict validation.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ScenarioRequest(BaseModel):
    description: str = Field(..., min_length=3, max_length=1000)
    affected_nodes: Optional[List[str]] = Field(default=None, max_length=20)
    severity: float = Field(default=0.7, ge=0.0, le=1.0)

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        dangerous_patterns = ["MATCH", "CREATE", "DELETE", "MERGE", "SET ", "REMOVE", "DROP"]
        upper = v.upper()
        for pattern in dangerous_patterns:
            if pattern in upper and any(c in v for c in "(){}[];"):
                raise ValueError("Description contains invalid characters")
        return v.strip()

    @field_validator("affected_nodes")
    @classmethod
    def validate_node_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            for node_id in v:
                if not node_id.isalnum() and not all(c.isalnum() or c in "_-" for c in node_id):
                    raise ValueError(f"Invalid node ID format: {node_id}")
        return v

    model_config = {"extra": "forbid"}


class AffectedSupplier(BaseModel):
    supplier_id: str
    supplier_name: str
    impact_score: float = Field(..., ge=0.0, le=100.0)
    time_to_impact_days: float = Field(..., ge=0.0)
    cascade_depth: int = Field(..., ge=0)
    primary_risk_factor: str


class AlternativeRoute(BaseModel):
    route_id: str
    description: str
    alternative_suppliers: List[str]
    cost_premium_pct: float
    lead_time_delta_days: int
    reliability_score: float = Field(..., ge=0.0, le=1.0)
    recommendation_strength: str


class SimulationResult(BaseModel):
    scenario_id: str
    scenario_description: str
    overall_network_impact: float = Field(..., ge=0.0, le=100.0)
    affected_suppliers: List[AffectedSupplier]
    cascade_path: List[str]
    time_to_impact_days: float
    alternative_routes: List[AlternativeRoute]
    executive_summary: str
    mitigation_actions: List[str]
    ai_enriched: bool = Field(default=False)
    ai_model_version: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
