"""按 ID 加载已启用的技能文本，拼入系统提示。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.db.models import Skill

MAX_SKILLS_PER_MESSAGE = 8
MAX_SKILLS_IMPORT_BATCH = 100


async def get_skills_context_for_prompt(
    session: AsyncSession,
    skill_ids: list[str] | None,
) -> str:
    """获取技能上下文。如果 skill_ids 为 None，则获取所有已启用的技能。"""
    ordered_ids: list[str] | None = None
    if skill_ids is not None:
        if not skill_ids:
            return ""
        seen: set[str] = set()
        ordered_ids = []
        for sid in skill_ids:
            if sid in seen or len(ordered_ids) >= MAX_SKILLS_PER_MESSAGE:
                continue
            seen.add(sid)
            ordered_ids.append(sid)
        if not ordered_ids:
            return ""
        stmt = (
            select(Skill)
            .where(Skill.id.in_(ordered_ids), Skill.is_active.is_(True))
            .order_by(Skill.sort_order.asc(), Skill.name.asc())
        )
    else:
        stmt = (
            select(Skill)
            .where(Skill.is_active.is_(True))
            .order_by(Skill.sort_order.asc(), Skill.name.asc())
            .limit(MAX_SKILLS_PER_MESSAGE)
        )

    result = await session.execute(stmt)
    rows = list(result.scalars().all())

    if ordered_ids is not None:
        by_id = {s.id: s for s in rows}
        parts = [
            f"## {by_id[sid].name}\n{by_id[sid].content.strip()}"
            for sid in ordered_ids
            if sid in by_id
        ]
    else:
        parts = [f"## {s.name}\n{s.content.strip()}" for s in rows]

    if not parts:
        return ""
    return "\n\n".join(parts)
