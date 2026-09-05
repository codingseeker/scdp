"""
main.py — FastAPI application entry point for Supply Chain Disruption Predictor.

Wires together:
- Modular API routers under /api/v1/
- Security middleware stack
- Centralized exception handling
- Structured logging
- Graceful startup and shutdown
- CORS with explicit origin allowlist (not wildcard in production)
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core import get_settings
from core.exceptions import ErrorResponse, register_exception_handlers
from core.logging import get_logger, setup_logging
from core.middleware import register_middleware
from database.neo4j import check_neo4j_health, close_neo4j_driver, get_neo4j_driver
from database.redis import check_redis_health
from schemas.common import HealthResponse, ReadyResponse

from api.v1.audit import router as audit_router
from api.v1.auth import router as auth_router
from api.v1.intelligence import router as intelligence_router
from api.v1.metrics import router as metrics_router
from api.v1.mitigation import router as mitigation_router
from api.v1.network import router as network_router
from api.v1.risks import router as risks_router
from api.v1.simulations import public_router as simulations_public_router
from api.v1.simulations import router as simulations_router
from api.v1.suppliers import router as suppliers_router
from api.v1.threats import router as threats_router

settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting SCDP API (env={settings.app_env})")
    get_neo4j_driver()
    try:
        from database.indexes import initialize_database
        initialize_database()
    except Exception as exc:
        logger.info("Database initialization skipped (Neo4j not available): %s", type(exc).__name__)

    # On first boot (non-production), seed the bundled demo dataset so the
    # graph API is immediately usable against a freshly created Neo4j.
    if not settings.is_production:
        try:
            from database.seed import seed_network, supplier_count
            if get_neo4j_driver() is not None and supplier_count() == 0:
                seed_network()
        except Exception as exc:
            logger.warning("Auto-seed skipped: %s", type(exc).__name__)

    yield
    logger.info("Shutting down SCDP API")
    close_neo4j_driver()


app = FastAPI(
    title="Supply Chain Disruption Predictor API",
    description="Supply chain risk intelligence platform.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS — explicit origins, not wildcard in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Security middleware
register_middleware(app)

# Exception handlers
register_exception_handlers(app)

# Mount versioned API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(network_router, prefix="/api/v1")
app.include_router(suppliers_router, prefix="/api/v1")
app.include_router(risks_router, prefix="/api/v1")
app.include_router(threats_router, prefix="/api/v1")
app.include_router(simulations_router, prefix="/api/v1")
app.include_router(simulations_public_router, prefix="/api/v1")
app.include_router(intelligence_router, prefix="/api/v1")
app.include_router(mitigation_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health / Ready — always public, no auth required
#
# /health is a liveness probe: the process is up regardless of dependencies.
# /ready is a readiness probe: 503 when a configured, required dependency is
# unreachable. Missing credentials (demo mode) do not make the app unready.
# ---------------------------------------------------------------------------

def _service_status_mapping() -> dict:
    return {
        "neo4j": "connected" if check_neo4j_health() else ("not_configured" if not settings.neo4j_password else "unavailable"),
        "redis": "connected" if check_redis_health() else ("not_configured" if not settings.redis_url else "unavailable"),
        "gemini": "configured" if settings.gemini_api_key else "not_configured",
        "news_api": "configured" if settings.news_api_key else "not_configured",
        "weather_api": "configured" if settings.weather_api_key else "not_configured",
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return HealthResponse(
        status="ok",
        version=app.version,
        services=_service_status_mapping(),
    )


@app.get("/api/v1/ready", response_model=ReadyResponse, tags=["System"])
@app.get("/ready", response_model=ReadyResponse, tags=["System"])
def readiness(request: Request):
    degraded = []
    if settings.neo4j_password and not check_neo4j_health():
        degraded.append("neo4j")
    # Redis is optional caching infrastructure; it is reported, not fatal.

    if not degraded:
        return ReadyResponse(
            status="ready",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            error="not_ready",
            detail=f"Required service(s) unavailable: {', '.join(degraded)}",
            request_id=request_id,
        ).model_dump(),
    )