"""微信 OAuth 认证与 JWT 签发。"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

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

# Access token 声明的类型，verify_token 会强制校验，防止未来引入 refresh JWT
# 时发生类型混淆。
ACCESS_TOKEN_TYPE = "access"


def _hash_token(token: str) -> str:
    return bcrypt.hashpw(token.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_token_hash(token: str, token_hash: str) -> bool:
    return bcrypt.checkpw(token.encode("utf-8"), token_hash.encode("utf-8"))


def _token_selector(token: str) -> str:
    """refresh token 的 SHA-256 hex。

    非密钥，仅用于在 DB 中 O(1) 定位「持有该 token 的用户」，再用 bcrypt
    哈希做最终校验。避免对所有用户逐行 bcrypt 比对（DoS 风险）。
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _create_access_token(user_id: str) -> tuple[str, int]:
    cfg = get_config()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": ACCESS_TOKEN_TYPE,
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
    user.refresh_token_selector = _token_selector(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
        "expires_in": expires_in,
    }


def verify_token(token: str) -> dict:
    """校验并解码 access token。强制要求 token 类型为 access。"""
    cfg = get_config()
    try:
        payload = jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
    except JWTError as e:
        raise RuntimeError(f"Token 无效: {e}") from None
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise RuntimeError("Token 类型错误")
    return payload  # type: ignore[no-any-return]


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
    """用 refresh token 换取新的 access/refresh token。

    通过 ``refresh_token_selector``（token 的 SHA-256）O(1) 定位用户，
    再用 bcrypt 校验原 token，避免逐行 bcrypt 比对的 DoS 风险。
    """
    selector = _token_selector(refresh_token)
    stmt = select(User).where(
        User.refresh_token_selector == selector,
        User.is_active.is_(True),
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.refresh_token_hash:
        raise RuntimeError("Refresh token 无效或已过期")

    if not _verify_token_hash(refresh_token, user.refresh_token_hash):
        raise RuntimeError("Refresh token 无效或已过期")

    access_token, expires_in = _create_access_token(user.id)
    new_refresh_token, _ = _create_refresh_token()
    user.refresh_token_hash = _hash_token(new_refresh_token)
    user.refresh_token_selector = _token_selector(new_refresh_token)

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
