"""
database/mock_data.py — Bundled demo dataset used as a fallback provider
when Neo4j and / or external intelligence APIs are not configured.

This is deliberately mock content: it powers the UI in demo mode and gives
repositories a well-defined fallback. Production deployments should connect
a real Neo4j database and real news / weather APIs; this module is then never
read from.
"""
from __future__ import annotations

from schemas import (
    SupplierNode, SupplierEdge,
    NewsItem, WeatherAlert, SupplierDetail, RiskLevel,
)

# ---------------------------------------------------------------------------
# Supplier Nodes
# ---------------------------------------------------------------------------
SUPPLIERS: list[SupplierNode] = [
    # Tier 1 — direct suppliers to focal company
    SupplierNode(id="s001", name="Apex Electronics", country="China", city="Shenzhen",
                 category="Electronics", tier=1, risk_score=72.4, risk_level=RiskLevel.HIGH,
                 revenue_dependency=34.0, lead_time_days=45, alternatives_count=2,
                 lat=22.5431, lng=114.0579, active_threats=3, criticality=88.0),

    SupplierNode(id="s002", name="PrecisionMetal Corp", country="Taiwan", city="Taipei",
                 category="Metal Components", tier=1, risk_score=51.2, risk_level=RiskLevel.MEDIUM,
                 revenue_dependency=18.5, lead_time_days=30, alternatives_count=3,
                 lat=25.0330, lng=121.5654, active_threats=1, criticality=70.0),

    SupplierNode(id="s003", name="Nordic Logistics", country="Germany", city="Hamburg",
                 category="Logistics", tier=1, risk_score=28.0, risk_level=RiskLevel.LOW,
                 revenue_dependency=12.0, lead_time_days=7, alternatives_count=5,
                 lat=53.5753, lng=10.0153, active_threats=0, criticality=55.0),

    SupplierNode(id="s004", name="MidEast Polymers", country="Saudi Arabia", city="Riyadh",
                 category="Chemicals", tier=1, risk_score=64.8, risk_level=RiskLevel.HIGH,
                 revenue_dependency=22.0, lead_time_days=60, alternatives_count=1,
                 lat=24.7136, lng=46.6753, active_threats=2, criticality=82.0),

    SupplierNode(id="s005", name="Pacific Freight Lines", country="Japan", city="Tokyo",
                 category="Logistics", tier=1, risk_score=33.1, risk_level=RiskLevel.LOW,
                 revenue_dependency=9.0, lead_time_days=14, alternatives_count=4,
                 lat=35.6762, lng=139.6503, active_threats=0, criticality=45.0),

    # Tier 2 — suppliers to Tier 1
    SupplierNode(id="s006", name="SiliconValley Semi", country="USA", city="San Jose",
                 category="Semiconductors", tier=2, risk_score=44.3, risk_level=RiskLevel.MEDIUM,
                 revenue_dependency=0.0, lead_time_days=90, alternatives_count=2,
                 lat=37.3382, lng=-121.8863, active_threats=1, criticality=78.0),

    SupplierNode(id="s007", name="RareEarth Mining Co", country="Congo", city="Lubumbashi",
                 category="Raw Materials", tier=2, risk_score=88.5, risk_level=RiskLevel.CRITICAL,
                 revenue_dependency=0.0, lead_time_days=120, alternatives_count=0,
                 lat=-11.6609, lng=27.4794, active_threats=5, criticality=95.0),

    SupplierNode(id="s008", name="Yangtze Steel Works", country="China", city="Wuhan",
                 category="Raw Materials", tier=2, risk_score=61.7, risk_level=RiskLevel.HIGH,
                 revenue_dependency=0.0, lead_time_days=35, alternatives_count=2,
                 lat=30.5928, lng=114.3055, active_threats=2, criticality=65.0),

    SupplierNode(id="s009", name="Rotterdam Chemical Hub", country="Netherlands", city="Rotterdam",
                 category="Chemicals", tier=2, risk_score=39.6, risk_level=RiskLevel.MEDIUM,
                 revenue_dependency=0.0, lead_time_days=21, alternatives_count=3,
                 lat=51.9244, lng=4.4777, active_threats=1, criticality=60.0),

    SupplierNode(id="s010", name="Indian Textile Mills", country="India", city="Mumbai",
                 category="Textiles", tier=2, risk_score=47.2, risk_level=RiskLevel.MEDIUM,
                 revenue_dependency=0.0, lead_time_days=55, alternatives_count=3,
                 lat=19.0760, lng=72.8777, active_threats=1, criticality=50.0),

    # Tier 3 — deep supply chain
    SupplierNode(id="s011", name="Cobalt Trade Africa", country="Zambia", city="Ndola",
                 category="Raw Materials", tier=3, risk_score=79.3, risk_level=RiskLevel.HIGH,
                 revenue_dependency=0.0, lead_time_days=150, alternatives_count=1,
                 lat=-12.9587, lng=28.6366, active_threats=3, criticality=72.0),

    SupplierNode(id="s012", name="Suez Canal Logistics", country="Egypt", city="Port Said",
                 category="Logistics", tier=3, risk_score=55.8, risk_level=RiskLevel.MEDIUM,
                 revenue_dependency=0.0, lead_time_days=0, alternatives_count=1,
                 lat=31.2653, lng=32.3019, active_threats=2, criticality=85.0),

    SupplierNode(id="s013", name="Vietnam Electronics Mfg", country="Vietnam", city="Ho Chi Minh City",
                 category="Electronics", tier=2, risk_score=42.1, risk_level=RiskLevel.MEDIUM,
                 revenue_dependency=0.0, lead_time_days=40, alternatives_count=3,
                 lat=10.8231, lng=106.6297, active_threats=0, criticality=55.0),

    SupplierNode(id="s014", name="Mexico Assembly Plant", country="Mexico", city="Monterrey",
                 category="Assembly", tier=1, risk_score=36.5, risk_level=RiskLevel.LOW,
                 revenue_dependency=14.5, lead_time_days=10, alternatives_count=2,
                 lat=25.6866, lng=-100.3161, active_threats=1, criticality=60.0),

    SupplierNode(id="s015", name="Singapore Port Authority", country="Singapore", city="Singapore",
                 category="Logistics", tier=2, risk_score=22.4, risk_level=RiskLevel.LOW,
                 revenue_dependency=0.0, lead_time_days=5, alternatives_count=6,
                 lat=1.3521, lng=103.8198, active_threats=0, criticality=40.0),
]

