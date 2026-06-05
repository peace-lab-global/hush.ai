"""场景(Scene)上下文加载。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.db.models import Scene


async def get_scene_context_for_prompt(
    session: AsyncSession,
    scene_id: str | None,
) -> str:
    """根据场景ID加载场景的系统提示词，用于注入到对话中。"""
    if not scene_id:
        return ""
    stmt = select(Scene).where(
        Scene.id == scene_id,
        Scene.is_active.is_(True),
    )
    result = await session.execute(stmt)
    scene = result.scalar_one_or_none()
    if not scene:
        return ""
    parts: list[str] = [scene.system_prompt]
    if scene.opening_message:
        parts.append(f"【开场白参考】{scene.opening_message}")
    return "\n\n".join(parts)
