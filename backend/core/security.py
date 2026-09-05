"""
core/security.py — Authentication, authorization, and security utilities.

- JWT token creation/validation with short-lived access tokens
- Role-based access control (admin, analyst, viewer)
- Password hashing with bcrypt (via passlib)
- In-memory demo users seeded from environment variables (never hardcoded)
- Never stores plaintext passwords
- Never logs tokens or secrets
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import lru_cache
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from core import get_settings
from core.exceptions import AuthenticationError, AuthorizationError
from core.logging import get_logger, log_security_event

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer_scheme = HTTPBearer(auto_error=False)


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class TokenData(BaseModel):
    user_id: str
    username: str
    role: UserRole
    exp: datetime


class UserInfo(BaseModel):
    user_id: str
    username: str
    role: UserRole


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@lru_cache(maxsize=1)
def get_demo_users() -> dict:
    """In-memory users seeded from settings. Empty when credentials are unset."""
    settings = get_settings()
    users: dict = {}
    entries = (
        (UserRole.ADMIN, "admin_username", "admin_password"),
        (UserRole.ANALYST, "analyst_username", "analyst_password"),
        (UserRole.VIEWER, "viewer_username", "viewer_password"),
    )
    for index, (role, username_attr, password_attr) in enumerate(entries, start=1):
        username = getattr(settings, username_attr)
        password = getattr(settings, password_attr)
        if not username or not password:
            continue
        users[username] = {
            "user_id": f"usr_{index:03d}",
            "username": username,
            "password_hash": hash_password(password),
            "role": role,
        }
    return users


def create_access_token(user: UserInfo, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role.value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user: UserInfo) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": user.user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenData:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return TokenData(
            user_id=payload["sub"],
            username=payload.get("username", ""),
            role=UserRole(payload.get("role", "viewer")),
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except JWTError as e:
        raise AuthenticationError("Invalid or expired token")


def authenticate_user(username: str, password: str) -> Optional[UserInfo]:
    user_data = get_demo_users().get(username)
    if not user_data:
        hash_password("dummy_to_prevent_timing")
        return None
    if not verify_password(password, user_data["password_hash"]):
        return None
    return UserInfo(
        user_id=user_data["user_id"],
        username=user_data["username"],
        role=user_data["role"],
    )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> UserInfo:
    if credentials is None:
        raise AuthenticationError("Authentication required")

    token_data = decode_token(credentials.credentials)

    if token_data.exp < datetime.now(timezone.utc):
        raise AuthenticationError("Token has expired")

    return UserInfo(
        user_id=token_data.user_id,
        username=token_data.username,
        role=token_data.role,
    )


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[UserInfo]:
    if credentials is None:
        return None
    try:
        return await get_current_user(request, credentials)
    except AuthenticationError:
        return None


def require_role(*allowed_roles: UserRole):
    async def role_checker(
        current_user: UserInfo = Depends(get_current_user),
    ) -> UserInfo:
        if current_user.role not in allowed_roles:
            log_security_event(
                logger,
                "authorization_failure",
                f"User {current_user.username} denied access (role={current_user.role.value})",
                user_id=current_user.user_id,
                details={"required_roles": [r.value for r in allowed_roles]},
            )
            raise AuthorizationError("Insufficient permissions for this operation")
        return current_user
    return role_checker