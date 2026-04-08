"""管理员认证相关功能。"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

from fastapi import HTTPException, Request
from jose import JWTError, jwt

from hushai.meditation.config import get_config


# 管理员账号配置（从环境变量读取）
def get_admin_credentials() -> dict[str, str]:
    """获取管理员账号配置。"""
    return {
        "username": os.environ.get("MEDITATION_ADMIN_USERNAME", "admin"),
        "password": os.environ.get("MEDITATION_ADMIN_PASSWORD", "admin"),
    }


def create_admin_token(username: str) -> str:
    """创建管理员 JWT Token。"""
    cfg = get_config()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)  # 24小时有效期
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "is_admin": True,
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def verify_admin_token(token: str) -> dict:
    """验证管理员 JWT Token。"""
    cfg = get_config()
    try:
        payload = jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
        if not payload.get("is_admin"):
            raise JWTError("Not an admin token")
        return payload
    except JWTError as e:
        raise RuntimeError(f"Token 无效: {e}") from None


def get_admin_from_request(request: Request) -> Optional[str]:
    """从请求中获取管理员用户名。"""
    # 先尝试从 Cookie 获取
    token = request.cookies.get("admin_token")
    if not token:
        # 再尝试从 Header 获取
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
    """装饰器：要求管理员登录。"""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        admin_user = get_admin_from_request(request)
        if not admin_user:
            raise HTTPException(status_code=401, detail="需要管理员登录")
        request.state.admin_user = admin_user
        return await func(request, *args, **kwargs)

    return wrapper
