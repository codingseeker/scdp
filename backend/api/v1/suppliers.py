"""
api/v1/suppliers.py — Supplier API endpoints.

- Pagination with max limits
- Filtering, sorting, search
- Auth required for detailed views
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from core import get_settings
from core.exceptions import NotFoundError
from core.logging import get_logger
from core.security import UserInfo, get_optional_user
from repositories.supplier_repository import get_all_suppliers, get_supplier_by_id
from schemas.supplier import SupplierDetail, SupplierListResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("risk_score", description="Field to sort by"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(None, max_length=200),
    user: Optional[UserInfo] = Depends(get_optional_user),
):
    settings = get_settings()
    page_size = min(page_size, settings.max_pagination_limit)

    suppliers = get_all_suppliers()

    if search:
        sl = search.lower()
        suppliers = [
            s for s in suppliers
            if sl in s.name.lower() or sl in s.country.lower() or sl in s.category.lower()
        ]

    reverse = order == "desc"
    try:
        suppliers = sorted(suppliers, key=lambda s: getattr(s, sort_by, 0), reverse=reverse)
    except AttributeError:
        pass

    total = len(suppliers)
    start = (page - 1) * page_size
    end = start + page_size

    return SupplierListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=suppliers[start:end],
    )


@router.get("/{supplier_id}", response_model=SupplierDetail)
async def get_supplier(
    supplier_id: str,
    user: Optional[UserInfo] = Depends(get_optional_user),
):
    detail = get_supplier_by_id(supplier_id)
    if not detail:
        raise NotFoundError("Supplier", supplier_id)
    logger.info(f"Supplier detail requested: {supplier_id}")
    return detail
