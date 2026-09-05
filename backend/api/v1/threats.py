"""
api/v1/threats.py — Threat intelligence API.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from core.security import get_optional_user
from repositories.threat_repository import get_all_threats

router = APIRouter(prefix="/threats", tags=["Intelligence"])


@router.get("")
async def get_threats(
    min_risk_relevance: float = Query(0.6, ge=0.0, le=1.0),
    user=Depends(get_optional_user),
):
    threats = get_all_threats(min_risk_relevance=min_risk_relevance)
    return {"threats": threats, "total": len(threats)}