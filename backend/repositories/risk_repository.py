"""
repositories/risk_repository.py — Risk data access.

Risk breakdowns are intelligence-derived data; in demo mode they come from
the bundled dataset (database/mock_data.py).
"""
from __future__ import annotations

from typing import Dict

from database.mock_data import RISK_BREAKDOWN


def get_risk_breakdown(supplier_id: str) -> Dict:
    return RISK_BREAKDOWN.get(supplier_id, {})