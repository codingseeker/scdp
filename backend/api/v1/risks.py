"""
api/v1/risks.py — Risk API endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from core.logging import get_logger
from core.security import UserInfo, get_optional_user
from repositories.supplier_repository import get_all_edges, get_all_suppliers
from services.risk_service import get_network_risk_summary

logger = get_logger(__name__)
router = APIRouter(prefix="/risks", tags=["Risks"])


@router.get("")
async def get_risks(user=Depends(get_optional_user)):
    suppliers = get_all_suppliers()
    edges = get_all_edges()
    summary = get_network_risk_summary(suppliers, edges)
    return summary


@router.get("/{supplier_id}")
async def get_supplier_risk(supplier_id: str, user=Depends(get_optional_user)):
    from repositories.risk_repository import get_risk_breakdown
    breakdown = get_risk_breakdown(supplier_id)
    if not breakdown:
        from core.exceptions import NotFoundError
        raise NotFoundError("Supplier risk data", supplier_id)
    return {"supplier_id": supplier_id, "risk_breakdown": breakdown}
