"""
tests/integration/test_audit_api.py — Integration tests for audit endpoint.
"""
import os

import pytest
from fastapi.testclient import TestClient


def _creds(role: str) -> dict:
    return {
        "username": os.environ[f"{role.upper()}_USERNAME"],
        "password": os.environ[f"{role.upper()}_PASSWORD"],
    }


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    response = client.post("/api/v1/auth/login", json=_creds("admin"))
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analyst_headers(client):
    response = client.post("/api/v1/auth/login", json=_creds("analyst"))
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuditApi:
    def test_admin_can_access_audit_logs(self, client, admin_headers):
        res = client.get("/api/v1/audit", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_analyst_forbidden_from_audit(self, client, analyst_headers):
        res = client.get("/api/v1/audit", headers=analyst_headers)
        assert res.status_code == 403

    def test_unauthenticated_forbidden(self, client):
        res = client.get("/api/v1/audit")
        assert res.status_code == 401
