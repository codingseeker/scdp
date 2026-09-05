"""
core/audit.py — Audit logging for security-sensitive actions.

Tracks authentication events, authorization failures, simulation operations,
and administrative actions with actor, resource, timestamp, and request ID.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.logging import get_logger, log_security_event
from schemas.common import AuditLogEntry

logger = get_logger("audit")

_audit_log_store: List[AuditLogEntry] = []
MAX_AUDIT_LOGS = 1000


def record_audit_event(
    actor: str,
    action: str,
    resource: str,
    result: str = "SUCCESS",
    resource_id: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLogEntry:
    """Record an audit log entry for security and compliance tracking."""
    entry = AuditLogEntry(
        id=f"audit-{uuid.uuid4()}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        actor=actor,
        action=action,
        resource=resource,
        resource_id=resource_id,
        request_id=request_id,
        result=result,
        details=details,
    )

    _audit_log_store.append(entry)
    if len(_audit_log_store) > MAX_AUDIT_LOGS:
        _audit_log_store.pop(0)

    log_security_event(
        logger,
        event_type=f"AUDIT_{action.upper()}",
        message=f"Audit event: {actor} performed {action} on {resource} ({result})",
        request_id=request_id,
        user_id=actor,
        details={"resource_id": resource_id, "result": result, **(details or {})},
    )

    return entry


def get_audit_logs(
    actor: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Retrieve filtered audit logs (Admin only)."""
    filtered = _audit_log_store
    if actor:
        filtered = [e for e in filtered if e.actor == actor]
    if action:
        filtered = [e for e in filtered if e.action == action]
    if resource:
        filtered = [e for e in filtered if e.resource == resource]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }
