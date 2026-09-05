"""
api/v1/mitigation.py — Mitigation API endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from core.logging import get_logger
from core.security import get_optional_user

logger = get_logger(__name__)
router = APIRouter(prefix="/mitigation", tags=["Mitigation"])


@router.get("/routes")
async def get_mitigation_routes(user=Depends(get_optional_user)):
    from repositories.supplier_repository import get_all_edges, get_all_suppliers
    from graph.risk_propagation import find_alternatives

    suppliers = get_all_suppliers()
    edges = get_all_edges()
    supplier_map = {s.id: s for s in suppliers}

    alternatives = find_alternatives(set(), edges, supplier_map)
    return {"routes": [a.model_dump() for a in alternatives]}


@router.get("/suppliers")
async def get_alternative_suppliers(user=Depends(get_optional_user)):
    from repositories.supplier_repository import get_all_suppliers
    suppliers = get_all_suppliers()
    alternatives = [s for s in suppliers if s.alternatives_count > 0]
    return {
        "suppliers": [s.model_dump() for s in alternatives],
        "total": len(alternatives),
    }
