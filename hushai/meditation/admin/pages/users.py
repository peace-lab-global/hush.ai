"""用户管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.core.memory import get_user_memories
from hushai.meditation.db.models import Conversation, Message, User

router = APIRouter(tags=["admin-web"])


@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: str = "",
    session: AsyncSession = Depends(get_session),
):
    """用户管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit

    # 构建查询
    base_query = select(User)
    count_query = select(func.count()).select_from(User)

    if search:
        base_query = base_query.where(
            (User.nickname.ilike(f"%{search}%")) | (User.wx_openid.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (User.nickname.ilike(f"%{search}%")) | (User.wx_openid.ilike(f"%{search}%"))
        )

    # 执行查询
    result = await session.execute(
        base_query.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit

    return templates.TemplateResponse(
        request,
        "users.html",
        {
            "admin_user": admin_user,
            "users": users,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "search": search,
            "limit": limit,
        },
    )


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail_page(
    request: Request,
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """用户详情页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    # 获取用户信息
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取统计
    conv_count = (
        await session.execute(
            select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        )
    ).scalar() or 0

    msg_count = (
        await session.execute(
            select(func.count())
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
        )
    ).scalar() or 0

    # 获取记忆
    memories, _ = await get_user_memories(session, user_id, limit=20)

    # 获取对话列表
    conv_result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    )
    conversations = list(conv_result.scalars().all())

    return templates.TemplateResponse(
        request,
        "user_detail.html",
        {
            "admin_user": admin_user,
            "user": user,
            "conv_count": conv_count,
            "msg_count": msg_count,
            "memories": memories,
            "conversations": conversations,
        },
    )


@router.post("/api/users/{user_id}/toggle-status")
async def toggle_user_status(
    request: Request,
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """切换用户状态。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = not user.is_active
    await session.commit()

    return {"success": True, "is_active": user.is_active}
