"""测试安全过滤模块 — 危机信号检测。

验证 P0 修复：正则预编译、级别与模式绑定、空输入处理、format_safety_message。
如实记录当前检测的局限（空格/拼音可绕过），不假装关键词黑名单是完整方案。
"""

from __future__ import annotations

import pytest

from hushai.meditation.core.safety import (
    EMERGENCY_MESSAGE,
    HELP_MESSAGE,
    SafetyResult,
    check_safety,
    format_safety_message,
)


class TestCheckSafety:
    @pytest.mark.parametrize(
        "text",
        [
            "我不想活了",
            "活着好累",
            "我想自杀",
            "有自残的念头",
            "活着没意思",
            "我想死",
        ],
    )
    def test_crisis_self_harm_detected(self, text: str):
        """自伤/自杀类命中应返回 crisis 级别。"""
        result = check_safety(text)
        assert not result.is_safe
        assert result.level == "crisis"
        assert result.suggestion == HELP_MESSAGE

    @pytest.mark.parametrize(
        "text",
        [
            "我想杀人",
            "我要报复社会",
            "想伤害别人",
        ],
    )
    def test_emergency_harm_others_detected(self, text: str):
        """伤害他人类命中应返回 emergency 级别（优先级高于 crisis）。"""
        result = check_safety(text)
        assert not result.is_safe
        assert result.level == "emergency"
        assert result.suggestion == EMERGENCY_MESSAGE

    @pytest.mark.parametrize(
        "text",
        [
            "今天天气真好",
            "我想冥想一下",
            "请帮我放松",
            "工作压力有点大",
        ],
    )
    def test_safe_text_passes(self, text: str):
        """正常冥想/日常文本应判定为安全。"""
        result = check_safety(text)
        assert result.is_safe
        assert result.level == "safe"
        assert result.message is None
        assert result.suggestion is None

    def test_empty_text_is_safe(self):
        """空输入不应误判为危机（P0 修复：增加空值短路）。"""
        result = check_safety("")
        assert result.is_safe
        assert check_safety("   ").is_safe

    def test_first_matched_rule_wins(self):
        """同时命中 emergency 和 crisis 时，emergency 应优先（规则顺序前置）。"""
        # 「杀人」(emergency) 与「想死」(crisis) 同时出现，取 emergency
        result = check_safety("我想杀人然后自己也不想活了")
        assert result.level == "emergency"


class TestRegexCompilation:
    def test_patterns_are_precompiled(self):
        """P0 修复：正则应在模块导入时一次性编译（非每次调用 re.search）。"""
        from hushai.meditation.core import safety

        assert hasattr(safety, "_CRISIS_RULES")
        assert all(callable(r.search) for r, _ in safety._CRISIS_RULES)
        # 每条规则绑定了级别，级别与模式在编译期关联
        assert all(level in ("crisis", "emergency") for _, level in safety._CRISIS_RULES)

    def test_english_keywords_case_insensitive(self):
        """英文关键词应大小写不敏感（依赖 re.IGNORECASE flag）。"""
        # 这条规则含「伤害他人」，若未来扩展英文，IGNORECASE 应生效
        # 当前规则以中文为主，此测试主要保护 flag 不被移除
        from hushai.meditation.core import safety

        for regex, _ in safety._CRISIS_RULES:
            assert regex.flags & __import__("re").IGNORECASE


class TestKnownLimitations:
    """如实记录当前关键词黑名单检测的局限——这些是已知缺陷，非通过测试。

    插入空格/分隔符、使用同音字/拼音即可绕过正则匹配。完整方案需要 LLM
    二次分类（本次修复未引入，见计划「不做的事」）。
    """

    def test_whitespace_obfuscation_bypasses(self):
        """已知局限：插入空格可绕过。记录此局限，提醒未来加固。"""
        # 「活 着 好 累」无法被「活着好累」正则命中
        assert check_safety("活 着 好 累").is_safe

    def test_pinyin_bypasses(self):
        """已知局限：拼音可绕过。"""
        assert check_safety("huo zhe hao lei").is_safe


class TestFormatSafetyMessage:
    def test_safe_result_returns_original(self):
        result = SafetyResult(is_safe=True, level="safe", message=None, suggestion=None)
        assert format_safety_message(result, "原始回复") == "原始回复"

    def test_unsafe_appends_warning(self):
        result = SafetyResult(is_safe=False, level="crisis", message="提示", suggestion="建议")
        out = format_safety_message(result, "原始回复")
        assert "原始回复" in out
        assert "温馨提示" in out
        assert "提示" in out
        assert "建议" in out

    def test_unsafe_with_empty_reply(self):
        """engine.chat 危机分支传入空 reply，应只返回温馨提示。"""
        result = SafetyResult(is_safe=False, level="crisis", message="提示", suggestion="建议")
        out = format_safety_message(result, "")
        assert out.startswith("【温馨提示】")
        assert "原始回复" not in out
