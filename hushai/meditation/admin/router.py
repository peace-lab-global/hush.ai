"""管理后台路由。"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import (
    create_admin_token,
    get_admin_credentials,
    get_admin_from_request,
)
from hushai.meditation.config import get_config
from hushai.meditation.core.memory import get_user_memories
from hushai.meditation.db.models import Conversation, KnowledgeChunk, Memory, Message, User
from hushai.meditation.db.session import get_session

router = APIRouter(prefix="/admin", tags=["admin-web"])

# 设置模板目录
templates = Jinja2Templates(directory="hushai/meditation/admin/templates")

# 添加 tojson 过滤器
def tojson_filter(value, indent=None):
    return json.dumps(value, ensure_ascii=False, indent=indent)

templates.env.filters["tojson"] = tojson_filter


# 请求模型
class LoginRequest(BaseModel):
    username: str
    password: str


# 上下文处理器
async def get_stats_context(session: AsyncSession) -> dict:
    """获取统计信息。"""
    # 用户统计
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

    # 记忆统计
    memory_count = (await session.execute(select(func.count()).select_from(Memory))).scalar() or 0

    # 知识库统计
    knowledge_count = (
        await session.execute(select(func.count()).select_from(KnowledgeChunk))
    ).scalar() or 0

    return {
        "user_count": user_count,
        "active_users": active_users,
        "conv_count": conv_count,
        "msg_count": msg_count,
        "memory_count": memory_count,
        "knowledge_count": knowledge_count,
    }


# 页面路由
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """登录页面。"""
    # 如果已登录，跳转到仪表盘
    if get_admin_from_request(request):
        return RedirectResponse(url="/admin/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """登录处理。"""
    creds = get_admin_credentials()
    if username != creds["username"] or password != creds["password"]:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "用户名或密码错误"}, status_code=401
        )

    token = create_admin_token(username)
    response = RedirectResponse(url="/admin/", status_code=302)
    response.set_cookie(
        "admin_token",
        token,
        httponly=True,
        max_age=86400,  # 24小时
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    """登出处理。"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_token")
    return response


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)):
    """仪表盘页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    stats = await get_stats_context(session)

    # 获取最近注册用户
    recent_users_result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(5)
    )
    recent_users = list(recent_users_result.scalars().all())

    # 获取最近对话
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
        "dashboard.html",
        {
            "request": request,
            "admin_user": admin_user,
            **stats,
            "recent_users": recent_users,
            "recent_conversations": recent_conversations,
        },
    )


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
        return RedirectResponse(url="/admin/login", status_code=302)

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
        "users.html",
        {
            "request": request,
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
        return RedirectResponse(url="/admin/login", status_code=302)

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
        "user_detail.html",
        {
            "request": request,
            "admin_user": admin_user,
            "user": user,
            "conv_count": conv_count,
            "msg_count": msg_count,
            "memories": memories,
            "conversations": conversations,
        },
    )


@router.get("/conversations", response_class=HTMLResponse)
async def conversations_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    user_id: str = None,
    session: AsyncSession = Depends(get_session),
):
    """对话管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

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
        "conversations.html",
        {
            "request": request,
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
        return RedirectResponse(url="/admin/login", status_code=302)

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
        "conversation_detail.html",
        {
            "request": request,
            "admin_user": admin_user,
            "conversation": conversation,
            "nickname": nickname,
            "user_id": user_id,
            "messages": messages,
        },
    )


@router.get("/memories", response_class=HTMLResponse)
async def memories_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    user_id: str = None,
    category: str = None,
    session: AsyncSession = Depends(get_session),
):
    """记忆管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    offset = (page - 1) * limit

    # 构建查询
    base_query = select(Memory, User.nickname).join(User, Memory.user_id == User.id)
    count_query = select(func.count()).select_from(Memory)

    if user_id:
        base_query = base_query.where(Memory.user_id == user_id)
        count_query = count_query.where(Memory.user_id == user_id)

    if category:
        base_query = base_query.where(Memory.category == category)
        count_query = count_query.where(Memory.category == category)

    # 执行查询
    result = await session.execute(
        base_query.order_by(Memory.created_at.desc()).offset(offset).limit(limit)
    )
    memories = [{"memory": row[0], "nickname": row[1]} for row in result.all()]
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit

    # 获取用户列表
    users_result = await session.execute(select(User).order_by(User.created_at.desc()).limit(100))
    users = list(users_result.scalars().all())

    # 获取分类列表
    category_result = await session.execute(
        select(Memory.category).distinct().order_by(Memory.category)
    )
    categories = [row[0] for row in category_result.all()]

    return templates.TemplateResponse(
        "memories.html",
        {
            "request": request,
            "admin_user": admin_user,
            "memories": memories,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "user_id": user_id,
            "category": category,
            "users": users,
            "categories": categories,
            "limit": limit,
        },
    )


@router.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: str = "",
    session: AsyncSession = Depends(get_session),
):
    """知识库管理页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    offset = (page - 1) * limit

    # 构建查询
    base_query = select(KnowledgeChunk)
    count_query = select(func.count()).select_from(KnowledgeChunk)

    if search:
        base_query = base_query.where(
            (KnowledgeChunk.title.ilike(f"%{search}%"))
            | (KnowledgeChunk.content.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (KnowledgeChunk.title.ilike(f"%{search}%"))
            | (KnowledgeChunk.content.ilike(f"%{search}%"))
        )

    # 执行查询
    result = await session.execute(
        base_query.order_by(KnowledgeChunk.created_at.desc()).offset(offset).limit(limit)
    )
    knowledge_items = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit

    return templates.TemplateResponse(
        "knowledge.html",
        {
            "request": request,
            "admin_user": admin_user,
            "knowledge_items": knowledge_items,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "search": search,
            "limit": limit,
        },
    )


@router.get("/knowledge/{item_id}", response_class=HTMLResponse)
async def knowledge_detail_page(
    request: Request,
    item_id: str,
    session: AsyncSession = Depends(get_session),
):
    """知识库详情页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    # 获取知识条目
    result = await session.execute(select(KnowledgeChunk).where(KnowledgeChunk.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")

    return templates.TemplateResponse(
        "knowledge_detail.html",
        {
            "request": request,
            "admin_user": admin_user,
            "item": item,
        },
    )


@router.get("/knowledge-import", response_class=HTMLResponse)
async def knowledge_import_page(
    request: Request,
):
    """知识库导入页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    return templates.TemplateResponse(
        "knowledge_import.html",
        {
            "request": request,
            "admin_user": admin_user,
        },
    )


# API 路由（供前端 JS 调用）
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


@router.delete("/api/memories/{memory_id}")
async def delete_memory(
    request: Request,
    memory_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除记忆。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="记忆不存在")

    await session.delete(memory)
    await session.commit()

    return {"success": True}


@router.delete("/api/knowledge/{item_id}")
async def delete_knowledge(
    request: Request,
    item_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除知识条目。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(KnowledgeChunk).where(KnowledgeChunk.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")

    await session.delete(item)
    await session.commit()

    return {"success": True}


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
):
    """系统设置页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return RedirectResponse(url="/admin/login", status_code=302)

    config = get_config()

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "admin_user": admin_user,
            "config": config,
        },
    )
