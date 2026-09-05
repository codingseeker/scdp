"""
tests/integration/test_api.py — Integration tests for FastAPI endpoints.
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
def auth_headers(client):
    response = client.post("/api/v1/auth/login", json=_creds("admin"))
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_ready(self, client):
        response = client.get("/ready")
        assert response.status_code == 200


class TestAuthEndpoints:
    def test_login_success(self, client):
        response = client.post("/api/v1/auth/login", json=_creds("admin"))
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_failure(self, client):
        username = _creds("admin")["username"]
        response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "wrong",
        })
        assert response.status_code == 401

    def test_me_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "admin"

    def test_me_unauthenticated(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestSupplierEndpoints:
    def test_list_suppliers(self, client):
        response = client.get("/api/v1/suppliers")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_supplier_pagination(self, client):
        response = client.get("/api/v1/suppliers?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5

    def test_supplier_detail(self, client):
        response = client.get("/api/v1/suppliers/s001")
        assert response.status_code == 200

    def test_supplier_not_found(self, client):
        response = client.get("/api/v1/suppliers/nonexistent")
        assert response.status_code == 404


class TestNetworkEndpoints:
    def test_get_network(self, client):
        response = client.get("/api/v1/network")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data

    def test_filter_by_tier(self, client):
        response = client.get("/api/v1/network?tier=1")
        assert response.status_code == 200
        for node in response.json()["nodes"]:
            assert node["tier"] == 1


class TestSimulationEndpoints:
    def test_simulation_requires_auth(self, client):
        response = client.post("/api/v1/simulations", json={
            "description": "Port closure",
            "severity": 0.7,
        })
        assert response.status_code == 401

    def test_simulation_with_auth(self, client, auth_headers):
        response = client.post("/api/v1/simulations", json={
            "description": "Port closure in Miami",
            "severity": 0.7,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "scenario_id" in data
        assert "affected_suppliers" in data

    def test_viewer_cannot_simulate(self, client):
        login = client.post("/api/v1/auth/login", json=_creds("viewer"))
        token = login.json()["access_token"]
        response = client.post("/api/v1/simulations", json={
            "description": "test",
            "severity": 0.5,
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_public_simulation_report_download(self, client):
        run = client.post("/api/v1/simulation", json={
            "description": "Port closure in Suez Canal",
            "severity": 0.7,
        })
        assert run.status_code == 200
        scenario_id = run.json()["scenario_id"]

        report = client.get(f"/api/v1/simulations/{scenario_id}/report")
        assert report.status_code == 200
        assert report.headers["content-disposition"].startswith("attachment;")
        assert "Supply Chain Disruption Predictor" in report.text
        assert "Port closure in Suez Canal" in report.text

    def test_report_not_found(self, client):
        report = client.get("/api/v1/simulations/doesnotexist/report")
        assert report.status_code == 404


class TestMetricsEndpoints:
    def test_get_metrics(self, client):
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200

    def test_prometheus_metrics(self, client):
        response = client.get("/api/v1/metrics/prometheus")
        assert response.status_code == 200
        assert "scdp_network_health" in response.text


class TestSecurityHeaders:
    def test_security_headers_present(self, client):
        response = client.get("/health")
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-request-id" in response.headers

    def test_request_id_returned(self, client):
        response = client.get("/health")
        assert response.headers.get("x-request-id") is not None
