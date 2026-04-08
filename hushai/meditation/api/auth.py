"""微信 OAuth 认证与 JWT 签发。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.config import get_config
from hushai.meditation.db.models import User

WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def wx_login(code: str, session: AsyncSession) -> dict:
    cfg = get_config()
    params = {
        "appid": cfg.wx_appid,
        "secret": cfg.wx_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(WX_CODE2SESSION_URL, params=params)
        data = resp.json()
    errcode = data.get("errcode", 0)
    if errcode:
        raise RuntimeError(f"微信登录失败: {data.get('errmsg', '未知错误')} (errcode={errcode})")
    openid = data.get("openid", "")
    session_key = data.get("session_key", "")
    unionid = data.get("unionid")
    if not openid:
        raise RuntimeError("微信登录失败: 未获取到 openid")
    stmt = select(User).where(User.wx_openid == openid)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        user = User(wx_openid=openid, wx_unionid=unionid, wx_session_key=session_key)
        session.add(user)
        await session.flush()
    else:
        user.wx_session_key = session_key
        if unionid:
            user.wx_unionid = unionid
    token = _create_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
    }


def _create_token(user_id: str) -> str:
    cfg = get_config()
    expire = datetime.now(timezone.utc) + timedelta(minutes=cfg.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def verify_token(token: str) -> dict:
    cfg = get_config()
    try:
        payload = jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
        return payload
    except JWTError as e:
        raise RuntimeError(f"Token 无效: {e}") from None


async def get_current_user_id(token: str, session: AsyncSession) -> str:
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise RuntimeError("Token 中缺少用户信息")
    stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise RuntimeError("用户不存在或已禁用")
    return user_id


def extract_bearer_token(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization
