"""冥想老师主引擎 — 编排对话、记忆提取、知识检索。"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.config import get_config
from hushai.meditation.core.knowledge import get_knowledge_context_for_prompt, search_knowledge_base
from hushai.meditation.core.llm import LLMMessage, chat_completion, chat_completion_stream
from hushai.meditation.core.memory import (
    extract_memories,
    get_memory_context_for_prompt,
    store_memories,
)
from hushai.meditation.core.prompt import (
    build_knowledge_qa_prompt,
    build_system_prompt,
    format_conversation_history,
)
from hushai.meditation.core.safety import check_safety, format_safety_message
from hushai.meditation.core.scenes import get_scene_context_for_prompt
from hushai.meditation.core.skills import get_skills_context_for_prompt
from hushai.meditation.db.models import Conversation, Message, Teacher
from hushai.meditation.db.session import get_session_factory

logger = logging.getLogger(__name__)

# 记忆提取触发的间隔：每 N 条用户消息提取一次。
_MEMORY_EXTRACTION_INTERVAL = 2


async def _get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: str | None,
) -> Conversation:
    if conversation_id:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_active.is_(True),
        )
        result = await session.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            return conv
    conv = Conversation(user_id=user_id)
    session.add(conv)
    await session.flush()
    return conv


async def _load_conversation_messages(
    session: AsyncSession,
    conversation_id: str,
) -> list[Message]:
    cfg = get_config()
    limit = None
    if cfg.conversation_max_turns > 0:
        limit = cfg.conversation_max_turns * 2
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def _resolve_teacher_prompt(
    session: AsyncSession,
    teacher_id: str | None,
    teacher_description: str | None,
) -> str | None:
    """根据 teacher_id 查库得到 system_prompt；无 id 则沿用传入的描述。"""
    if not teacher_id:
        return teacher_description
    result = await session.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    return teacher.system_prompt if teacher else teacher_description


async def _prepare_turn_context(
    session: AsyncSession,
    user_id: str,
    conv: Conversation,
    message: str,
    skill_ids: list[str] | None,
    scene_id: str | None,
    teacher_id: str | None,
    teacher_description: str | None,
) -> list[LLMMessage]:
    """组装下一轮对话的 LLM messages（system + 历史）。

    供 ``chat`` / ``chat_stream`` 共用，消除重复的上下文构建逻辑。
    """
    prev_messages = await _load_conversation_messages(session, conv.id)
    memory_context = await get_memory_context_for_prompt(session, user_id, message)
    knowledge_context = await get_knowledge_context_for_prompt(message)
    skills_context = await get_skills_context_for_prompt(session, skill_ids)
    scene_context = await get_scene_context_for_prompt(session, scene_id)

    history_dicts = [{"role": m.role, "content": m.content} for m in prev_messages[:-1]]
    history_text = format_conversation_history(history_dicts)

    resolved_teacher = await _resolve_teacher_prompt(session, teacher_id, teacher_description)
    system_prompt = build_system_prompt(
        memory_context=memory_context,
        knowledge_context=knowledge_context,
        conversation_history=history_text,
        teacher_description=resolved_teacher,
        skills_context=skills_context,
        scene_context=scene_context,
    )

    llm_messages = [LLMMessage(role="system", content=system_prompt)]
    for m in prev_messages:
        llm_messages.append(LLMMessage(role=m.role, content=m.content))
    return llm_messages


async def _maybe_extract_and_title(
    session: AsyncSession,
    conv: Conversation,
    user_id: str,
    all_messages: list[Message],
    provider: str | None,
) -> bool:
    """按周期触发记忆提取，并在首轮补全会话标题。返回是否更新了记忆。"""
    user_turn_count = sum(1 for m in all_messages if m.role == "user")
    memory_updated = False
    if user_turn_count % _MEMORY_EXTRACTION_INTERVAL == 0:
        try:
            memories_data = await extract_memories(all_messages, provider=provider)
            if memories_data:
                await store_memories(session, user_id, memories_data, conv.id)
                memory_updated = True
        except Exception:
            logger.warning("记忆提取失败", exc_info=True)

    if not conv.title:
        first_user_msg = next((m for m in all_messages if m.role == "user"), None)
        if first_user_msg:
            conv.title = first_user_msg.content[:64]
    return memory_updated


def _persist_user_message(
    session: AsyncSession,
    conv: Conversation,
    message: str,
) -> Message:
    user_msg = Message(conversation_id=conv.id, role="user", content=message)
    session.add(user_msg)
    return user_msg


async def chat(
    *,
    user_id: str,
    message: str,
    conversation_id: str | None = None,
    teacher_description: str | None = None,
    skill_ids: list[str] | None = None,
    provider: str | None = None,
    scene_id: str | None = None,
    teacher_id: str | None = None,
) -> dict[str, Any]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            conv = await _get_or_create_conversation(session, user_id, conversation_id)

            # 安全检查必须在调用 LLM 之前：危机内容不应被送往外部模型。
            safety_result = check_safety(message)
            if not safety_result.is_safe:
                reply = format_safety_message(safety_result, "")
                assistant_msg = Message(conversation_id=conv.id, role="assistant", content=reply)
                session.add(assistant_msg)
                await session.flush()
                if not conv.title:
                    conv.title = message[:64]
                await session.commit()
                return {
                    "reply": reply,
                    "conversation_id": conv.id,
                    "memory_updated": False,
                }

            _persist_user_message(session, conv, message)
            await session.flush()

            llm_messages = await _prepare_turn_context(
                session,
                user_id,
                conv,
                message,
                skill_ids,
                scene_id,
                teacher_id,
                teacher_description,
            )
            reply = await chat_completion(
                llm_messages,
                provider=provider,
                temperature=0.7,
                max_tokens=1024,
            )

            assistant_msg = Message(conversation_id=conv.id, role="assistant", content=reply)
            session.add(assistant_msg)
            await session.flush()

            prev_messages = await _load_conversation_messages(session, conv.id)
            memory_updated = await _maybe_extract_and_title(
                session, conv, user_id, prev_messages, provider
            )

            await session.commit()
            return {
                "reply": reply,
                "conversation_id": conv.id,
                "memory_updated": memory_updated,
            }
        except Exception:
            await session.rollback()
            raise


async def chat_stream(
    *,
    user_id: str,
    message: str,
    conversation_id: str | None = None,
    teacher_description: str | None = None,
    skill_ids: list[str] | None = None,
    provider: str | None = None,
    scene_id: str | None = None,
    teacher_id: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    factory = get_session_factory()
    async with factory() as session:
        committed = False
        try:
            conv = await _get_or_create_conversation(session, user_id, conversation_id)

            # 安全检查必须在调用 LLM 之前：危机内容不应被送往外部模型。
            safety_result = check_safety(message)
            if not safety_result.is_safe:
                warning_text = (
                    f"\n\n【温馨提示】{safety_result.message}\n\n{safety_result.suggestion}"
                )
                for char in warning_text:
                    yield {"delta": char, "done": False, "conversation_id": conv.id}
                    await asyncio.sleep(0.02)
                assistant_msg = Message(
                    conversation_id=conv.id, role="assistant", content=warning_text.strip()
                )
                session.add(assistant_msg)
                await session.flush()
                if not conv.title:
                    conv.title = message[:64]
                await session.commit()
                committed = True
                yield {"delta": "", "done": True, "conversation_id": conv.id}
                return

            _persist_user_message(session, conv, message)
            await session.flush()

            llm_messages = await _prepare_turn_context(
                session,
                user_id,
                conv,
                message,
                skill_ids,
                scene_id,
                teacher_id,
                teacher_description,
            )

            collected_parts: list[str] = []
            async for delta in chat_completion_stream(
                llm_messages,
                provider=provider,
                temperature=0.7,
                max_tokens=1024,
            ):
                collected_parts.append(delta)
                yield {"delta": delta, "done": False, "conversation_id": conv.id}

            full_reply = "".join(collected_parts)
            assistant_msg = Message(conversation_id=conv.id, role="assistant", content=full_reply)
            session.add(assistant_msg)
            await session.flush()

            prev_messages = await _load_conversation_messages(session, conv.id)
            await _maybe_extract_and_title(session, conv, user_id, prev_messages, provider)

            await session.commit()
            committed = True
            yield {"delta": "", "done": True, "conversation_id": conv.id}
        finally:
            if not committed:
                await session.rollback()


async def knowledge_qa(
    *,
    user_id: str,
    message: str,
    conversation_id: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            conv = await _get_or_create_conversation(session, user_id, conversation_id)
            user_msg = Message(
                conversation_id=conv.id,
                role="user",
                content=message,
            )
            session.add(user_msg)
            await session.flush()

            kb_results = await search_knowledge_base(message, top_k=8)
            kb_context_parts: list[str] = []
            for r in kb_results:
                src = f"（来源: {r.get('source', '知识库')}）" if r.get("source") else ""
                kb_context_parts.append(f"- {r['content'][:300]}{src}")
            kb_context = "\n".join(kb_context_parts) if kb_context_parts else ""

            memory_context = await get_memory_context_for_prompt(session, user_id, message)

            system_prompt = build_knowledge_qa_prompt(
                knowledge_context=kb_context,
                memory_context=memory_context,
            )

            prev_messages = await _load_conversation_messages(session, conv.id)
            llm_messages = [LLMMessage(role="system", content=system_prompt)]
            for m in prev_messages:
                llm_messages.append(LLMMessage(role=m.role, content=m.content))

            reply = await chat_completion(
                llm_messages,
                provider=provider,
                temperature=0.5,
                max_tokens=1500,
            )
            assistant_msg = Message(
                conversation_id=conv.id,
                role="assistant",
                content=reply,
            )
            session.add(assistant_msg)
            await session.flush()

            if not conv.title:
                conv.title = message[:64]

            await session.commit()
            return {
                "reply": reply,
                "conversation_id": conv.id,
                "sources": [
                    {
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "score": round(r.get("score", 0), 3),
                    }
                    for r in kb_results[:5]
                ],
            }
        except Exception:
            await session.rollback()
            raise
