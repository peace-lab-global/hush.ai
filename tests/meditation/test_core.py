"""冥想模块核心测试 — prompt、memory、knowledge。"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hushai.meditation.config import MeditationConfig, reset_config, set_config
from hushai.meditation.core.prompt import (
    ROLE_BASE,
    SAFETY_GUARD,
    build_system_prompt,
    format_conversation_history,
)


@pytest.fixture(autouse=True)
def _reset_config_fixture():
    yield
    reset_config()


class TestBuildSystemPrompt:
    def test_base_prompt_only(self):
        result = build_system_prompt()
        assert ROLE_BASE in result
        assert SAFETY_GUARD in result

    def test_with_memory_context(self):
        result = build_system_prompt(memory_context="客户喜欢呼吸冥想")
        assert "客户喜欢呼吸冥想" in result
        assert "关于这位客户" in result

    def test_with_knowledge_context(self):
        result = build_system_prompt(knowledge_context="观呼吸法是一种基础冥想技术")
        assert "观呼吸法是一种基础冥想技术" in result
        assert "相关理论参考" in result

    def test_with_conversation_history(self):
        msgs = [
            {"role": "user", "content": "我想学冥想"},
            {"role": "assistant", "content": "很好，我们可以从呼吸开始"},
        ]
        history = format_conversation_history(msgs)
        result = build_system_prompt(conversation_history=history)
        assert "我想学冥想" in result
        assert "很好，我们可以从呼吸开始" in result

    def test_with_teacher_description(self):
        result = build_system_prompt(teacher_description="你叫静心老师，擅长内观禅修")
        assert "静心老师" in result

    def test_with_skills_context(self):
        result = build_system_prompt(skills_context="## 睡前放松\n请用缓慢、低沉的语气引导。")
        assert "当前加持的技能指引" in result
        assert "睡前放松" in result

    @pytest.mark.asyncio
    async def test_get_skills_context_auto_mount(self):
        from hushai.meditation.core.skills import get_skills_context_for_prompt
        from hushai.meditation.db.models import Skill
        
        mock_session = AsyncMock()
        mock_result = MagicMock()
        skill = Skill(id="s1", name="自动技能", content="自动内容", is_active=True)
        mock_result.scalars.return_value.all.return_value = [skill]
        mock_session.execute.return_value = mock_result
        
        # 测试 skill_ids=None (自动挂载)
        result = await get_skills_context_for_prompt(mock_session, None)
        assert "自动技能" in result
        assert "自动内容" in result
        
        # 测试 skill_ids=[] (不挂载)
        result = await get_skills_context_for_prompt(mock_session, [])
        assert result == ""

    def test_all_sections(self):
        result = build_system_prompt(
            memory_context="客户偏好: 呼吸法",
            knowledge_context="知识: 身体扫描",
            conversation_history="学生: 最近很焦虑",
            teacher_description="你是静心老师",
            skills_context="## 焦虑安抚\n优先共情再引导呼吸。",
        )
        assert "客户偏好" in result
        assert "知识" in result
        assert "学生" in result
        assert "静心老师" in result
        assert "焦虑安抚" in result


class TestFormatConversationHistory:
    def test_empty_messages(self):
        result = format_conversation_history([])
        assert result == ""

    def test_user_assistant_messages(self):
        msgs = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，欢迎"},
        ]
        result = format_conversation_history(msgs)
        assert "学生: 你好" in result
        assert "老师: 你好，欢迎" in result

    def test_max_turns(self):
        msgs = [{"role": "user", "content": f"消息{i}"} for i in range(10)]
        result = format_conversation_history(msgs, max_turns=3)
        lines = result.strip().split("\n")
        assert len(lines) == 3


class TestMeditationConfig:
    def test_from_env_defaults(self):
        with patch.dict("os.environ", {}, clear=True):
            cfg = MeditationConfig.from_env()
            assert cfg.default_llm_provider == "openai"
            assert cfg.default_llm_model == "gpt-4o-mini"
            assert cfg.memory_top_k == 5
            assert cfg.knowledge_top_k == 3
            assert cfg.port == 8000
            assert cfg.debug is False

    def test_from_env_custom(self):
        env = {
            "MEDITATION_POSTGRES_URL": "postgresql://test:test@localhost/db",
            "MEDITATION_JWT_SECRET": "secret123",
            "MEDITATION_PORT": "9000",
            "MEDITATION_DEBUG": "true",
            "MEDITATION_MEMORY_TOP_K": "10",
        }
        with patch.dict("os.environ", env, clear=False):
            cfg = MeditationConfig.from_env()
            assert cfg.postgres_url == "postgresql://test:test@localhost/db"
            assert cfg.jwt_secret == "secret123"
            assert cfg.port == 9000
            assert cfg.debug is True
            assert cfg.memory_top_k == 10


class TestMemoryExtraction:
    @pytest.mark.asyncio
    async def test_extract_memories_parses_json(self):
        mock_response = json.dumps(
            [
                {
                    "category": "meditation_experience",
                    "content": "客户每天冥想15分钟，使用呼吸法",
                    "summary": "每日冥想15分钟",
                    "importance": 0.8,
                }
            ]
        )
        set_config(
            MeditationConfig(
                openai_api_key="test",
                jwt_secret="test",
            )
        )
        with patch(
            "hushai.meditation.core.memory.chat_completion",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            from hushai.meditation.core.memory import extract_memories

            mock_msg = MagicMock()
            mock_msg.role = "user"
            mock_msg.content = "我每天冥想15分钟"
            result = await extract_memories([mock_msg])
            assert len(result) == 1
            assert result[0]["category"] == "meditation_experience"

    @pytest.mark.asyncio
    async def test_extract_memories_empty(self):
        set_config(
            MeditationConfig(
                openai_api_key="test",
                jwt_secret="test",
            )
        )
        with patch(
            "hushai.meditation.core.memory.chat_completion",
            new_callable=AsyncMock,
            return_value="[]",
        ):
            from hushai.meditation.core.memory import extract_memories

            mock_msg = MagicMock()
            mock_msg.role = "user"
            mock_msg.content = "你好"
            result = await extract_memories([mock_msg])
            assert result == []

    @pytest.mark.asyncio
    async def test_extract_memories_invalid_json(self):
        set_config(
            MeditationConfig(
                openai_api_key="test",
                jwt_secret="test",
            )
        )
        with patch(
            "hushai.meditation.core.memory.chat_completion",
            new_callable=AsyncMock,
            return_value="not json at all",
        ):
            from hushai.meditation.core.memory import extract_memories

            mock_msg = MagicMock()
            mock_msg.role = "user"
            mock_msg.content = "你好"
            result = await extract_memories([mock_msg])
            assert result == []

    @pytest.mark.asyncio
    async def test_extract_memories_code_block_json(self):
        mock_response = (
            '```json\n[{"category": "emotion_pattern", '
            '"content": "焦虑", "summary": "焦虑", "importance": 0.7}]\n```'
        )
        set_config(
            MeditationConfig(
                openai_api_key="test",
                jwt_secret="test",
            )
        )
        with patch(
            "hushai.meditation.core.memory.chat_completion",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            from hushai.meditation.core.memory import extract_memories

            mock_msg = MagicMock()
            mock_msg.role = "user"
            mock_msg.content = "我最近很焦虑"
            result = await extract_memories([mock_msg])
            assert len(result) == 1
            assert result[0]["category"] == "emotion_pattern"


class TestKnowledgeChunking:
    def test_split_text_short(self):
        from hushai.meditation.core.knowledge import _split_text_to_chunks

        text = "这是一段简短的文字。"
        chunks = _split_text_to_chunks(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == "这是一段简短的文字。"

    def test_split_text_long(self):
        from hushai.meditation.core.knowledge import _split_text_to_chunks

        paragraphs = [f"第{i}段内容，" * 50 for i in range(10)]
        text = "\n\n".join(paragraphs)
        chunks = _split_text_to_chunks(text, chunk_size=200, overlap=20)
        assert len(chunks) > 1

    def test_split_text_empty(self):
        from hushai.meditation.core.knowledge import _split_text_to_chunks

        chunks = _split_text_to_chunks("", chunk_size=100)
        assert chunks == []

    def test_split_chinese_text(self):
        from hushai.meditation.core.knowledge import _split_text_to_chunks

        text = "这是一段中文内容。" * 100
        chunks = _split_text_to_chunks(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 300


class TestMarkdownKnowledgeImport:
    def test_markdown_to_plain_basic(self):
        from hushai.meditation.core.knowledge import markdown_to_plain_text

        md = "# 标题\n\n这是**粗体**与[链接](https://x.com)。\n\n- 一项\n"
        plain = markdown_to_plain_text(md)
        assert "标题" in plain
        assert "粗体" in plain
        assert "链接" in plain
        assert "http" not in plain

    def test_prepare_frontmatter_and_title(self):
        from hushai.meditation.core.knowledge import prepare_import_content

        raw = """---
title: 测试文档
tags: 冥想, 入门
---

## 第一节

正文 **内容**。
"""
        plain, title, tags = prepare_import_content(
            raw, filename="x.md", is_markdown=True
        )
        assert title == "测试文档"
        assert "冥想" in tags
        assert "markdown" in tags
        assert "第一节" in plain
        assert "**" not in plain


class TestExtractBearerToken:
    def test_bearer_prefix(self):
        from hushai.meditation.api.auth import extract_bearer_token

        assert extract_bearer_token("Bearer abc123") == "abc123"

    def test_no_bearer_prefix(self):
        from hushai.meditation.api.auth import extract_bearer_token

        assert extract_bearer_token("abc123") == "abc123"
