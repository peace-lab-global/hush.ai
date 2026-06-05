"""测试 knowledge QA prompt 构建。"""

from __future__ import annotations

from hushai.meditation.core.prompt import (
    KNOWLEDGE_QA_KB_SECTION,
    KNOWLEDGE_QA_MEMORY_SECTION,
    KNOWLEDGE_QA_SYSTEM,
    build_knowledge_qa_prompt,
)


class TestBuildKnowledgeQAPrompt:
    def test_no_args_returns_system_only(self):
        result = build_knowledge_qa_prompt()
        assert result == KNOWLEDGE_QA_SYSTEM

    def test_system_contains_xiaoguan(self):
        assert "小观" in KNOWLEDGE_QA_SYSTEM

    def test_with_knowledge_context(self):
        result = build_knowledge_qa_prompt(knowledge_context="正念呼吸的核心要点是……")
        assert "正念呼吸的核心要点是……" in result
        assert "知识库参考" in result

    def test_with_memory_context(self):
        result = build_knowledge_qa_prompt(memory_context="用户喜欢冥想")
        assert "用户喜欢冥想" in result
        assert "关于这位用户" in result

    def test_with_both_contexts(self):
        result = build_knowledge_qa_prompt(
            knowledge_context="KB内容",
            memory_context="MEM内容",
        )
        assert "KB内容" in result
        assert "MEM内容" in result
        assert "知识库参考" in result
        assert "关于这位用户" in result

    def test_empty_strings_treated_as_absent(self):
        result = build_knowledge_qa_prompt(knowledge_context="", memory_context="")
        assert result == KNOWLEDGE_QA_SYSTEM

    def test_kb_section_template(self):
        formatted = KNOWLEDGE_QA_KB_SECTION.format(knowledge_context="测试")
        assert "测试" in formatted
        assert "知识库参考" in formatted

    def test_memory_section_template(self):
        formatted = KNOWLEDGE_QA_MEMORY_SECTION.format(memory_context="测试")
        assert "测试" in formatted
        assert "关于这位用户" in formatted
