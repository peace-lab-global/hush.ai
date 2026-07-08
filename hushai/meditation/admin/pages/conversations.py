"""对话管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import (
    BatchDeleteRequest,
    get_session,
    login_redirect,
    templates,
)
from hushai.meditation.db.models import Conversation, Message, User

router = APIRouter(tags=["admin-web"])


@router.get("/conversations", response_class=HTMLResponse)
async def conversations_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    user_id: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """对话管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit

    # 构建查询
    base_query = select(Conversation, User.nickname).join(User, Conversation.user_id == User.id)
    count_query = select(func.count()).select_from(Conversation)

    if user_id:
        base_query = base_query.where(Conversation.user_id == user_id)
        count_query = count_query.where(Conversation.user_id == user_id)

    # 执行查询
    result = await session.execute(
        base_query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)
    )
    conversations = [{"conv": row[0], "nickname": row[1]} for row in result.all()]
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit

    # 获取用户列表（用于筛选）
    users_result = await session.execute(select(User).order_by(User.created_at.desc()).limit(100))
    users = list(users_result.scalars().all())

    return templates.TemplateResponse(
        request,
        "conversations.html",
        {
            "admin_user": admin_user,
            "conversations": conversations,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "user_id": user_id,
            "users": users,
            "limit": limit,
        },
    )


@router.get("/conversations/{conversation_id}", response_class=HTMLResponse)
async def conversation_detail_page(
    request: Request,
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
):
    """对话详情页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    # 获取对话
    result = await session.execute(
        select(Conversation, User.nickname, User.id)
        .join(User, Conversation.user_id == User.id)
        .where(Conversation.id == conversation_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="对话不存在")

    conversation, nickname, user_id = row

    # 获取消息
    msg_result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = list(msg_result.scalars().all())

    return templates.TemplateResponse(
        request,
        "conversation_detail.html",
        {
            "admin_user": admin_user,
            "conversation": conversation,
            "nickname": nickname,
            "user_id": user_id,
            "messages": messages,
        },
    )


@router.post("/api/conversations/batch-delete")
async def batch_delete_conversations(
    request: Request,
    req: BatchDeleteRequest,
    session: AsyncSession = Depends(get_session),
):
    """批量删除对话（软删除，标记 is_active=False）。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    if not req.ids:
        return {"deleted": 0}

    result = await session.execute(select(Conversation).where(Conversation.id.in_(req.ids)))
    conversations = list(result.scalars().all())
    count = 0
    for conv in conversations:
        conv.is_active = False
        count += 1
    await session.commit()
    return {"deleted": count}
