"""
repositories/threat_repository.py — Threat data access.

Threats are currently derived from the bundled news dataset
(database/mock_data.py). Live threat ingestion can be layered on later.
"""
from __future__ import annotations

import uuid
from typing import List

from database.mock_data import NEWS_DB, SUPPLIER_MAP


def get_all_threats(min_risk_relevance: float = 0.6) -> List[dict]:
    threats: List[dict] = []
    for supplier_id, news_items in NEWS_DB.items():
        supplier = SUPPLIER_MAP.get(supplier_id)
        if not supplier:
            continue
        for news in news_items:
            if news.risk_relevance < min_risk_relevance:
                continue
            severity = (
                "CRITICAL"
                if news.risk_relevance >= 0.9
                else "HIGH"
                if news.risk_relevance >= 0.75
                else "MEDIUM"
            )
            threats.append(
                {
                    "id": str(uuid.uuid4()),
                    "supplier_id": supplier_id,
                    "supplier_name": supplier.name,
                    "title": news.title,
                    "source": news.source,
                    "severity": severity,
                    "published_at": news.published_at,
                    "risk_relevance": news.risk_relevance,
                }
            )
    threats.sort(key=lambda t: t["risk_relevance"], reverse=True)
    return threats