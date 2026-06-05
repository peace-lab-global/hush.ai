"""微信 OAuth 认证与 JWT 签发。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets

import bcrypt
import httpx
from jose import JWTError, jwt  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.config import get_config
from hushai.meditation.db.models import User

WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
REFRESH_TOKEN_EXPIRE_DAYS = 30


def _hash_token(token: str) -> str:
    return bcrypt.hashpw(token.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_token_hash(token: str, token_hash: str) -> bool:
    return bcrypt.checkpw(token.encode("utf-8"), token_hash.encode("utf-8"))


def _create_access_token(user_id: str) -> tuple[str, int]:
    cfg = get_config()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    token = jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)
    return token, ACCESS_TOKEN_EXPIRE_MINUTES


def _create_refresh_token() -> tuple[str, int]:
    token = secrets.token_urlsafe(32)
    return token, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600


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

    access_token, expires_in = _create_access_token(user.id)
    refresh_token, _ = _create_refresh_token()
    user.refresh_token_hash = _hash_token(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
        "expires_in": expires_in,
    }


def _create_token(user_id: str) -> str:
    cfg = get_config()
    expire = datetime.now(timezone.utc) + timedelta(minutes=cfg.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)  # type: ignore[no-any-return]


def verify_token(token: str) -> dict:
    cfg = get_config()
    try:
        payload = jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
        return payload  # type: ignore[no-any-return]
    except JWTError as e:
        raise RuntimeError(f"Token 无效: {e}") from None


async def get_current_user_id(token: str, session: AsyncSession) -> str:
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise RuntimeError("Token 中缺少用户信息")
    stmt = select(User).where(User.id == str(user_id), User.is_active.is_(True))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise RuntimeError("用户不存在或已禁用")
    return str(user_id)


async def refresh_access_token(refresh_token: str, session: AsyncSession) -> dict:
    stmt = select(User).where(
        User.refresh_token_hash.isnot(None),
        User.is_active.is_(True),
    )
    result = await session.execute(stmt)
    user = None
    for u in result.scalars().all():
        if u.refresh_token_hash and _verify_token_hash(refresh_token, u.refresh_token_hash):
            user = u
            break

    if not user:
        raise RuntimeError("Refresh token 无效或已过期")

    access_token, expires_in = _create_access_token(user.id)
    new_refresh_token, refresh_expires_in = _create_refresh_token()
    user.refresh_token_hash = _hash_token(new_refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


def extract_bearer_token(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization
