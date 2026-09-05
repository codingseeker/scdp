"""
services/risk_service.py — Risk calculation business logic.
"""
from __future__ import annotations

from typing import Dict, List

from graph.supplier_scoring import (
    calculate_criticality_score,
    detect_critical_path_suppliers,
    detect_geographic_concentration,
    detect_single_source_failures,
)
from schemas.supplier import SupplierEdge, SupplierNode


def get_network_risk_summary(
    suppliers: List[SupplierNode],
    edges: List[SupplierEdge],
) -> Dict:
    supplier_map = {s.id: s for s in suppliers}

    single_source = detect_single_source_failures(suppliers, edges)
    critical_path = detect_critical_path_suppliers(suppliers, edges)
    geo_concentration = detect_geographic_concentration(suppliers)

    criticality_scores = {
        s.id: calculate_criticality_score(s, edges, supplier_map)
        for s in suppliers
    }

    return {
        "single_source_failures": single_source,
        "critical_path_suppliers": critical_path,
        "geographic_concentration": geo_concentration,
        "criticality_scores": criticality_scores,
    }
