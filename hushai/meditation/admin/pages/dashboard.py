"""仪表盘页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_stats_context, login_redirect, templates
from hushai.meditation.db.models import Conversation, User
from hushai.meditation.db.session import get_session

router = APIRouter(tags=["admin-web"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)):
    """仪表盘页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    stats = await get_stats_context(session)

    recent_users_result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(5)
    )
    recent_users = list(recent_users_result.scalars().all())

    recent_conv_result = await session.execute(
        select(Conversation, User.nickname)
        .join(User, Conversation.user_id == User.id)
        .order_by(Conversation.created_at.desc())
        .limit(5)
    )
    recent_conversations = [
        {"conv": row[0], "nickname": row[1]} for row in recent_conv_result.all()
    ]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "admin_user": admin_user,
            **stats,
            "recent_users": recent_users,
            "recent_conversations": recent_conversations,
        },
    )
