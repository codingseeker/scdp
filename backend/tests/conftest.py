"""
tests/conftest.py — Shared pytest configuration.

Seeds deterministic, password-based demo users into the environment before the
application is imported so tests do not depend on a developer's local `.env`.
"""
import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("NEO4J_PASSWORD", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("JWT_SECRET", "test_only_jwt_secret_that_is_long_enough_32")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin123")
os.environ.setdefault("ANALYST_USERNAME", "analyst")
os.environ.setdefault("ANALYST_PASSWORD", "analyst123")
os.environ.setdefault("VIEWER_USERNAME", "viewer")
os.environ.setdefault("VIEWER_PASSWORD", "viewer123")
