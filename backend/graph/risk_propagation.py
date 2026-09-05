"""
graph/risk_propagation.py — Deterministic risk propagation engine.

This is the original engine.py refactored into the graph/ module.
Risk calculation algorithms are kept unchanged per the non-breaking rules.
"""
from __future__ import annotations

import uuid
from typing import Any, List, Optional, Set

from schemas.simulation import AffectedSupplier, AlternativeRoute, SimulationResult
from schemas.supplier import SupplierEdge, SupplierNode


def build_adjacency(
    suppliers: List[SupplierNode],
    edges: List[SupplierEdge],
) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {s.id: [] for s in suppliers}
    for edge in edges:
        if edge.relationship in ("SUPPLIES", "LOGISTICS"):
            adj.setdefault(edge.source, []).append(edge.target)
    return adj


def build_reverse_adjacency(
    suppliers: List[SupplierNode],
    edges: List[SupplierEdge],
) -> dict[str, list[str]]:
    radj: dict[str, list[str]] = {s.id: [] for s in suppliers}
    for edge in edges:
        if edge.relationship in ("SUPPLIES", "LOGISTICS"):
            radj.setdefault(edge.target, []).append(edge.source)
    return radj


def _get_edge(edges: List[SupplierEdge], source: str, target: str) -> Optional[SupplierEdge]:
    for e in edges:
        if e.source == source and e.target == target:
            return e
    return None


def cascade_bfs(
    origin_ids: List[str],
    severity: float,
    adj: dict[str, list[str]],
    supplier_map: dict[str, SupplierNode],
    edges: List[SupplierEdge],
    max_depth: int = 4,
) -> List[AffectedSupplier]:
    visited: dict[str, dict[str, Any]] = {}
    queue: list[tuple[str, int, float, float]] = []

    for oid in origin_ids:
        if oid in supplier_map:
            s = supplier_map[oid]
            initial_impact = severity * (s.criticality / 100.0) * 100.0
            queue.append((oid, 0, initial_impact, 0.0))

    head = 0
    while head < len(queue):
        sid, depth, impact, time_acc = queue[head]
        head += 1

        if sid in visited:
            if visited[sid]["impact_score"] >= impact:
                continue
        visited[sid] = {
            "impact_score": impact,
            "cascade_depth": depth,
            "time_to_impact_days": time_acc,
        }

        if depth >= max_depth or impact < 5.0:
            continue

        for neighbor in adj.get(sid, []):
            edge = _get_edge(edges, sid, neighbor)
            if edge is None:
                continue
            edge_impact = impact * edge.reliability * 0.75
            edge_time = time_acc + edge.lead_time_days * (1.0 - severity * 0.3)
            queue.append((neighbor, depth + 1, edge_impact, edge_time))

    results: List[AffectedSupplier] = []
    for sid, data in visited.items():
        s = supplier_map.get(sid)
        if not s:
            continue
        risk_factors = [
            ("Geopolitical instability", 0.4),
            ("Weather disruption", 0.3),
            ("Supply shortfall", 0.2),
            ("Logistics bottleneck", 0.1),
        ]
        primary = max(risk_factors, key=lambda x: x[1] * (s.risk_score / 100))[0]
        results.append(AffectedSupplier(
            supplier_id=sid,
            supplier_name=s.name,
            impact_score=round(min(data["impact_score"], 100.0), 1),
            time_to_impact_days=round(data["time_to_impact_days"], 1),
            cascade_depth=data["cascade_depth"],
            primary_risk_factor=primary,
        ))

    results.sort(key=lambda x: x.impact_score, reverse=True)
    return results


def find_alternatives(
    affected_ids: Set[str],
    edges: List[SupplierEdge],
    supplier_map: dict[str, SupplierNode],
) -> List[AlternativeRoute]:
    alternatives: List[AlternativeRoute] = []
    used = set()

    for edge in edges:
        if edge.relationship != "ALTERNATIVE":
            continue
        if edge.source in affected_ids or edge.target in affected_ids:
            continue
        key = f"{edge.source}-{edge.target}"
        if key in used:
            continue
        used.add(key)
        src = supplier_map.get(edge.source)
        tgt = supplier_map.get(edge.target)
        if not src or not tgt:
            continue
        alternatives.append(AlternativeRoute(
            route_id=f"route-{edge.id}",
            description=f"Route via {src.name} ({src.country}) as alternative to {tgt.name}",
            alternative_suppliers=[edge.source, edge.target],
            cost_premium_pct=round(15.0 + (1 - edge.reliability) * 25, 1),
            lead_time_delta_days=int(edge.lead_time_days * 0.2),
            reliability_score=round(edge.reliability, 2),
            recommendation_strength="High" if edge.reliability >= 0.85 else "Medium",
        ))

    if not alternatives:
        alternatives.append(AlternativeRoute(
            route_id="route-generic-01",
            description="Engage spot-market procurement through Singapore bonded warehouses",
            alternative_suppliers=["s015", "s013"],
            cost_premium_pct=28.5,
            lead_time_delta_days=12,
            reliability_score=0.78,
            recommendation_strength="Medium",
        ))

    return alternatives[:5]


def extract_cascade_path(affected: List[AffectedSupplier]) -> List[str]:
    by_depth: dict[int, list[str]] = {}
    for a in affected:
        by_depth.setdefault(a.cascade_depth, []).append(a.supplier_name)
    return [f"Depth {d}: {', '.join(names)}" for d, names in sorted(by_depth.items())]
