"""
core/config.py — Centralized application configuration using Pydantic Settings.
All secrets loaded from environment variables; never hardcoded.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: str = Field(default="")
    neo4j_database: str = Field(default="neo4j")
    neo4j_max_connection_pool_size: int = Field(default=50)
    neo4j_connection_timeout: int = Field(default=30)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: str = Field(default="")
    redis_ssl: bool = Field(default=False)
    redis_cache_ttl: int = Field(default=300)

    # Gemini AI
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-pro")
    gemini_max_tokens: int = Field(default=4096)
    gemini_timeout: int = Field(default=30)
    gemini_rate_limit_rpm: int = Field(default=60)

    # External Intelligence
    news_api_key: str = Field(default="")
    news_api_timeout: int = Field(default=15)
    weather_api_key: str = Field(default="")
    weather_api_timeout: int = Field(default=15)

    # Authentication — in-memory users seeded from environment
    admin_username: str = Field(default="")
    admin_password: str = Field(default="")
    analyst_username: str = Field(default="")
    analyst_password: str = Field(default="")
    viewer_username: str = Field(default="")
    viewer_password: str = Field(default="")

    jwt_secret: str = Field(default="")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # CORS
    cors_origins: str = Field(default="http://localhost:5173")

    # Rate Limiting
    rate_limit_default: str = Field(default="100/minute")
    rate_limit_auth: str = Field(default="20/minute")
    rate_limit_simulation: str = Field(default="10/minute")
    rate_limit_ai: str = Field(default="30/minute")

    # Request Limits
    max_request_body_size: int = Field(default=1_048_576)  # 1MB
    max_pagination_limit: int = Field(default=100)

    @model_validator(mode="after")
    def enforce_production_secrets(self) -> "Settings":
        if self.app_env.lower() != "production":
            return self
        problems: List[str] = []
        if not self.jwt_secret or self.jwt_secret.startswith("change_me"):
            problems.append("JWT_SECRET must be set to a strong secret (not a placeholder) in production")
        for label, password in (
            ("ADMIN_PASSWORD", self.admin_password),
            ("ANALYST_PASSWORD", self.analyst_password),
            ("VIEWER_PASSWORD", self.viewer_password),
        ):
            if not password:
                problems.append(f"{label} must be set in production")
        if problems:
            raise ValueError("Invalid production configuration: " + "; ".join(problems))
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()