"""
api/v1/audit.py — Audit log management endpoints.
Requires Admin role.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from core.audit import get_audit_logs
from core.security import UserInfo, UserRole, require_role

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("")
async def list_audit_logs(
    actor: Optional[str] = Query(None, description="Filter by actor username"),
    action: Optional[str] = Query(None, description="Filter by action (e.g. login, simulation)"),
    resource: Optional[str] = Query(None, description="Filter by resource"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: UserInfo = Depends(require_role(UserRole.ADMIN)),
):
    return get_audit_logs(
        actor=actor,
        action=action,
        resource=resource,
        page=page,
        page_size=page_size,
    )
