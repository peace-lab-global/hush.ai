"""冥想老师主引擎 — 编排对话、记忆提取、知识检索。"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.config import get_config
from hushai.meditation.core.knowledge import get_knowledge_context_for_prompt
from hushai.meditation.core.llm import LLMMessage, chat_completion, chat_completion_stream
from hushai.meditation.core.memory import (
    extract_memories,
    get_memory_context_for_prompt,
    store_memories,
)
from hushai.meditation.core.prompt import (
    build_system_prompt,
    format_conversation_history,
)
from hushai.meditation.core.skills import get_skills_context_for_prompt
from hushai.meditation.db.models import Conversation, Message
from hushai.meditation.db.session import get_session_factory

logger = logging.getLogger(__name__)


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
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    result = await session.execute(stmt)
    msgs = list(result.scalars().all())
    if cfg.conversation_max_turns > 0:
        cutoff = len(msgs) - cfg.conversation_max_turns * 2
        if cutoff > 0:
            msgs = msgs[cutoff:]
    return msgs


async def chat(
    *,
    user_id: str,
    message: str,
    conversation_id: str | None = None,
    teacher_description: str | None = None,
    skill_ids: list[str] | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    factory = get_session_factory()
    async with factory() as session:
        conv = await _get_or_create_conversation(session, user_id, conversation_id)
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=message,
        )
        session.add(user_msg)
        await session.flush()

        prev_messages = await _load_conversation_messages(session, conv.id)
        memory_context = await get_memory_context_for_prompt(session, user_id, message)
        knowledge_context = await get_knowledge_context_for_prompt(message)
        skills_context = await get_skills_context_for_prompt(session, skill_ids)
        history_dicts = [{"role": m.role, "content": m.content} for m in prev_messages[:-1]]
        history_text = format_conversation_history(history_dicts)
        system_prompt = build_system_prompt(
            memory_context=memory_context,
            knowledge_context=knowledge_context,
            conversation_history=history_text,
            teacher_description=teacher_description,
            skills_context=skills_context,
        )
        llm_messages = [LLMMessage(role="system", content=system_prompt)]
        for m in prev_messages:
            llm_messages.append(LLMMessage(role=m.role, content=m.content))
        reply = await chat_completion(
            llm_messages,
            provider=provider,
            temperature=0.7,
            max_tokens=1024,
        )
        assistant_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=reply,
        )
        session.add(assistant_msg)
        await session.flush()

        all_conv_messages = prev_messages + [assistant_msg]
        memory_updated = False
        try:
            memories_data = await extract_memories(all_conv_messages, provider=provider)
            if memories_data:
                await store_memories(session, user_id, memories_data, conv.id)
                memory_updated = True
        except Exception:
            logger.warning("记忆提取失败", exc_info=True)

        if not conv.title:
            first_user_msg = next((m for m in all_conv_messages if m.role == "user"), None)
            if first_user_msg:
                conv.title = first_user_msg.content[:64]

        await session.commit()
        return {
            "reply": reply,
            "conversation_id": conv.id,
            "memory_updated": memory_updated,
        }


async def chat_stream(
    *,
    user_id: str,
    message: str,
    conversation_id: str | None = None,
    teacher_description: str | None = None,
    skill_ids: list[str] | None = None,
    provider: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    factory = get_session_factory()
    async with factory() as session:
        conv = await _get_or_create_conversation(session, user_id, conversation_id)
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=message,
        )
        session.add(user_msg)
        await session.flush()

        prev_messages = await _load_conversation_messages(session, conv.id)
        memory_context = await get_memory_context_for_prompt(session, user_id, message)
        knowledge_context = await get_knowledge_context_for_prompt(message)
        skills_context = await get_skills_context_for_prompt(session, skill_ids)
        history_dicts = [{"role": m.role, "content": m.content} for m in prev_messages[:-1]]
        history_text = format_conversation_history(history_dicts)
        system_prompt = build_system_prompt(
            memory_context=memory_context,
            knowledge_context=knowledge_context,
            conversation_history=history_text,
            teacher_description=teacher_description,
            skills_context=skills_context,
        )
        llm_messages = [LLMMessage(role="system", content=system_prompt)]
        for m in prev_messages:
            llm_messages.append(LLMMessage(role=m.role, content=m.content))

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
        assistant_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=full_reply,
        )
        session.add(assistant_msg)
        await session.flush()

        try:
            all_msgs = prev_messages + [assistant_msg]
            memories_data = await extract_memories(all_msgs, provider=provider)
            if memories_data:
                await store_memories(session, user_id, memories_data, conv.id)
        except Exception:
            logger.warning("记忆提取失败", exc_info=True)

        if not conv.title:
            first_user_msg = next((m for m in prev_messages if m.role == "user"), None)
            if first_user_msg:
                conv.title = first_user_msg.content[:64]

        await session.commit()
        yield {"delta": "", "done": True, "conversation_id": conv.id}
