"""
graph/supplier_scoring.py — Supplier criticality scoring.

Calculates:
- Supplier criticality based on dependency depth, alternatives, lead time, geographic concentration
- Single-source-of-failure detection
- Critical-path supplier detection
- Geographic concentration risk
"""
from __future__ import annotations

from typing import Dict, List, Set

from schemas.supplier import SupplierEdge, SupplierNode


def calculate_criticality_score(
    supplier: SupplierNode,
    edges: List[SupplierEdge],
    supplier_map: dict[str, SupplierNode],
) -> float:
    base_score = supplier.criticality

    dependency_factor = min(supplier.revenue_dependency / 100.0 * 30, 30)

    alternatives_factor = max(0, (5 - supplier.alternatives_count) * 5)

    lead_time_factor = min(supplier.lead_time_days / 150.0 * 15, 15)

    downstream_count = sum(1 for e in edges if e.source == supplier.id)
    downstream_factor = min(downstream_count * 5, 20)

    score = (
        base_score * 0.3
        + dependency_factor
        + alternatives_factor
        + lead_time_factor
        + downstream_factor
    )
    return round(min(score, 100.0), 1)


def detect_single_source_failures(
    suppliers: List[SupplierNode],
    edges: List[SupplierEdge],
) -> List[str]:
    single_source_ids: List[str] = []
    for supplier in suppliers:
        upstream = [e for e in edges if e.target == supplier.id and e.relationship == "SUPPLIES"]
        if len(upstream) == 1 and supplier.alternatives_count == 0:
            single_source_ids.append(supplier.id)
    return single_source_ids


def detect_critical_path_suppliers(
    suppliers: List[SupplierNode],
    edges: List[SupplierEdge],
) -> List[str]:
    critical = []
    for supplier in suppliers:
        downstream_count = sum(1 for e in edges if e.source == supplier.id)
        if downstream_count >= 2 and supplier.alternatives_count <= 1:
            critical.append(supplier.id)
    return critical


def detect_geographic_concentration(
    suppliers: List[SupplierNode],
) -> Dict[str, List[str]]:
    country_suppliers: Dict[str, List[str]] = {}
    for s in suppliers:
        country_suppliers.setdefault(s.country, []).append(s.id)

    concentrated = {
        country: ids
        for country, ids in country_suppliers.items()
        if len(ids) >= 2
    }
    return concentrated
