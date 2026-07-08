"""管理员认证相关功能。"""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

import bcrypt
from fastapi import HTTPException, Request
from jose import JWTError, jwt  # type: ignore[import-untyped]
from sqlalchemy import select

from hushai.meditation.config import get_config
from hushai.meditation.db.models import AdminUser
from hushai.meditation.db.session import get_session_factory

CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_COOKIE_NAME = "admin_csrf_token"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


async def verify_admin_credentials_db(username: str, password: str) -> AdminUser | None:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(AdminUser).where(
            AdminUser.username == username,
            AdminUser.is_active.is_(True),
        )
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()
        if admin and verify_password(password, admin.password_hash):
            return admin
        return None


async def get_admin_user_by_username(username: str) -> AdminUser | None:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(AdminUser).where(
            AdminUser.username == username,
            AdminUser.is_active.is_(True),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


def get_admin_credentials() -> dict[str, str]:
    return {
        "username": os.environ.get("MEDITATION_ADMIN_USERNAME", "admin"),
        "password": os.environ.get("MEDITATION_ADMIN_PASSWORD", "admin"),
    }


def create_admin_token(username: str) -> str:
    cfg = get_config()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "is_admin": True,
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)  # type: ignore[no-any-return]


def verify_admin_token(token: str) -> dict:
    cfg = get_config()
    try:
        payload = jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
        if not payload.get("is_admin"):
            raise JWTError("Not an admin token")
        return payload  # type: ignore[no-any-return]
    except JWTError as e:
        raise RuntimeError(f"Token 无效: {e}") from None


def get_admin_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get("admin_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]

    if not token:
        return None

    try:
        payload = verify_admin_token(token)
        return payload.get("sub")
    except RuntimeError:
        return None


def require_admin(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        admin_user = get_admin_from_request(request)
        if not admin_user:
            raise HTTPException(status_code=401, detail="需要管理员登录")
        request.state.admin_user = admin_user  # type: ignore[attr-defined]
        return await func(request, *args, **kwargs)

    return wrapper


async def init_default_admin() -> bool:
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(AdminUser)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return False

        creds = get_admin_credentials()
        admin = AdminUser(
            username=creds["username"],
            password_hash=hash_password(creds["password"]),
            display_name="管理员",
        )
        session.add(admin)
        await session.commit()
        return True


def generate_csrf_token() -> str:
    """生成 CSRF 令牌。"""
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def get_csrf_from_request(request: Request) -> str | None:
    """从请求中获取 CSRF 令牌。"""
    return request.cookies.get(CSRF_TOKEN_COOKIE_NAME)


def set_csrf_cookie(response, csrf_token: str) -> None:
    """设置 CSRF 令牌到响应 cookie。

    ``secure`` 跟随配置：开发环境（HTTP）不启用以免本地无法写入，生产
    （HTTPS）启用。CSRF token 需对前端 JS 可见（用于读取后放入 X-CSRF-Token），
    故 ``httponly=False``。
    """
    cfg = get_config()
    response.set_cookie(
        CSRF_TOKEN_COOKIE_NAME,
        csrf_token,
        httponly=False,
        max_age=86400,
        samesite="strict",
        secure=not cfg.debug,
    )


def verify_csrf_token(request: Request) -> bool:
    """验证 CSRF 令牌。"""
    cookie_token = get_csrf_from_request(request)
    if not cookie_token:
        return False
    header_token = request.headers.get("X-CSRF-Token", "")
    return cookie_token == header_token


def require_csrf(func):
    """CSRF 保护装饰器。"""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if request.method in ("POST", "PUT", "DELETE", "PATCH") and not verify_csrf_token(request):
            raise HTTPException(status_code=403, detail="CSRF 验证失败")
        return await func(request, *args, **kwargs)

    return wrapper
