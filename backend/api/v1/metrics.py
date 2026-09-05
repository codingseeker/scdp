"""
api/v1/metrics.py — Metrics API endpoints.

Exposes operational metrics compatible with Prometheus scraping.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from ai.gemini_client import get_usage_stats
from core.logging import get_logger
from core.security import get_optional_user
from repositories.supplier_repository import get_all_suppliers
from schemas.common import MetricsResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=MetricsResponse)
async def get_metrics(user=Depends(get_optional_user)):
    suppliers = get_all_suppliers()
    avg_risk = sum(s.risk_score for s in suppliers) / len(suppliers) if suppliers else 0
    high_risk = sum(1 for s in suppliers if s.risk_score >= 60)
    critical = sum(1 for s in suppliers if s.risk_score >= 80)
    active_threats = sum(s.active_threats for s in suppliers)
    health_score = round(100 - avg_risk, 1)

    if health_score < 40:
        trend = "degrading"
    elif health_score < 65:
        trend = "stable"
    else:
        trend = "improving"

    return MetricsResponse(
        network_health_score=health_score,
        active_threats=active_threats,
        high_risk_suppliers=high_risk,
        critical_suppliers=critical,
        average_risk_score=round(avg_risk, 1),
        disruption_probability_30d=round(min(avg_risk / 100 * 1.5, 1.0), 2),
        last_updated=datetime.now(timezone.utc).isoformat(),
        trend=trend,
    )


@router.get("/prometheus", response_class=PlainTextResponse)
async def prometheus_metrics():
    suppliers = get_all_suppliers()
    avg_risk = sum(s.risk_score for s in suppliers) / len(suppliers) if suppliers else 0
    high_risk = sum(1 for s in suppliers if s.risk_score >= 60)
    ai_stats = get_usage_stats()

    lines = [
        "# HELP scdp_network_health Network health score",
        "# TYPE scdp_network_health gauge",
        f"scdp_network_health {round(100 - avg_risk, 1)}",
        "",
        "# HELP scdp_high_risk_suppliers Number of high risk suppliers",
        "# TYPE scdp_high_risk_suppliers gauge",
        f"scdp_high_risk_suppliers {high_risk}",
        "",
        "# HELP scdp_total_suppliers Total suppliers in network",
        "# TYPE scdp_total_suppliers gauge",
        f"scdp_total_suppliers {len(suppliers)}",
        "",
        "# HELP scdp_gemini_requests_total Total Gemini API requests",
        "# TYPE scdp_gemini_requests_total counter",
        f"scdp_gemini_requests_total {ai_stats['total_requests']}",
        "",
        "# HELP scdp_gemini_failures_total Total Gemini API failures",
        "# TYPE scdp_gemini_failures_total counter",
        f"scdp_gemini_failures_total {ai_stats['failed_requests']}",
        "",
        "# HELP scdp_gemini_tokens_total Total Gemini tokens used",
        "# TYPE scdp_gemini_tokens_total counter",
        f"scdp_gemini_tokens_total {ai_stats['total_tokens']}",
        "",
    ]
    return "\n".join(lines)
