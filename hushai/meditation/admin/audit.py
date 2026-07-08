"""审计日志工具。"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.db.models import AuditLog


async def log_admin_action(
    session: AsyncSession,
    admin_username: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    log = AuditLog(
        admin_username=admin_username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    session.add(log)
    await session.flush()
    return log
