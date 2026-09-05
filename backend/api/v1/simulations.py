"""
api/v1/simulations.py — Simulation API endpoints.

- Authenticated simulations for analyst/admin roles (audited)
- A public /simulation endpoint used by the SPA demo
- Simulation history stored in the simulation repository
- Downloadable Markdown report per simulation
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response

from core import get_settings
from core.exceptions import NotFoundError
from core.logging import get_logger
from core.security import UserInfo, UserRole, get_optional_user, require_role
from repositories.simulation_repository import get_simulation, list_simulations, save_simulation
from repositories.supplier_repository import get_all_edges, get_all_suppliers
from schemas.simulation import ScenarioRequest, SimulationResult
from services.simulation_service import run_simulation

logger = get_logger(__name__)
router = APIRouter(prefix="/simulations", tags=["Simulation"])


@router.post("", response_model=SimulationResult)
async def create_simulation(
    request: ScenarioRequest,
    current_user: UserInfo = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    logger.info(
        f"Simulation requested by {current_user.username}: {request.description!r}, severity={request.severity}"
    )
    suppliers = get_all_suppliers()
    edges = get_all_edges()

    result = await run_simulation(
        description=request.description,
        affected_nodes=request.affected_nodes,
        severity=request.severity,
        suppliers=suppliers,
        edges=edges,
    )

    save_simulation(result)
    from core.audit import record_audit_event
    record_audit_event(
        actor=current_user.username,
        action="create_simulation",
        resource="simulation",
        resource_id=result.scenario_id,
        details={"impact": result.overall_network_impact, "severity": request.severity},
    )
    logger.info(f"Simulation complete: scenario_id={result.scenario_id}, impact={result.overall_network_impact}")
    return result


@router.get("")
async def get_simulations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserInfo = Depends(get_optional_user),
):
    settings = get_settings()
    page_size = min(page_size, settings.max_pagination_limit)
    return list_simulations(page, page_size)


@router.get("/{simulation_id}")
async def get_simulation_detail(
    simulation_id: str,
    user=Depends(get_optional_user),
):
    result = get_simulation(simulation_id)
    if not result:
        raise NotFoundError("Simulation", simulation_id)
    return result


@router.get("/{simulation_id}/report")
async def download_simulation_report(
    simulation_id: str,
    user=Depends(get_optional_user),
):
    """Return the simulation report as a downloadable Markdown file."""
    entry = get_simulation(simulation_id)
    if not entry:
        raise NotFoundError("Simulation", simulation_id)

    from services.report_service import render_simulation_report
    content = render_simulation_report(entry["result"])

    filename = f"scdp-report-{simulation_id}.md"
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


# Public demo route consumed by the frontend SPA (no auth, no audit trail).
# The authenticated POST /simulations is the audited path.
public_router = APIRouter(prefix="/simulation", tags=["Simulation"])


@public_router.post("", response_model=SimulationResult)
async def run_demo_simulation(request: ScenarioRequest):
    suppliers = get_all_suppliers()
    edges = get_all_edges()
    result = await run_simulation(
        description=request.description,
        affected_nodes=request.affected_nodes,
        severity=request.severity,
        suppliers=suppliers,
        edges=edges,
    )
    save_simulation(result)
    return result