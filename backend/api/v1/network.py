"""
api/v1/network.py — Supply network graph API (Neo4j-backed, demo-data fallback).
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from core.logging import get_logger
from core.security import get_optional_user
from repositories.supplier_repository import get_all_edges, get_all_suppliers
from schemas.supplier import NetworkGraph

logger = get_logger(__name__)
router = APIRouter(prefix="/network", tags=["Network"])


@router.get("", response_model=NetworkGraph)
async def get_network_graph(
    tier: Optional[int] = Query(None, ge=1, le=3, description="Filter by supplier tier"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_risk: Optional[float] = Query(None, ge=0, le=100, description="Minimum risk score"),
    user=Depends(get_optional_user),
):
    nodes = get_all_suppliers()
    edges = get_all_edges()

    if tier is not None:
        nodes = [s for s in nodes if s.tier == tier]

    if category is not None:
        category_lower = category.lower()
        nodes = [s for s in nodes if s.category.lower() == category_lower]

    if min_risk is not None:
        nodes = [s for s in nodes if s.risk_score >= min_risk]

    allowed_ids = {s.id for s in nodes}
    edges = [e for e in edges if e.source in allowed_ids and e.target in allowed_ids]
    return NetworkGraph(nodes=nodes, edges=edges)