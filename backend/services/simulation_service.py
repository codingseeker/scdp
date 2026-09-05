"""
services/simulation_service.py — Simulation business logic.

Orchestrates:
- Scenario keyword → affected nodes inference
- Cascade simulation via deterministic graph engine
- AI enrichment (optional; skipped when Gemini is not configured)
- Executive summary generation
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from ai.gemini_client import call_gemini, get_model_version
from ai.prompts import build_mitigation_prompt
from ai.validators import MitigationResponse, validate_ai_response
from core.logging import get_logger
from graph.risk_propagation import (
    build_adjacency,
    cascade_bfs,
    extract_cascade_path,
    find_alternatives,
)
from schemas.simulation import AffectedSupplier, AlternativeRoute, SimulationResult
from schemas.supplier import SupplierEdge, SupplierNode

logger = get_logger(__name__)

SCENARIO_KEYWORDS: list[tuple[list[str], list[str]]] = [
    (["port", "closure", "miami", "pacific", "suez", "canal"], ["s012", "s003", "s015"]),
    (["storm", "typhoon", "hurricane", "cyclone", "flood"], ["s001", "s008", "s007"]),
    (["war", "conflict", "sanction", "geopolit"], ["s007", "s004", "s011"]),
    (["semiconductor", "chip", "silicon", "microchip"], ["s006", "s001", "s013"]),
    (["cobalt", "lithium", "rare earth", "mining"], ["s007", "s011"]),
    (["logistics", "shipping", "freight", "transport"], ["s003", "s005", "s015"]),
    (["chemical", "polymer", "refin"], ["s004", "s009"]),
    (["factory", "manufacturing", "assembly", "plant"], ["s001", "s014"]),
]


def infer_affected_nodes(
    description: str,
    suppliers: List[SupplierNode],
) -> List[str]:
    desc_lower = description.lower()
    matched: set[str] = set()
    for keywords, nodes in SCENARIO_KEYWORDS:
        if any(kw in desc_lower for kw in keywords):
            matched.update(nodes)
    if not matched:
        top = sorted(suppliers, key=lambda s: s.risk_score, reverse=True)[:3]
        matched = {s.id for s in top}
    return list(matched)


def _generate_summary(
    description: str,
    affected: List[AffectedSupplier],
    routes: List[AlternativeRoute],
    severity: float,
    network_impact: float,
) -> tuple[str, list[str]]:
    top_3 = [a.supplier_name for a in affected[:3]]
    top_route = routes[0].description if routes else "spot procurement"

    summary = (
        f"Scenario analysis for: '{description}'. "
        f"Severity {severity:.0%}. "
        f"Network impact: {network_impact:.1f}/100. "
        f"Top affected suppliers: {', '.join(top_3)}. "
        f"Recommended immediate action: {top_route}. "
        f"Time to critical impact: {affected[0].time_to_impact_days if affected else 0:.0f} days."
    )

    actions = [
        f"Activate emergency inventory buffers for {top_3[0] if top_3 else 'key suppliers'}.",
        f"Contact {routes[0].alternative_suppliers[0] if routes and routes[0].alternative_suppliers else 'backup suppliers'} for capacity confirmation.",
        "Issue supply chain alert to logistics partners.",
        "Convene daily risk committee review for the next 14 days.",
        "Reassess safety stock levels across all Tier 1 suppliers.",
        "Initiate dual-sourcing negotiations for single-source dependencies.",
    ]
    return summary, actions


async def run_simulation(
    description: str,
    affected_nodes: Optional[List[str]],
    severity: float,
    suppliers: List[SupplierNode],
    edges: List[SupplierEdge],
    enable_ai: bool = True,
) -> SimulationResult:
    supplier_map = {s.id: s for s in suppliers}
    adj = build_adjacency(suppliers, edges)
    origin_ids = affected_nodes if affected_nodes else infer_affected_nodes(description, suppliers)

    affected = cascade_bfs(origin_ids, severity, adj, supplier_map, edges)
    affected_set = {a.supplier_id for a in affected}
    routes = find_alternatives(affected_set, edges, supplier_map)
    cascade_path = extract_cascade_path(affected)

    avg_impact = sum(a.impact_score for a in affected) / len(affected) if affected else 0
    network_impact = round(min(avg_impact * severity, 100.0), 1)
    time_to_impact = affected[0].time_to_impact_days if affected else 30.0
    summary, actions = _generate_summary(description, affected, routes, severity, network_impact)

    ai_enriched = False
    ai_model_version = None
    confidence_score = None

    if enable_ai:
        try:
            prompt = build_mitigation_prompt(
                description,
                [{"id": a.supplier_id, "name": a.supplier_name} for a in affected[:5]],
                [{"id": r.route_id} for r in routes[:3]],
            )
            raw_response = await call_gemini(
                prompt["system_instruction"],
                prompt["user_prompt"],
            )
            if raw_response:
                validated = validate_ai_response(raw_response, MitigationResponse)
                if validated:
                    ai_enriched = True
                    ai_model_version = get_model_version()
                    confidence_score = 0.85
                    summary = validated.executive_summary + f" [AI-enriched via {ai_model_version}]"
                    actions = [s.description for s in validated.strategies]
        except Exception as e:
            logger.warning(f"AI enrichment failed, using deterministic results: {type(e).__name__}")

    return SimulationResult(
        scenario_id=str(uuid.uuid4()),
        scenario_description=description,
        overall_network_impact=network_impact,
        affected_suppliers=affected,
        cascade_path=cascade_path,
        time_to_impact_days=round(time_to_impact, 1),
        alternative_routes=routes,
        executive_summary=summary,
        mitigation_actions=actions,
        ai_enriched=ai_enriched,
        ai_model_version=ai_model_version,
        confidence_score=confidence_score,
    )
