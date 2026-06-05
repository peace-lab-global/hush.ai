"""测试 Pydantic 请求/响应模型。"""

from __future__ import annotations

import pytest

from hushai.meditation.schemas import (
    ChatRequest,
    KnowledgeImportRequest,
    KnowledgeQAResponse,
    KnowledgeSourceItem,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SkillImportItem,
    SkillImportRequest,
)


class TestKnowledgeQAResponse:
    def test_defaults(self):
        r = KnowledgeQAResponse(reply="你好", conversation_id="c1")
        assert r.reply == "你好"
        assert r.conversation_id == "c1"
        assert r.sources == []

    def test_with_sources(self):
        src = KnowledgeSourceItem(id="k1", title="冥想入门", score=0.92)
        r = KnowledgeQAResponse(reply="答", conversation_id="c2", sources=[src])
        assert len(r.sources) == 1
        assert r.sources[0].id == "k1"
        assert r.sources[0].title == "冥想入门"
        assert r.sources[0].score == 0.92


class TestKnowledgeSourceItem:
    def test_defaults(self):
        item = KnowledgeSourceItem()
        assert item.id is None
        assert item.title is None
        assert item.score == 0.0

    def test_full(self):
        item = KnowledgeSourceItem(id="abc", title="标题", score=0.85)
        assert item.id == "abc"
        assert item.title == "标题"
        assert item.score == 0.85


class TestChatRequest:
    def test_defaults(self):
        r = ChatRequest(message="你好")
        assert r.message == "你好"
        assert r.conversation_id is None
        assert r.stream is False
        assert r.skill_ids is None
        assert r.provider is None

    def test_skill_ids_dedup(self):
        r = ChatRequest(message="hi", skill_ids=["a", "b", "a", "c", "b"])
        assert r.skill_ids == ["a", "b", "c"]

    def test_skill_ids_strips_and_filters_empty(self):
        r = ChatRequest(message="hi", skill_ids=["  a ", "", "  ", "b"])
        assert r.skill_ids == ["a", "b"]

    def test_skill_ids_all_invalid_returns_none(self):
        r = ChatRequest(message="hi", skill_ids=["", "  "])
        assert r.skill_ids is None

    def test_skill_ids_respects_max_limit(self):
        ids = [f"s{i}" for i in range(20)]
        r = ChatRequest(message="hi", skill_ids=ids)
        assert len(r.skill_ids) == 8

    def test_message_too_long_raises(self):
        with pytest.raises(ValueError):
            ChatRequest(message="x" * 5001)

    def test_message_empty_raises(self):
        with pytest.raises(ValueError):
            ChatRequest(message="")


class TestKnowledgeImportRequest:
    def test_defaults(self):
        r = KnowledgeImportRequest(content="一些内容")
        assert r.content == "一些内容"
        assert r.title is None
        assert r.tags == []
        assert r.parent_id is None
        assert r.content_format == "plain"

    def test_markdown_format(self):
        r = KnowledgeImportRequest(content="**粗体**", content_format="markdown")
        assert r.content_format == "markdown"

    def test_empty_content_raises(self):
        with pytest.raises(ValueError):
            KnowledgeImportRequest(content="")


class TestSkillImportItem:
    def test_strip_text_validator(self):
        item = SkillImportItem(name="  冥想  ", content="  内容  ")
        assert item.name == "冥想"
        assert item.content == "内容"

    def test_strip_desc_empty_to_none(self):
        item = SkillImportItem(name="n", content="c", description="")
        assert item.description is None

    def test_strip_desc_whitespace_to_none(self):
        item = SkillImportItem(name="n", content="c", description="   ")
        assert item.description is None

    def test_strip_desc_strips_value(self):
        item = SkillImportItem(name="n", content="c", description="  描述  ")
        assert item.description == "描述"

    def test_defaults(self):
        item = SkillImportItem(name="n", content="c")
        assert item.sort_order == 0
        assert item.is_active is True
        assert item.description is None


class TestSkillImportRequest:
    def test_accept_top_level_array(self):
        data = [{"name": "技能A", "content": "内容A"}]
        r = SkillImportRequest.model_validate(data)
        assert len(r.skills) == 1
        assert r.skills[0].name == "技能A"

    def test_normal_dict_form(self):
        data = {"skills": [{"name": "技能B", "content": "内容B"}]}
        r = SkillImportRequest.model_validate(data)
        assert len(r.skills) == 1
        assert r.skills[0].name == "技能B"

    def test_empty_skills_raises(self):
        with pytest.raises(ValueError):
            SkillImportRequest(skills=[])

    def test_multiple_skills(self):
        data = [
            {"name": "A", "content": "a"},
            {"name": "B", "content": "b"},
        ]
        r = SkillImportRequest.model_validate(data)
        assert len(r.skills) == 2


class TestLoginResponse:
    def test_defaults(self):
        r = LoginResponse(access_token="at", refresh_token="rt", user_id="u1")
        assert r.access_token == "at"
        assert r.refresh_token == "rt"
        assert r.token_type == "bearer"
        assert r.expires_in == 604800
        assert r.nickname is None

    def test_with_nickname(self):
        r = LoginResponse(access_token="at", refresh_token="rt", user_id="u1", nickname="小明")
        assert r.nickname == "小明"


class TestRefreshTokenRequest:
    def test_requires_token(self):
        r = RefreshTokenRequest(refresh_token="abc123")
        assert r.refresh_token == "abc123"

    def test_empty_token_raises(self):
        with pytest.raises(ValueError):
            RefreshTokenRequest(refresh_token="")


class TestRefreshTokenResponse:
    def test_defaults(self):
        r = RefreshTokenResponse(access_token="at", refresh_token="rt")
        assert r.access_token == "at"
        assert r.refresh_token == "rt"
        assert r.token_type == "bearer"
        assert r.expires_in == 604800

    def test_custom_expires_in(self):
        r = RefreshTokenResponse(access_token="at", refresh_token="rt", expires_in=3600)
        assert r.expires_in == 3600
