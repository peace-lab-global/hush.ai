"""测试 engine.chat 的安全检查时机。

P0 修复验证：危机内容必须在调用 LLM 之前被拦截，不得送往外部模型。
旧实现在 LLM 调用之后才 check_safety（engine.py:130），已修正为之前。
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hushai.meditation import config as cfg_module
from hushai.meditation.core import engine


@pytest.fixture(autouse=True)
def _test_config():
    cfg_module.set_config(
        cfg_module.MeditationConfig(debug=False, jwt_secret="test", openai_api_key="sk-test")
    )
    yield
    cfg_module.reset_config()


def _make_mock_session_and_factory():
    """构造一个能通过 conversation 创建/flush 的 mock session + factory。"""
    conv = MagicMock()
    conv.id = "conv-1"
    conv.title = None

    async def _execute(stmt):
        result = MagicMock()
        result.scalar_one_or_none.return_value = conv
        result.scalars.return_value.all.return_value = []
        return result

    async def _flush():
        for call in session.add.call_args_list:
            instance = call.args[0]
            if not getattr(instance, "id", None):
                instance.id = "conv-1"

    session = AsyncMock()
    session.execute = AsyncMock(side_effect=_execute)
    session.flush = AsyncMock(side_effect=_flush)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()

    factory = MagicMock()
    factory.return_value.__aenter__ = AsyncMock(return_value=session)
    factory.return_value.__aexit__ = AsyncMock(return_value=False)
    return session, conv, factory


@pytest.mark.asyncio
async def test_crisis_input_skips_llm_call():
    """危机输入时 chat() 不应调用 chat_completion（P0 核心修复）。"""
    session, conv, factory = _make_mock_session_and_factory()

    with (
        patch.object(engine, "get_session_factory", return_value=factory),
        patch.object(engine, "chat_completion", new=AsyncMock()) as mock_llm,
    ):
        result = await engine.chat(
            user_id="user-1",
            message="我不想活了，活着好累",
        )

    # 核心断言：LLM 未被调用
    mock_llm.assert_not_called()
    # 返回的是安全提示，包含热线信息
    assert "温馨提示" in result["reply"]
    assert "400-161-9995" in result["reply"] or "120" in result["reply"]
    assert result["memory_updated"] is False


@pytest.mark.asyncio
async def test_normal_input_calls_llm():
    """正常输入应照常调用 LLM。"""
    session, conv, factory = _make_mock_session_and_factory()
    mock_llm = AsyncMock(return_value="正常回复，深呼吸")
    # _load_conversation_messages 会被调用，返回空列表即可

    with (
        patch.object(engine, "get_session_factory", return_value=factory),
        patch.object(engine, "chat_completion", new=mock_llm),
        patch.object(engine, "retrieve_relevant_memories", new=AsyncMock(return_value=[])),
        patch.object(engine, "get_knowledge_context_for_prompt", new=AsyncMock(return_value="")),
        patch.object(engine, "get_memory_context_for_prompt", new=AsyncMock(return_value="")),
        patch.object(engine, "get_scene_context_for_prompt", new=AsyncMock(return_value="")),
        patch.object(engine, "get_skills_context_for_prompt", return_value=""),
    ):
        result = await engine.chat(
            user_id="user-1",
            message="今天压力有点大，帮我放松一下",
        )

    mock_llm.assert_called_once()
    assert result["reply"] == "正常回复，深呼吸"


@pytest.mark.asyncio
async def test_crisis_input_still_persists_message():
    """危机输入也应持久化对话与消息（用于审计/追踪），只是不调 LLM。"""
    session, conv, factory = _make_mock_session_and_factory()

    with (
        patch.object(engine, "get_session_factory", return_value=factory),
        patch.object(engine, "chat_completion", new=AsyncMock()) as mock_llm,
    ):
        await engine.chat(user_id="user-1", message="我想自杀")

    mock_llm.assert_not_called()
    # commit 应被调用（消息已持久化）
    session.commit.assert_awaited()
    # 至少添加了 user_msg 和 assistant_msg 两条
    assert session.add.call_count >= 2
