"""
tests/unit/test_supplier_scoring.py — Unit tests for supplier scoring.
"""
import pytest

from graph.supplier_scoring import (
    calculate_criticality_score,
    detect_critical_path_suppliers,
    detect_geographic_concentration,
    detect_single_source_failures,
)
from schemas.supplier import SupplierEdge, SupplierNode, RiskLevel


def _make_supplier(sid, alternatives=2, country="USA", tier=1, criticality=50.0, revenue_dep=10.0):
    return SupplierNode(
        id=sid, name=f"Supplier {sid}", country=country, city="Test",
        category="Test", tier=tier, risk_score=50.0, risk_level=RiskLevel.MEDIUM,
        revenue_dependency=revenue_dep, lead_time_days=30, alternatives_count=alternatives,
        lat=0.0, lng=0.0, criticality=criticality,
    )


def _make_edge(eid, source, target, rel="SUPPLIES"):
    return SupplierEdge(
        id=eid, source=source, target=target, relationship=rel,
        volume_usd=1000000, lead_time_days=10, reliability=0.8,
    )


class TestSingleSourceFailures:
    def test_detects_single_source(self):
        suppliers = [_make_supplier("a", alternatives=0), _make_supplier("b")]
        edges = [_make_edge("e1", "b", "a")]
        result = detect_single_source_failures(suppliers, edges)
        assert "a" in result

    def test_no_single_source(self):
        suppliers = [_make_supplier("a", alternatives=3)]
        edges = [_make_edge("e1", "b", "a"), _make_edge("e2", "c", "a")]
        result = detect_single_source_failures(suppliers, edges)
        assert "a" not in result


class TestCriticalPathDetection:
    def test_detects_critical_path(self):
        suppliers = [_make_supplier("a", alternatives=0), _make_supplier("b"), _make_supplier("c")]
        edges = [_make_edge("e1", "a", "b"), _make_edge("e2", "a", "c")]
        result = detect_critical_path_suppliers(suppliers, edges)
        assert "a" in result


class TestGeographicConcentration:
    def test_detects_concentration(self):
        suppliers = [
            _make_supplier("a", country="China"),
            _make_supplier("b", country="China"),
            _make_supplier("c", country="USA"),
        ]
        result = detect_geographic_concentration(suppliers)
        assert "China" in result
        assert "USA" not in result
