"""
repositories/supplier_repository.py — Supplier data access.

Backed by Neo4j when configured; otherwise falls back to the bundled demo
dataset (database/mock_data.py) so the API and UI work out of the box.
All Cypher queries are parameterized.
"""
from __future__ import annotations

from typing import List, Optional

from core.logging import get_logger
from database.mock_data import (
    EDGES as MOCK_EDGES,
    SUPPLIERS as MOCK_SUPPLIERS,
    get_supplier_detail as get_mock_supplier_detail,
)
from database.neo4j import execute_query, get_neo4j_driver
from schemas.supplier import SupplierDetail, SupplierEdge, SupplierNode

logger = get_logger(__name__)


def get_all_suppliers() -> List[SupplierNode]:
    if get_neo4j_driver() is None:
        return MOCK_SUPPLIERS

    records = execute_query("MATCH (s:Supplier) RETURN s ORDER BY s.risk_score DESC")
    if not records:
        logger.info("Neo4j contains no suppliers — using bundled demo dataset")
        return MOCK_SUPPLIERS
    return [_record_to_supplier(record) for record in records]


def get_all_edges() -> List[SupplierEdge]:
    if get_neo4j_driver() is None:
        return MOCK_EDGES

    records = execute_query(
        "MATCH (a:Supplier)-[r:CONNECTED]->(b:Supplier) "
        "RETURN a.id AS source, b.id AS target, r"
    )
    if not records:
        logger.info("Neo4j contains no edges — using bundled demo dataset")
        return MOCK_EDGES

    edges: List[SupplierEdge] = []
    for record in records:
        rel = dict(record.get("r")) if record.get("r") is not None else {}
        edges.append(
            SupplierEdge(
                id=rel.get("id", ""),
                source=str(record.get("source", "")),
                target=str(record.get("target", "")),
                relationship=rel.get("relationship", "SUPPLIES"),
                volume_usd=rel.get("volume_usd", 0),
                lead_time_days=rel.get("lead_time_days", 0),
                reliability=rel.get("reliability", 0.0),
            )
        )
    return edges


def get_supplier_by_id(supplier_id: str) -> Optional[SupplierDetail]:
    if get_neo4j_driver() is None:
        return get_mock_supplier_detail(supplier_id)

    records = execute_query(
        "MATCH (s:Supplier {id: $id}) RETURN s",
        parameters={"id": supplier_id},
    )
    if not records:
        return None

    supplier = _record_to_supplier(records[0])

    upstream = [
        row.get("id")
        for row in execute_query(
            "MATCH (u:Supplier)-[r:CONNECTED]->(:Supplier {id: $id}) "
            "WHERE r.relationship <> 'ALTERNATIVE' RETURN u.id AS id",
            parameters={"id": supplier_id},
        )
        if row.get("id")
    ]
    downstream = [
        row.get("id")
        for row in execute_query(
            "MATCH (:Supplier {id: $id})-[r:CONNECTED]->(d:Supplier) "
            "WHERE r.relationship <> 'ALTERNATIVE' RETURN d.id AS id",
            parameters={"id": supplier_id},
        )
        if row.get("id")
    ]

    return SupplierDetail(
        supplier=supplier,
        news=[],
        weather_alerts=[],
        upstream_suppliers=upstream,
        downstream_customers=downstream,
        risk_breakdown=_derive_risk_breakdown(supplier),
    )


def _derive_risk_breakdown(supplier: SupplierNode) -> dict:
    score = supplier.risk_score
    return {
        "geopolitical": round(score * 0.40, 1),
        "weather": round(score * 0.25, 1),
        "financial": round(score * 0.20, 1),
        "logistics": round(score * 0.15, 1),
    }


def _record_to_supplier(record: dict) -> SupplierNode:
    raw = record.get("s")
    props = dict(raw) if raw is not None else {}
    return SupplierNode(**props)