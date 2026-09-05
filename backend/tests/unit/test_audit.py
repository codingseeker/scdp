"""
tests/unit/test_audit.py — Unit tests for audit logging system.
"""
import pytest
from core.audit import record_audit_event, get_audit_logs


class TestAuditSystem:
    def test_record_audit_event(self):
        entry = record_audit_event(
            actor="admin",
            action="login",
            resource="auth",
            result="SUCCESS",
            details={"test": True},
        )
        assert entry.id.startswith("audit-")
        assert entry.actor == "admin"
        assert entry.action == "login"
        assert entry.resource == "auth"
        assert entry.result == "SUCCESS"

    def test_get_audit_logs_filtering(self):
        record_audit_event(actor="user1", action="simulation", resource="sim")
        record_audit_event(actor="user2", action="config_change", resource="config")

        logs_user1 = get_audit_logs(actor="user1")
        assert any(e.actor == "user1" for e in logs_user1["items"])

        logs_config = get_audit_logs(action="config_change")
        assert any(e.action == "config_change" for e in logs_config["items"])
