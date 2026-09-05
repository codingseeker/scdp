"""
api/v1/auth.py — Authentication endpoints.

- Login with username/password
- JWT token issuance
- Token refresh
- Rate limited to prevent brute force
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from core import get_settings
from core.exceptions import AuthenticationError
from core.logging import get_logger, log_security_event
from core.security import (
    UserInfo,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, body: LoginRequest):
    user = authenticate_user(body.username, body.password)
    req_id = getattr(request.state, "request_id", None)
    if not user:
        from core.audit import record_audit_event
        record_audit_event(
            actor=body.username,
            action="login",
            resource="auth",
            result="FAILURE",
            request_id=req_id,
            details={"ip": request.client.host if request.client else None},
        )
        log_security_event(
            logger,
            "authentication_failure",
            f"Failed login attempt for username: {body.username}",
            request_id=req_id,
            ip_address=request.client.host if request.client else None,
        )
        raise AuthenticationError("Invalid username or password")

    from core.audit import record_audit_event
    record_audit_event(
        actor=user.username,
        action="login",
        resource="auth",
        result="SUCCESS",
        request_id=req_id,
        details={"role": user.role.value, "ip": request.client.host if request.client else None},
    )

    settings = get_settings()
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    logger.info(f"Successful login: {user.username} (role={user.role.value})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    token_data = decode_token(body.refresh_token)
    user = UserInfo(
        user_id=token_data.user_id,
        username=token_data.username,
        role=token_data.role,
    )
    settings = get_settings()
    new_access = create_access_token(user)
    new_refresh = create_refresh_token(user)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role.value,
    )
