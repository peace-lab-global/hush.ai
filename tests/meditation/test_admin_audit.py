"""管理后台审计日志工具测试。"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.audit import log_admin_action
from hushai.meditation.db.models import AuditLog


@pytest.mark.asyncio
async def test_log_admin_action_minimal(meditation_session: AsyncSession) -> None:
    """仅必填字段也应成功写入。"""
    log = await log_admin_action(
        session=meditation_session,
        admin_username="alice",
        action="user.delete",
        resource_type="user",
    )
    assert log.id  # 自动生成的 UUID
    assert log.admin_username == "alice"
    assert log.action == "user.delete"
    assert log.resource_type == "user"
    assert log.resource_id is None
    assert log.detail is None
    assert log.ip_address is None
    assert log.user_agent is None
    assert log.created_at is not None


@pytest.mark.asyncio
async def test_log_admin_action_full(meditation_session: AsyncSession) -> None:
    """所有字段都填时也应正确持久化。"""
    log = await log_admin_action(
        session=meditation_session,
        admin_username="bob",
        action="knowledge.import",
        resource_type="knowledge_item",
        resource_id="kg-42",
        detail="imported 17 markdown files",
        ip_address="10.0.0.1",
        user_agent="curl/8.0",
    )
    assert log.admin_username == "bob"
    assert log.resource_id == "kg-42"
    assert log.detail == "imported 17 markdown files"
    assert log.ip_address == "10.0.0.1"
    assert log.user_agent == "curl/8.0"


@pytest.mark.asyncio
async def test_log_admin_action_persists_to_session(meditation_session: AsyncSession) -> None:
    """flush 后记录应可被查询到。"""
    from sqlalchemy import select

    await log_admin_action(
        session=meditation_session,
        admin_username="carol",
        action="settings.update",
        resource_type="system_config",
    )
    stmt = select(AuditLog).where(AuditLog.admin_username == "carol")
    result = await meditation_session.execute(stmt)
    rows = list(result.scalars().all())
    assert len(rows) == 1
    assert rows[0].action == "settings.update"
