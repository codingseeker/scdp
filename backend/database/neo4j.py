"""
database/neo4j.py — Neo4j connection management with pooling, retry, and security.

- Connection pooling with configurable pool size
- Encrypted connections in production
- Parameterized queries ONLY (never string concatenation)
- Query timeout enforcement
- Retry handling for transient failures
- Returns None (mock-data mode) when Neo4j is not configured
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from core import get_settings
from core.logging import get_logger

logger = get_logger(__name__)

_driver = None


def get_neo4j_driver():
    global _driver
    settings = get_settings()

    if not settings.neo4j_password:
        logger.debug("Neo4j credentials not configured — using bundled demo data")
        return None

    if _driver is not None:
        return _driver

    try:
        from neo4j import GraphDatabase

        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
            max_connection_pool_size=settings.neo4j_max_connection_pool_size,
            connection_timeout=settings.neo4j_connection_timeout,
            encrypted=settings.is_production,
        )
        _driver.verify_connectivity()
        logger.info("Neo4j connection established")
        return _driver
    except Exception as e:
        logger.error(f"Neo4j connection failed: {type(e).__name__}")
        _driver = None
        return None


def close_neo4j_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
        logger.info("Neo4j connection closed")


def execute_query(
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> List[Dict[str, Any]]:
    driver = get_neo4j_driver()
    if driver is None:
        return []

    settings = get_settings()
    start = time.monotonic()

    for attempt in (1, 2):
        try:
            with driver.session(database=settings.neo4j_database) as session:
                result = session.run(query, parameters or {}, timeout=timeout)
                records = [dict(record) for record in result]

            duration_ms = round((time.monotonic() - start) * 1000, 2)
            if duration_ms > 5000:
                logger.warning(f"Slow Neo4j query: {duration_ms}ms", extra={
                    "extra_data": {"query_preview": query[:100], "duration_ms": duration_ms}
                })
            return records
        except Exception as e:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            logger.warning(f"Neo4j query failed (attempt {attempt}): {type(e).__name__}")

    logger.error(f"Neo4j query failed after retry: {type(e).__name__}")
    return []


def check_neo4j_health() -> bool:
    driver = get_neo4j_driver()
    if driver is None:
        return False
    try:
        driver.verify_connectivity()
        return True
    except Exception:
        return False