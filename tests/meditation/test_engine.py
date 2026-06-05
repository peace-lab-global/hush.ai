"""测试冥想引擎 — knowledge_qa 编排。"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hushai.meditation.config import MeditationConfig, reset_config, set_config


@pytest.fixture(autouse=True)
def _reset_config_fixture():
    yield
    reset_config()


def _make_config():
    return MeditationConfig(jwt_secret="test", openai_api_key="test-key")


def _make_mock_session():
    session = AsyncMock()
    conv = MagicMock()
    conv.id = "conv-1"
    conv.title = None

    async def _execute(stmt):
        result = MagicMock()
        result.scalar_one_or_none.return_value = conv
        result.scalars.return_value.all.return_value = []
        return result

    async def _flush():
        for obj in session.add.call_args_list:
            instance = obj[0][0]
            if not getattr(instance, "id", None):
                instance.id = "conv-1"

    session.execute = AsyncMock(side_effect=_execute)
    session.flush = AsyncMock(side_effect=_flush)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session, conv


def _make_factory(session):
    factory = MagicMock()
    factory.return_value.__aenter__ = AsyncMock(return_value=session)
    factory.return_value.__aexit__ = AsyncMock(return_value=False)
    return factory


class TestKnowledgeQA:
    @pytest.mark.asyncio
    async def test_builds_correct_system_prompt(self):
        set_config(_make_config())
        session, conv = _make_mock_session()
        factory = _make_factory(session)

        with (
            patch("hushai.meditation.core.engine.get_session_factory", return_value=factory),
            patch(
                "hushai.meditation.core.engine.search_knowledge_base",
                new_callable=AsyncMock,
                return_value=[],
            ) as mock_search,
            patch(
                "hushai.meditation.core.engine.get_memory_context_for_prompt",
                new_callable=AsyncMock,
                return_value="",
            ),
            patch(
                "hushai.meditation.core.engine.chat_completion",
                new_callable=AsyncMock,
                return_value="这是小观的回答",
            ),
            patch("hushai.meditation.core.engine.build_knowledge_qa_prompt") as mock_build,
        ):
            from hushai.meditation.core.engine import knowledge_qa

            mock_build.return_value = "system-prompt"

            await knowledge_qa(
                user_id="u1",
                message="什么是正念？",
            )

            mock_build.assert_called_once_with(
                knowledge_context="",
                memory_context="",
            )
            mock_search.assert_called_once_with("什么是正念？", top_k=8)

    @pytest.mark.asyncio
    async def test_searches_knowledge_base(self):
        set_config(_make_config())
        session, conv = _make_mock_session()
        factory = _make_factory(session)

        kb_results = [
            {
                "id": "k1",
                "content": "正念是对当下的觉知",
                "title": "正念入门",
                "score": 0.95,
                "source": "book",
            },
            {
                "id": "k2",
                "content": "呼吸是正念的基础",
                "title": "呼吸法",
                "score": 0.80,
                "source": None,
            },
        ]

        with (
            patch("hushai.meditation.core.engine.get_session_factory", return_value=factory),
            patch(
                "hushai.meditation.core.engine.search_knowledge_base",
                new_callable=AsyncMock,
                return_value=kb_results,
            ),
            patch(
                "hushai.meditation.core.engine.get_memory_context_for_prompt",
                new_callable=AsyncMock,
                return_value="用户喜欢冥想",
            ),
            patch(
                "hushai.meditation.core.engine.chat_completion",
                new_callable=AsyncMock,
                return_value="正念是一种觉知练习",
            ),
            patch("hushai.meditation.core.engine.build_knowledge_qa_prompt", return_value="sys"),
        ):
            from hushai.meditation.core.engine import knowledge_qa

            result = await knowledge_qa(
                user_id="u1",
                message="什么是正念？",
            )

            assert len(result["sources"]) == 2
            assert result["sources"][0]["id"] == "k1"
            assert result["sources"][0]["title"] == "正念入门"
            assert result["sources"][0]["score"] == 0.95
            assert result["sources"][1]["id"] == "k2"

    @pytest.mark.asyncio
    async def test_returns_reply_conversation_id_sources(self):
        set_config(_make_config())
        session, conv = _make_mock_session()
        factory = _make_factory(session)

        with (
            patch("hushai.meditation.core.engine.get_session_factory", return_value=factory),
            patch(
                "hushai.meditation.core.engine.search_knowledge_base",
                new_callable=AsyncMock,
                return_value=[
                    {"id": "k1", "content": "内容", "title": "标题", "score": 0.9},
                ],
            ),
            patch(
                "hushai.meditation.core.engine.get_memory_context_for_prompt",
                new_callable=AsyncMock,
                return_value="",
            ),
            patch(
                "hushai.meditation.core.engine.chat_completion",
                new_callable=AsyncMock,
                return_value="正念是对当下的觉知。",
            ),
            patch("hushai.meditation.core.engine.build_knowledge_qa_prompt", return_value="sys"),
        ):
            from hushai.meditation.core.engine import knowledge_qa

            result = await knowledge_qa(
                user_id="u1",
                message="什么是正念？",
            )

            assert result["reply"] == "正念是对当下的觉知。"
            assert result["conversation_id"] == "conv-1"
            assert "sources" in result
            assert isinstance(result["sources"], list)

    @pytest.mark.asyncio
    async def test_includes_kb_context_in_prompt(self):
        set_config(_make_config())
        session, conv = _make_mock_session()
        factory = _make_factory(session)

        kb_results = [
            {"content": "正念三要素", "source": "书", "id": "k1", "title": "t", "score": 0.9},
        ]

        with (
            patch("hushai.meditation.core.engine.get_session_factory", return_value=factory),
            patch(
                "hushai.meditation.core.engine.search_knowledge_base",
                new_callable=AsyncMock,
                return_value=kb_results,
            ),
            patch(
                "hushai.meditation.core.engine.get_memory_context_for_prompt",
                new_callable=AsyncMock,
                return_value="用户有焦虑倾向",
            ),
            patch(
                "hushai.meditation.core.engine.chat_completion",
                new_callable=AsyncMock,
                return_value="回答",
            ),
            patch("hushai.meditation.core.engine.build_knowledge_qa_prompt") as mock_build,
        ):
            from hushai.meditation.core.engine import knowledge_qa

            await knowledge_qa(user_id="u1", message="正念是什么")

            call_kwargs = mock_build.call_args.kwargs
            assert "正念三要素" in call_kwargs["knowledge_context"]
            assert "来源" in call_kwargs["knowledge_context"]
            assert call_kwargs["memory_context"] == "用户有焦虑倾向"

    @pytest.mark.asyncio
    async def test_limits_sources_to_five(self):
        set_config(_make_config())
        session, conv = _make_mock_session()
        factory = _make_factory(session)

        kb_results = [
            {"id": f"k{i}", "content": f"内容{i}", "title": f"标题{i}", "score": 0.9 - i * 0.01}
            for i in range(10)
        ]

        with (
            patch("hushai.meditation.core.engine.get_session_factory", return_value=factory),
            patch(
                "hushai.meditation.core.engine.search_knowledge_base",
                new_callable=AsyncMock,
                return_value=kb_results,
            ),
            patch(
                "hushai.meditation.core.engine.get_memory_context_for_prompt",
                new_callable=AsyncMock,
                return_value="",
            ),
            patch(
                "hushai.meditation.core.engine.chat_completion",
                new_callable=AsyncMock,
                return_value="回答",
            ),
            patch("hushai.meditation.core.engine.build_knowledge_qa_prompt", return_value="sys"),
        ):
            from hushai.meditation.core.engine import knowledge_qa

            result = await knowledge_qa(user_id="u1", message="测试")
            assert len(result["sources"]) == 5

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        set_config(_make_config())
        session, conv = _make_mock_session()
        factory = _make_factory(session)

        with (
            patch("hushai.meditation.core.engine.get_session_factory", return_value=factory),
            patch(
                "hushai.meditation.core.engine.search_knowledge_base",
                new_callable=AsyncMock,
                side_effect=RuntimeError("boom"),
            ),
        ):
            from hushai.meditation.core.engine import knowledge_qa

            with pytest.raises(RuntimeError, match="boom"):
                await knowledge_qa(user_id="u1", message="测试")

            session.rollback.assert_called_once()
