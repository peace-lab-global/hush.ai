"""长期记忆管理 — 提取、存储、检索。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.config import get_config
from hushai.meditation.core.llm import LLMMessage, chat_completion
from hushai.meditation.db import vector
from hushai.meditation.db.models import Memory, Message

MEMORY_EXTRACTION_PROMPT = """你是一个记忆提取助手。分析以下对话内容，提取出需要长期记住的关键信息。

记忆类别：
- meditation_experience: 冥想经历（练习时长、频率、技法偏好、身体感受）
- emotion_pattern: 情绪模式（常见情绪、触发因素、情绪变化趋势）
- personal_preference: 个人偏好（喜欢的引导风格、时间偏好、沟通方式）
- goal_progress: 目标与进展（修行目标、里程碑、当前阶段）
- important_event: 重要事件（突破、感悟、困难、转折点）
- health_note: 健康相关（身体限制、不适、医嘱）
- life_context: 生活背景（工作、家庭、压力源）

请以 JSON 数组返回，每个元素包含：
- "category": 类别（上述之一）
- "content": 原始事实描述（详细、具体）
- "summary": 简短摘要（不超过50字）
- "importance": 重要度 0.0-1.0

如果对话中没有需要记住的信息，返回空数组 []。

对话内容：
{conversation}

只输出 JSON 数组，不要其他文字。"""

logger = logging.getLogger(__name__)


async def extract_memories(
    messages: list[Message],
    *,
    provider: str | None = None,
) -> list[dict[str, Any]]:
    conversation_text = "\n".join(
        f"{'用户' if m.role == 'user' else '老师'}: {m.content}" for m in messages
    )
    prompt = MEMORY_EXTRACTION_PROMPT.format(conversation=conversation_text)
    cfg = get_config()
    model = cfg.memory_extraction_model or None
    try:
        raw = await chat_completion(
            [LLMMessage(role="system", content=prompt)],
            provider=provider,
            model=model,
            temperature=0.3,
            max_tokens=1024,
        )
        text = raw.strip()
        if text.startswith("```"):
            first_nl = text.find("\n")
            last_tick = text.rfind("```")
            if first_nl != -1 and last_tick > first_nl:
                text = text[first_nl + 1 : last_tick].strip()
        result = json.loads(text)
        if not isinstance(result, list):
            return []
        return [r for r in result if isinstance(r, dict) and r.get("category") and r.get("content")]
    except (json.JSONDecodeError, ValueError, KeyError):
        logger.warning("记忆提取 JSON 解析失败", exc_info=True)
        return []


async def store_memories(
    session: AsyncSession,
    user_id: str,
    memories_data: list[dict[str, Any]],
    source_conversation_id: str | None = None,
) -> list[Memory]:
    stored: list[Memory] = []
    for md in memories_data:
        category = md.get("category", "life_context")
        content = md.get("content", "")
        summary = md.get("summary", "")
        importance = float(md.get("importance", 0.5))
        mem = Memory(
            user_id=user_id,
            category=category,
            content=content,
            summary=summary,
            importance=max(0.0, min(1.0, importance)),
            source_conversation_id=source_conversation_id,
            status="active",
        )
        session.add(mem)
        await session.flush()
        vector.add_memory_embedding(
            memory_id=mem.id,
            content=content,
            user_id=user_id,
            category=category,
        )
        stored.append(mem)
    return stored


async def retrieve_relevant_memories(
    session: AsyncSession,
    user_id: str,
    query: str,
    top_k: int | None = None,
) -> list[Memory]:
    cfg = get_config()
    top_k = top_k or cfg.memory_top_k
    results = vector.search_memories(query, user_id=user_id, top_k=top_k)
    if not results:
        return []
    ids = [r["id"] for r in results]
    stmt = select(Memory).where(
        Memory.id.in_(ids),
        Memory.status == "active",
    )
    db_result = await session.execute(stmt)
    mem_map = {m.id: m for m in db_result.scalars().all()}
    ordered: list[Memory] = []
    for r in results:
        m = mem_map.get(r["id"])
        if m:
            ordered.append(m)
    return ordered


async def get_user_memories(
    session: AsyncSession,
    user_id: str,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Memory], int]:
    base = select(Memory).where(Memory.user_id == user_id, Memory.status == "active")
    if category:
        base = base.where(Memory.category == category)
    count_stmt = select(func.count()).select_from(base.subquery())
    base = base.order_by(Memory.importance.desc(), Memory.updated_at.desc())
    base = base.limit(limit).offset(offset)
    result = await session.execute(base)
    memories = list(result.scalars().all())
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0
    return memories, total


async def get_memory_context_for_prompt(
    session: AsyncSession,
    user_id: str,
    current_message: str,
) -> str:
    memories = await retrieve_relevant_memories(session, user_id, current_message)
    if not memories:
        return ""
    lines: list[str] = ["【关于这位客户，你记得以下信息】"]
    for m in memories:
        label = _category_label(m.category)
        lines.append(f"- [{label}] {m.summary or m.content[:80]}")
    return "\n".join(lines)


def _category_label(category: str) -> str:
    labels = {
        "meditation_experience": "冥想经历",
        "emotion_pattern": "情绪模式",
        "personal_preference": "个人偏好",
        "goal_progress": "目标进展",
        "important_event": "重要事件",
        "health_note": "健康提醒",
        "life_context": "生活背景",
    }
    return labels.get(category, category)


async def archive_old_memories(
    session: AsyncSession,
    user_id: str,
) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    stmt = (
        update(Memory)
        .where(
            Memory.user_id == user_id,
            Memory.status == "active",
            Memory.importance < 0.3,
            Memory.updated_at < cutoff,
        )
        .values(status="archived")
    )
    result = await session.execute(stmt)
    return result.rowcount  # type: ignore[attr-defined]
