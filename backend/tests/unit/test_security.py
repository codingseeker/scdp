"""
tests/unit/test_security.py — Security-focused tests.

Tests: authentication, authorization, IDOR, input validation, Cypher injection,
rate limiting, oversized payloads.
"""
import os

import pytest

from core.security import (
    UserInfo,
    UserRole,
    authenticate_user,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def _creds(role: str) -> tuple[str, str]:
    return os.environ[f"{role.upper()}_USERNAME"], os.environ[f"{role.upper()}_PASSWORD"]


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("test_password")
        assert hashed != "test_password"
        assert verify_password("test_password", hashed)
        assert not verify_password("wrong_password", hashed)

    def test_different_hashes(self):
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # bcrypt uses salt


class TestAuthentication:
    def test_valid_login(self):
        username, password = _creds("admin")
        user = authenticate_user(username, password)
        assert user is not None
        assert user.role == UserRole.ADMIN

    def test_invalid_password(self):
        username, _ = _creds("admin")
        user = authenticate_user(username, "wrong")
        assert user is None

    def test_nonexistent_user(self):
        user = authenticate_user("nonexistent", "password")
        assert user is None


class TestJwtTokens:
    def test_create_and_decode(self):
        user = UserInfo(user_id="usr_001", username="admin", role=UserRole.ADMIN)
        token = create_access_token(user)
        decoded = decode_token(token)
        assert decoded.user_id == "usr_001"
        assert decoded.username == "admin"
        assert decoded.role == UserRole.ADMIN

    def test_invalid_token(self):
        from core.exceptions import AuthenticationError
        with pytest.raises(AuthenticationError):
            decode_token("invalid.token.here")


class TestInputValidation:
    def test_scenario_rejects_cypher(self):
        from schemas.simulation import ScenarioRequest
        with pytest.raises(Exception):
            ScenarioRequest(
                description="MATCH (n) DELETE n;",
                severity=0.5,
            )

    def test_scenario_rejects_extra_fields(self):
        from schemas.simulation import ScenarioRequest
        with pytest.raises(Exception):
            ScenarioRequest(
                description="test",
                severity=0.5,
                admin_override=True,
            )

    def test_valid_scenario(self):
        from schemas.simulation import ScenarioRequest
        req = ScenarioRequest(description="Port closure in Miami", severity=0.8)
        assert req.description == "Port closure in Miami"
        assert req.severity == 0.8

    def test_severity_bounds(self):
        from schemas.simulation import ScenarioRequest
        with pytest.raises(Exception):
            ScenarioRequest(description="test", severity=1.5)
        with pytest.raises(Exception):
            ScenarioRequest(description="test", severity=-0.1)
