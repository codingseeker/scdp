"""
database/indexes.py — Neo4j constraint and index initialization.
Reproducible database setup with constraints, indexes, and seed data.
"""
from __future__ import annotations

from core.logging import get_logger
from database.neo4j import execute_query

logger = get_logger(__name__)

CONSTRAINTS = [
    "CREATE CONSTRAINT supplier_id IF NOT EXISTS FOR (s:Supplier) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
    "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT threat_id IF NOT EXISTS FOR (t:Threat) REQUIRE t.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX supplier_country IF NOT EXISTS FOR (s:Supplier) ON (s.country)",
    "CREATE INDEX supplier_tier IF NOT EXISTS FOR (s:Supplier) ON (s.tier)",
    "CREATE INDEX supplier_risk IF NOT EXISTS FOR (s:Supplier) ON (s.risk_score)",
    "CREATE INDEX supplier_category IF NOT EXISTS FOR (s:Supplier) ON (s.category)",
    "CREATE INDEX threat_severity IF NOT EXISTS FOR (t:Threat) ON (t.severity)",
    "CREATE INDEX route_reliability IF NOT EXISTS FOR ()-[r:SUPPLIES]-() ON (r.reliability)",
]


def initialize_database() -> bool:
    try:
        for constraint in CONSTRAINTS:
            execute_query(constraint)
        for index in INDEXES:
            execute_query(index)
        logger.info("Neo4j constraints and indexes initialized")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {type(e).__name__}")
        return False
