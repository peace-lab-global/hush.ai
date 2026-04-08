"""登录 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import wx_login
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import ErrorResponse, LoginResponse, WxLoginRequest

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