SUPPLIER_MAP = {s.id: s for s in SUPPLIERS}

# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------
EDGES: list[SupplierEdge] = [
    # Tier 2 → Tier 1 supply relationships
    SupplierEdge(id="e001", source="s007", target="s001", relationship="SUPPLIES",
                 volume_usd=45_000_000, lead_time_days=120, reliability=0.62),
    SupplierEdge(id="e002", source="s006", target="s001", relationship="SUPPLIES",
                 volume_usd=80_000_000, lead_time_days=90, reliability=0.78),
    SupplierEdge(id="e003", source="s008", target="s002", relationship="SUPPLIES",
                 volume_usd=30_000_000, lead_time_days=35, reliability=0.71),
    SupplierEdge(id="e004", source="s009", target="s004", relationship="SUPPLIES",
                 volume_usd=55_000_000, lead_time_days=21, reliability=0.83),
    SupplierEdge(id="e005", source="s013", target="s001", relationship="SUPPLIES",
                 volume_usd=25_000_000, lead_time_days=40, reliability=0.85),
    SupplierEdge(id="e006", source="s010", target="s014", relationship="SUPPLIES",
                 volume_usd=15_000_000, lead_time_days=55, reliability=0.76),
    # Tier 3 → Tier 2
    SupplierEdge(id="e007", source="s011", target="s007", relationship="SUPPLIES",
                 volume_usd=20_000_000, lead_time_days=150, reliability=0.55),
    SupplierEdge(id="e008", source="s012", target="s009", relationship="LOGISTICS",
                 volume_usd=10_000_000, lead_time_days=0, reliability=0.72),
    SupplierEdge(id="e009", source="s015", target="s013", relationship="LOGISTICS",
                 volume_usd=8_000_000, lead_time_days=5, reliability=0.92),
    # Logistics
    SupplierEdge(id="e010", source="s003", target="s001", relationship="LOGISTICS",
                 volume_usd=12_000_000, lead_time_days=7, reliability=0.91),
    SupplierEdge(id="e011", source="s005", target="s002", relationship="LOGISTICS",
                 volume_usd=9_000_000, lead_time_days=14, reliability=0.88),
    SupplierEdge(id="e012", source="s003", target="s004", relationship="LOGISTICS",
                 volume_usd=7_000_000, lead_time_days=7, reliability=0.89),
    # Alternative suppliers
    SupplierEdge(id="e013", source="s013", target="s006", relationship="ALTERNATIVE",
                 volume_usd=0, lead_time_days=45, reliability=0.82),
    SupplierEdge(id="e014", source="s015", target="s003", relationship="ALTERNATIVE",
                 volume_usd=0, lead_time_days=8, reliability=0.90),
]

