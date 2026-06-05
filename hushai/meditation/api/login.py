"""登录 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import refresh_access_token, wx_login
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    ErrorResponse,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    WxLoginRequest,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/wx-login",
    response_model=LoginResponse,
    responses={400: {"model": ErrorResponse}},
)
async def wx_login_endpoint(
    req: WxLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    try:
        result = await wx_login(req.code, session)
        await session.commit()
        return LoginResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def refresh_token_endpoint(
    req: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
) -> RefreshTokenResponse:
    try:
        result = await refresh_access_token(req.refresh_token, session)
        await session.commit()
        return RefreshTokenResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None
