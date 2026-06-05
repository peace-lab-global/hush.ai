"""开发模式登录 & 静态页面路由。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from hushai.meditation.api.auth import _create_access_token, _create_refresh_token, _hash_token
from hushai.meditation.db.models import User
from hushai.meditation.db.session import get_session_factory
from hushai.meditation.schemas import LoginResponse

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    from pathlib import Path

    html_path = Path(__file__).parent.parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@router.post("/api/auth/dev-login", response_model=LoginResponse)
async def dev_login(request: Request):

    body = await request.json()
    nickname = body.get("nickname", "冥想者")[:20]
    factory = get_session_factory()
    async with factory() as session:
        user = User(
            id=str(uuid.uuid4()),
            nickname=nickname,
            wx_openid="dev_" + str(uuid.uuid4())[:12],
        )
        session.add(user)
        await session.flush()
        user_id = user.id

        access_token, expires_in = _create_access_token(user_id)
        refresh_token, _ = _create_refresh_token()
        user.refresh_token_hash = _hash_token(refresh_token)

        await session.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user_id,
        nickname=nickname,
        expires_in=expires_in,
    )
