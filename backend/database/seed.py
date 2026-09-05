"""
database/seed.py — Database seeding with the bundled demo dataset.
Uses parameterized Cypher queries — never string concatenation.
"""
from __future__ import annotations

from core.logging import get_logger
from database.mock_data import EDGES, SUPPLIERS
from database.neo4j import execute_query

logger = get_logger(__name__)


def seed_suppliers(suppliers: list) -> int:
    count = 0
    for s in suppliers:
        execute_query(
            """
            MERGE (s:Supplier {id: $id})
            SET s.name = $name,
                s.country = $country,
                s.city = $city,
                s.category = $category,
                s.tier = $tier,
                s.risk_score = $risk_score,
                s.risk_level = $risk_level,
                s.revenue_dependency = $revenue_dependency,
                s.lead_time_days = $lead_time_days,
                s.alternatives_count = $alternatives_count,
                s.lat = $lat,
                s.lng = $lng,
                s.active_threats = $active_threats,
                s.criticality = $criticality
            """,
            parameters={
                "id": s.id,
                "name": s.name,
                "country": s.country,
                "city": s.city,
                "category": s.category,
                "tier": s.tier,
                "risk_score": s.risk_score,
                "risk_level": s.risk_level.value,
                "revenue_dependency": s.revenue_dependency,
                "lead_time_days": s.lead_time_days,
                "alternatives_count": s.alternatives_count,
                "lat": s.lat,
                "lng": s.lng,
                "active_threats": s.active_threats,
                "criticality": s.criticality,
            },
        )
        count += 1
    logger.info(f"Seeded {count} suppliers")
    return count


def seed_edges(edges: list) -> int:
    count = 0
    for e in edges:
        execute_query(
            """
            MATCH (src:Supplier {id: $source})
            MATCH (tgt:Supplier {id: $target})
            MERGE (src)-[r:CONNECTED {id: $id}]->(tgt)
            SET r.relationship = $relationship,
                r.volume_usd = $volume_usd,
                r.lead_time_days = $lead_time_days,
                r.reliability = $reliability
            """,
            parameters={
                "id": e.id,
                "source": e.source,
                "target": e.target,
                "relationship": e.relationship,
                "volume_usd": e.volume_usd,
                "lead_time_days": e.lead_time_days,
                "reliability": e.reliability,
            },
        )
        count += 1
    logger.info(f"Seeded {count} edges")
    return count


def supplier_count() -> int:
    records = execute_query("MATCH (s:Supplier) RETURN count(s) AS count")
    if not records:
        return 0
    return int(records[0].get("count") or 0)


def seed_network() -> tuple[int, int]:
    """Seed the bundled demo dataset into Neo4j. Returns (suppliers, edges)."""
    logger.info("Seeding demo dataset into Neo4j")
    suppliers = seed_suppliers(SUPPLIERS)
    edges = seed_edges(EDGES)
    logger.info("Demo dataset seeding complete")
    return suppliers, edges
