"""数据导出页面（CSV/Excel）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.export import get_export_response
from hushai.meditation.db.models import Conversation, KnowledgeChunk, Memory, User
from hushai.meditation.db.session import get_session

router = APIRouter(tags=["admin-web"])


@router.get("/export/conversations")
async def export_conversations(
    request: Request,
    user_id: str | None = None,
    format: str = "csv",
    session: AsyncSession = Depends(get_session),
):
    """导出对话记录为 CSV/Excel。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    base_query = select(Conversation, User.nickname).join(User, Conversation.user_id == User.id)
    if user_id:
        base_query = base_query.where(Conversation.user_id == user_id)

    result = await session.execute(base_query.order_by(Conversation.updated_at.desc()))
    rows = result.all()

    data = []
    for row in rows:
        conv, nickname = row
        data.append(
            {
                "用户昵称": nickname or "未命名",
                "用户ID": conv.user_id,
                "对话标题": conv.title or "无标题",
                "对话ID": conv.id,
                "创建时间": conv.created_at,
                "更新时间": conv.updated_at,
                "状态": "进行中" if conv.is_active else "已结束",
            }
        )

    return get_export_response(data, "conversations", format)


@router.get("/export/audit-logs")
async def export_audit_logs(
    request: Request,
    action: str | None = None,
    admin_username: str | None = None,
    format: str = "csv",
    session: AsyncSession = Depends(get_session),
):
    """导出审计日志为 CSV/Excel。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    from hushai.meditation.db.models import AuditLog

    base = select(AuditLog)
    if action:
        base = base.where(AuditLog.action == action)
    if admin_username:
        base = base.where(AuditLog.admin_username == admin_username)

    result = await session.execute(base.order_by(AuditLog.created_at.desc()))
    logs = list(result.scalars().all())

    data = []
    for log in logs:
        data.append(
            {
                "时间": log.created_at,
                "管理员": log.admin_username,
                "操作": log.action,
                "资源类型": log.resource_type,
                "资源ID": log.resource_id or "",
                "详情": log.detail or "",
                "IP地址": log.ip_address or "",
            }
        )

    return get_export_response(data, "audit_logs", format)


@router.get("/export/users")
async def export_users(
    request: Request,
    search: str = "",
    format: str = "csv",
    session: AsyncSession = Depends(get_session),
):
    """导出用户列表为 CSV/Excel。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    base_query = select(User)
    if search:
        base_query = base_query.where(
            (User.nickname.ilike(f"%{search}%")) | (User.wx_openid.ilike(f"%{search}%"))
        )

    result = await session.execute(base_query.order_by(User.created_at.desc()))
    users = list(result.scalars().all())

    data = []
    for user in users:
        data.append(
            {
                "昵称": user.nickname or "未命名",
                "用户ID": user.id,
                "OpenID": user.wx_openid or "",
                "注册时间": user.created_at,
                "状态": "正常" if user.is_active else "已禁用",
            }
        )

    return get_export_response(data, "users", format)


@router.get("/export/memories")
async def export_memories(
    request: Request,
    user_id: str | None = None,
    category: str | None = None,
    format: str = "csv",
    session: AsyncSession = Depends(get_session),
):
    """导出记忆列表为 CSV/Excel。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    base_query = select(Memory, User.nickname).join(User, Memory.user_id == User.id)
    if user_id:
        base_query = base_query.where(Memory.user_id == user_id)
    if category:
        base_query = base_query.where(Memory.category == category)

    result = await session.execute(base_query.order_by(Memory.created_at.desc()))
    rows = result.all()

    data = []
    for row in rows:
        mem, nickname = row
        data.append(
            {
                "用户昵称": nickname or "未命名",
                "用户ID": mem.user_id,
                "分类": mem.category,
                "内容": mem.content,
                "摘要": mem.summary or "",
                "重要度": mem.importance,
                "状态": mem.status or "",
                "创建时间": mem.created_at,
            }
        )

    return get_export_response(data, "memories", format)


@router.get("/export/knowledge")
async def export_knowledge(
    request: Request,
    search: str = "",
    format: str = "csv",
    session: AsyncSession = Depends(get_session),
):
    """导出知识库为 CSV/Excel。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    base_query = select(KnowledgeChunk)
    if search:
        base_query = base_query.where(
            (KnowledgeChunk.title.ilike(f"%{search}%"))
            | (KnowledgeChunk.content.ilike(f"%{search}%"))
        )

    result = await session.execute(base_query.order_by(KnowledgeChunk.created_at.desc()))
    items = list(result.scalars().all())

    data = []
    for item in items:
        data.append(
            {
                "标题": item.title or "无标题",
                "内容": item.content,
                "标签": ", ".join(item.tags) if item.tags else "",
                "来源": item.source or "",
                "创建时间": item.created_at,
            }
        )

    return get_export_response(data, "knowledge", format)
