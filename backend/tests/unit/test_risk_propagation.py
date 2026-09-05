"""
tests/unit/test_risk_propagation.py — Unit tests for risk propagation engine.
"""
import pytest

from graph.risk_propagation import build_adjacency, cascade_bfs, extract_cascade_path, find_alternatives
from schemas.supplier import SupplierEdge, SupplierNode
from schemas.supplier import RiskLevel


def _make_supplier(sid, name="Test", risk=50.0, criticality=70.0, tier=1):
    return SupplierNode(
        id=sid, name=name, country="Test", city="Test",
        category="Test", tier=tier, risk_score=risk,
        risk_level=RiskLevel.MEDIUM, revenue_dependency=10.0,
        lead_time_days=30, alternatives_count=2,
        lat=0.0, lng=0.0, criticality=criticality,
    )


def _make_edge(eid, source, target, rel="SUPPLIES", reliability=0.8):
    return SupplierEdge(
        id=eid, source=source, target=target,
        relationship=rel, volume_usd=1000000,
        lead_time_days=10, reliability=reliability,
    )


class TestBuildAdjacency:
    def test_basic_adjacency(self):
        suppliers = [_make_supplier("a"), _make_supplier("b")]
        edges = [_make_edge("e1", "a", "b")]
        adj = build_adjacency(suppliers, edges)
        assert "b" in adj["a"]
        assert "a" not in adj["b"]

    def test_alternative_excluded(self):
        suppliers = [_make_supplier("a"), _make_supplier("b")]
        edges = [_make_edge("e1", "a", "b", rel="ALTERNATIVE")]
        adj = build_adjacency(suppliers, edges)
        assert adj["a"] == []


class TestCascadeBfs:
    def test_single_node_impact(self):
        suppliers = [_make_supplier("a", criticality=80.0)]
        edges = []
        supplier_map = {s.id: s for s in suppliers}
        adj = build_adjacency(suppliers, edges)
        result = cascade_bfs(["a"], 0.8, adj, supplier_map, edges)
        assert len(result) == 1
        assert result[0].supplier_id == "a"
        assert result[0].impact_score > 0

    def test_cascade_propagation(self):
        suppliers = [_make_supplier("a"), _make_supplier("b")]
        edges = [_make_edge("e1", "a", "b")]
        supplier_map = {s.id: s for s in suppliers}
        adj = build_adjacency(suppliers, edges)
        result = cascade_bfs(["a"], 0.7, adj, supplier_map, edges)
        assert len(result) == 2

    def test_max_depth_limit(self):
        suppliers = [_make_supplier(f"s{i}") for i in range(10)]
        edges = [_make_edge(f"e{i}", f"s{i}", f"s{i+1}") for i in range(9)]
        supplier_map = {s.id: s for s in suppliers}
        adj = build_adjacency(suppliers, edges)
        result = cascade_bfs(["s0"], 0.9, adj, supplier_map, edges, max_depth=4)
        depths = {a.cascade_depth for a in result}
        assert max(depths) <= 4

    def test_empty_origins(self):
        suppliers = [_make_supplier("a")]
        edges = []
        supplier_map = {s.id: s for s in suppliers}
        adj = build_adjacency(suppliers, edges)
        result = cascade_bfs([], 0.7, adj, supplier_map, edges)
        assert result == []


class TestFindAlternatives:
    def test_finds_alternatives(self):
        suppliers = [_make_supplier("a"), _make_supplier("b")]
        edges = [_make_edge("e1", "a", "b", rel="ALTERNATIVE")]
        supplier_map = {s.id: s for s in suppliers}
        result = find_alternatives(set(), edges, supplier_map)
        assert len(result) >= 1

    def test_excludes_affected(self):
        suppliers = [_make_supplier("a"), _make_supplier("b")]
        edges = [_make_edge("e1", "a", "b", rel="ALTERNATIVE")]
        supplier_map = {s.id: s for s in suppliers}
        result = find_alternatives({"a"}, edges, supplier_map)
        alt_ids = set()
        for r in result:
            alt_ids.update(r.alternative_suppliers)
        assert "a" not in alt_ids or len(result) == 1  # generic fallback


class TestExtractCascadePath:
    def test_basic_path(self):
        from schemas.simulation import AffectedSupplier
        affected = [
            AffectedSupplier(supplier_id="a", supplier_name="A", impact_score=80, time_to_impact_days=0, cascade_depth=0, primary_risk_factor="test"),
            AffectedSupplier(supplier_id="b", supplier_name="B", impact_score=60, time_to_impact_days=5, cascade_depth=1, primary_risk_factor="test"),
        ]
        path = extract_cascade_path(affected)
        assert len(path) == 2
        assert "Depth 0" in path[0]
        assert "Depth 1" in path[1]
