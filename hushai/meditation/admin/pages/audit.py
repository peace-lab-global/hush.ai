"""审计日志页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import login_redirect, templates
from hushai.meditation.db.session import get_session

router = APIRouter(tags=["admin-web"])


@router.get("/audit-logs")
async def audit_logs_page(
    request: Request,
    page: int = 1,
    limit: int = 50,
    action: str | None = None,
    admin_username: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """审计日志页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    from hushai.meditation.db.models import AuditLog

    offset = (page - 1) * limit
    base = select(AuditLog)
    count_query = select(func.count()).select_from(AuditLog)

    if action:
        base = base.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)
    if admin_username:
        base = base.where(AuditLog.admin_username == admin_username)
        count_query = count_query.where(AuditLog.admin_username == admin_username)

    result = await session.execute(
        base.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    )
    logs = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit if total else 1

    result_usernames = await session.execute(select(AuditLog.admin_username).distinct())
    usernames = [row[0] for row in result_usernames.all()]

    result_actions = await session.execute(select(AuditLog.action).distinct())
    actions = [row[0] for row in result_actions.all()]

    return templates.TemplateResponse(
        request,
        "audit_logs.html",
        {
            "admin_user": admin_user,
            "logs": logs,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "action": action,
            "admin_username": admin_username,
            "usernames": usernames,
            "actions": actions,
            "limit": limit,
        },
    )