# ---------------------------------------------------------------------------
# News items (per supplier)
# ---------------------------------------------------------------------------
NEWS_DB: dict[str, list[NewsItem]] = {
    "s001": [
        NewsItem(title="Shenzhen factory output hits 18-month low amid power rationing",
                 source="Reuters", published_at="2026-08-15T09:22:00Z",
                 sentiment="negative", risk_relevance=0.82,
                 url="https://reuters.com/example"),
        NewsItem(title="China tightens export controls on advanced electronics components",
                 source="Bloomberg", published_at="2026-08-14T14:05:00Z",
                 sentiment="negative", risk_relevance=0.91,
                 url="https://bloomberg.com/example"),
        NewsItem(title="Apex Electronics Q2 revenue beats estimates despite headwinds",
                 source="FT", published_at="2026-08-12T07:30:00Z",
                 sentiment="positive", risk_relevance=0.35,
                 url="https://ft.com/example"),
    ],
    "s004": [
        NewsItem(title="Saudi Aramco warns of potential output disruption amid regional tensions",
                 source="Al Jazeera", published_at="2026-08-16T11:00:00Z",
                 sentiment="negative", risk_relevance=0.88,
                 url="https://aljazeera.com/example"),
        NewsItem(title="Oil price surge linked to Red Sea shipping lane closures",
                 source="WSJ", published_at="2026-08-15T16:30:00Z",
                 sentiment="negative", risk_relevance=0.75,
                 url="https://wsj.com/example"),
    ],
    "s007": [
        NewsItem(title="DRC mining sector halted by civil unrest in Katanga province",
                 source="African Business", published_at="2026-08-16T08:00:00Z",
                 sentiment="negative", risk_relevance=0.95,
                 url="https://africanbusiness.com/example"),
        NewsItem(title="Global cobalt prices rise 23% YTD as supply shrinks",
                 source="Mining Journal", published_at="2026-08-14T10:15:00Z",
                 sentiment="negative", risk_relevance=0.89,
                 url="https://miningjournal.com/example"),
    ],
    "s012": [
        NewsItem(title="Suez Canal vessel congestion reaches 3-year high",
                 source="Lloyd's List", published_at="2026-08-17T06:45:00Z",
                 sentiment="negative", risk_relevance=0.93,
                 url="https://lloydslist.com/example"),
    ],
    "s002": [
        NewsItem(title="Taiwan semiconductor exports decline on US tariff uncertainty",
                 source="Nikkei Asia", published_at="2026-08-15T13:00:00Z",
                 sentiment="negative", risk_relevance=0.67,
                 url="https://nikkei.com/example"),
    ],
    "s006": [
        NewsItem(title="TSMC-linked suppliers expand Vietnam capacity to reduce geopolitical risk",
                 source="TechCrunch", published_at="2026-08-13T09:00:00Z",
                 sentiment="positive", risk_relevance=0.45,
                 url="https://techcrunch.com/example"),
    ],
}

# ---------------------------------------------------------------------------
# Weather alerts
# ---------------------------------------------------------------------------
WEATHER_DB: dict[str, list[WeatherAlert]] = {
    "s001": [
        WeatherAlert(location="Shenzhen, China", event_type="Typhoon",
                     severity="HIGH", affected_suppliers=["s001", "s008"],
                     eta_hours=36),
    ],
    "s004": [
        WeatherAlert(location="Arabian Sea", event_type="Cyclone",
                     severity="MEDIUM", affected_suppliers=["s004", "s012"],
                     eta_hours=72),
    ],
    "s007": [
        WeatherAlert(location="Central Africa", event_type="Flooding",
                     severity="HIGH", affected_suppliers=["s007", "s011"],
                     eta_hours=12),
    ],
    "s011": [
        WeatherAlert(location="Zambia", event_type="Drought",
                     severity="MEDIUM", affected_suppliers=["s011"],
                     eta_hours=0),
    ],
    "s003": [],
    "s005": [],
}

# ---------------------------------------------------------------------------
# Risk breakdown per supplier
# ---------------------------------------------------------------------------
RISK_BREAKDOWN: dict[str, dict] = {
    "s001": {"geopolitical": 35, "weather": 22, "financial": 8, "logistics": 7},
    "s002": {"geopolitical": 28, "weather": 5, "financial": 10, "logistics": 8},
    "s003": {"geopolitical": 5, "weather": 10, "financial": 5, "logistics": 8},
    "s004": {"geopolitical": 40, "weather": 15, "financial": 5, "logistics": 5},
    "s005": {"geopolitical": 8, "weather": 12, "financial": 5, "logistics": 8},
    "s006": {"geopolitical": 20, "weather": 5, "financial": 12, "logistics": 7},
    "s007": {"geopolitical": 50, "weather": 20, "financial": 8, "logistics": 10},
    "s008": {"geopolitical": 30, "weather": 18, "financial": 7, "logistics": 6},
    "s009": {"geopolitical": 10, "weather": 12, "financial": 8, "logistics": 9},
    "s010": {"geopolitical": 18, "weather": 14, "financial": 8, "logistics": 7},
    "s011": {"geopolitical": 42, "weather": 20, "financial": 10, "logistics": 7},
    "s012": {"geopolitical": 30, "weather": 12, "financial": 5, "logistics": 8},
    "s013": {"geopolitical": 15, "weather": 10, "financial": 9, "logistics": 8},
    "s014": {"geopolitical": 12, "weather": 8, "financial": 8, "logistics": 8},
    "s015": {"geopolitical": 5, "weather": 8, "financial": 4, "logistics": 5},
}


def get_supplier_detail(supplier_id: str) -> SupplierDetail | None:
    supplier = SUPPLIER_MAP.get(supplier_id)
    if not supplier:
        return None
    upstream = [e.source for e in EDGES if e.target == supplier_id]
    downstream = [e.target for e in EDGES if e.source == supplier_id]
    return SupplierDetail(
        supplier=supplier,
        news=NEWS_DB.get(supplier_id, []),
        weather_alerts=WEATHER_DB.get(supplier_id, []),
        upstream_suppliers=upstream,
        downstream_customers=downstream,
        risk_breakdown=RISK_BREAKDOWN.get(supplier_id, {}),
    )