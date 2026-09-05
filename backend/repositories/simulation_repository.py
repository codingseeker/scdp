"""
repositories/simulation_repository.py — Simulation history storage.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from schemas.simulation import SimulationResult

_simulation_history: List[Dict] = []


def save_simulation(result: SimulationResult) -> str:
    entry = {
        "id": result.scenario_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result.model_dump(),
    }
    _simulation_history.append(entry)
    if len(_simulation_history) > 100:
        _simulation_history.pop(0)
    return result.scenario_id


def get_simulation(simulation_id: str) -> Optional[Dict]:
    for entry in _simulation_history:
        if entry["id"] == simulation_id:
            return entry
    return None


def list_simulations(page: int = 1, page_size: int = 20) -> Dict:
    total = len(_simulation_history)
    start = (page - 1) * page_size
    end = start + page_size
    items = _simulation_history[start:end]
    return {"total": total, "page": page, "page_size": page_size, "items": items}
