"""管理后台页面共用基础设施：模板、鉴权依赖、统计上下文。

抽离自原 1667 行的 ``admin/router.py``，供各资源页面复用，消除 36 处手写
``get_admin_from_request`` + redirect/HTTPException 的鉴权样板。
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.db.models import Conversation, KnowledgeChunk, Memory, Message, Skill, User
from hushai.meditation.db.session import get_session

# 模板目录：相对 __file__，避免依赖进程 cwd（否则从非项目根启动时管理后台 500）
_ADMIN_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_ADMIN_TEMPLATES_DIR))


def tojson_filter(value, indent=None):
    return json.dumps(value, ensure_ascii=False, indent=indent)


templates.env.filters["tojson"] = tojson_filter


class LoginRequest(BaseModel):
    username: str
    password: str


class BatchDeleteRequest(BaseModel):
    ids: list[str]


async def get_stats_context(session: AsyncSession) -> dict:
    """仪表盘统计：各资源总数。"""
    user_count = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
    active_users = (
        await session.execute(
            select(func.count()).select_from(User).where(User.is_active.is_(True))
        )
    ).scalar() or 0
    conv_count = (
        await session.execute(select(func.count()).select_from(Conversation))
    ).scalar() or 0
    msg_count = (await session.execute(select(func.count()).select_from(Message))).scalar() or 0
    memory_count = (await session.execute(select(func.count()).select_from(Memory))).scalar() or 0
    knowledge_count = (
        await session.execute(select(func.count()).select_from(KnowledgeChunk))
    ).scalar() or 0
    skill_count = (await session.execute(select(func.count()).select_from(Skill))).scalar() or 0

    return {
        "user_count": user_count,
        "active_users": active_users,
        "conv_count": conv_count,
        "msg_count": msg_count,
        "memory_count": memory_count,
        "knowledge_count": knowledge_count,
        "skill_count": skill_count,
    }


async def require_admin_page(request: Request) -> str:
    """页面路由鉴权：未登录重定向到登录页（返回占位 str，实际重定向会被路由处理）。

    注意：FastAPI 依赖无法直接返回 RedirectResponse 给路由函数，因此页面路由
    仍保留显式 ``if not admin_user: return RedirectResponse(...)``。本依赖用于
    统一获取 admin_user 身份，避免重复样板。
    """
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")
    return admin_user


async def require_admin_api(request: Request) -> str:
    """API 路由鉴权：未登录抛 401。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")
    return admin_user


def login_redirect() -> RedirectResponse:
    """统一的未登录重定向响应。"""
    return RedirectResponse(url="/admin/login", status_code=302)


# 公共导出，便于页面文件按需引用 session 依赖
__all__ = [
    "BatchDeleteRequest",
    "LoginRequest",
    "get_session",
    "get_stats_context",
    "login_redirect",
    "require_admin_api",
    "require_admin_page",
    "templates",
]
