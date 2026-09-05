"""
schemas/supplier.py — Supplier-related Pydantic schemas with strict validation.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupplierNode(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    country: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    tier: int = Field(..., ge=1, le=5)
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevel
    revenue_dependency: float = Field(..., ge=0.0, le=100.0)
    lead_time_days: int = Field(..., ge=0)
    alternatives_count: int = Field(..., ge=0)
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    active_threats: int = Field(default=0, ge=0)
    criticality: float = Field(default=50.0, ge=0.0, le=100.0)


class SupplierEdge(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    source: str = Field(..., min_length=1, max_length=50)
    target: str = Field(..., min_length=1, max_length=50)
    relationship: str = Field(..., pattern=r"^(SUPPLIES|LOGISTICS|ALTERNATIVE)$")
    volume_usd: float = Field(..., ge=0.0)
    lead_time_days: int = Field(..., ge=0)
    reliability: float = Field(..., ge=0.0, le=1.0)


class NetworkGraph(BaseModel):
    nodes: List[SupplierNode]
    edges: List[SupplierEdge]


class SupplierListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[SupplierNode]


class NewsItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    source: str = Field(..., min_length=1, max_length=200)
    published_at: str
    sentiment: str = Field(..., pattern=r"^(positive|neutral|negative)$")
    risk_relevance: float = Field(..., ge=0.0, le=1.0)
    url: str = Field(..., max_length=2000)


class WeatherAlert(BaseModel):
    location: str = Field(..., min_length=1, max_length=200)
    event_type: str = Field(..., min_length=1, max_length=100)
    severity: str
    affected_suppliers: List[str]
    eta_hours: int = Field(..., ge=0)


class SupplierDetail(BaseModel):
    supplier: SupplierNode
    news: List[NewsItem]
    weather_alerts: List[WeatherAlert]
    upstream_suppliers: List[str]
    downstream_customers: List[str]
    risk_breakdown: dict
