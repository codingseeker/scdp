"""
schemas/auth.py — Authentication and authorization schemas.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=200)

    model_config = {"extra": "forbid"}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

    model_config = {"extra": "forbid"}


class UserResponse(BaseModel):
    user_id: str
    username: str
    role: str
