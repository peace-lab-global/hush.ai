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
    if skill_ids is not None:
        if not skill_ids:
            return ""
        seen: set[str] = set()
        ordered: list[str] = []
        for sid in skill_ids:
            if sid in seen or len(ordered) >= MAX_SKILLS_PER_MESSAGE:
                continue
            seen.add(sid)
            ordered.append(sid)
        if not ordered:
            return ""
        stmt = (
            select(Skill)
            .where(Skill.id.in_(ordered), Skill.is_active.is_(True))
            .order_by(Skill.sort_order.asc(), Skill.name.asc())
        )
    else:
        # 自动挂载所有已启用的技能
        stmt = (
            select(Skill)
            .where(Skill.is_active.is_(True))
            .order_by(Skill.sort_order.asc(), Skill.name.asc())
            .limit(MAX_SKILLS_PER_MESSAGE)
        )

    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    
    if skill_ids is not None:
        by_id = {s.id: s for s in rows}
        parts: list[str] = []
        for sid in ordered:
            s = by_id.get(sid)
            if not s:
                continue
            parts.append(f"## {s.name}\n{s.content.strip()}")
    else:
        parts = [f"## {s.name}\n{s.content.strip()}" for s in rows]

    if not parts:
        return ""
    return "\n\n".join(parts)
