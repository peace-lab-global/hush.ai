"""测试 core/llm.py — LLM 适配层（区别于测顶层 hushai/llm.py 的 test_llm.py）。

验证 P0 修复：
- _chat_completion_stream_single 不再含「return None」语义陷阱（generator 类型 Bug）
- fallback 顺序正确且去重
- _build_fallback_order 公用辅助
- debug 无 key 时走 mock
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import OpenAIError

from hushai.meditation import config as cfg_module
from hushai.meditation.core import llm


@pytest.fixture(autouse=True)
def _test_config():
    cfg_module.set_config(
        cfg_module.MeditationConfig(
            debug=False,
            jwt_secret="test",
            openai_api_key="sk-openai",
            deepseek_api_key="sk-deepseek",
            zhipu_api_key="sk-zhipu",
            kimi_api_key="sk-kimi",
            default_llm_provider="openai",
        )
    )
    # 重置 provider 缓存，确保每个测试读到新配置
    llm._providers = {}
    yield
    cfg_module.reset_config()
    llm._providers = {}


class TestBuildFallbackOrder:
    def test_primary_first(self):
        """主 provider 应在最前。"""
        order = llm._build_fallback_order("openai")
        assert order[0] == "openai"

    def test_no_duplicates(self):
        """P0 修复：列表推导不应产生重复（旧代码 tried 集合为空导致死代码）。"""
        order = llm._build_fallback_order("openai")
        assert len(order) == len(set(order))
        # 应包含全部 4 个 provider
        assert set(order) == {"openai", "deepseek", "zhipu", "kimi"}

    def test_custom_primary_not_in_defaults(self):
        """主 provider 不在 DEFAULT_PROVIDER_ORDER 时也应正确。"""
        order = llm._build_fallback_order("custom-provider")
        assert order[0] == "custom-provider"
        assert order[1:] == llm.DEFAULT_PROVIDER_ORDER


class TestStreamSingleIsPureGenerator:
    """P0 核心修复：_stream_single 含 yield 必然返回 generator。

    旧实现 _chat_completion_stream_single 用 ``return`` 表达「无客户端」，
    但 generator function 的 return 永远不返回 None，导致调用方
    ``result_gen is not None`` 判定失效。新设计把「客户端是否存在」移到
    调用方，_stream_single 只负责流式拉取。
    """

    @pytest.mark.asyncio
    async def test_stream_single_yields_deltas(self):
        client = MagicMock()
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock(delta=MagicMock(content="Hello"))]
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock(delta=MagicMock(content=" World"))]

        async def _aiter():
            yield chunk1
            yield chunk2

        client.chat.completions.create = AsyncMock(return_value=_aiter())

        deltas = []
        async for d in llm._stream_single(client, "model", [], 0.7, 100):
            deltas.append(d)
        assert deltas == ["Hello", " World"]

    @pytest.mark.asyncio
    async def test_stream_single_propagates_openai_error(self):
        """失败时抛 OpenAIError，由调用方驱动 fallback。"""
        client = MagicMock()
        client.chat.completions.create = AsyncMock(
            side_effect=OpenAIError("boom")  # type: ignore[arg-type]
        )
        with pytest.raises(OpenAIError):
            async for _ in llm._stream_single(client, "model", [], 0.7, 100):
                pass


class TestChatCompletionFallback:
    @pytest.mark.asyncio
    async def test_fallback_when_primary_fails(self):
        """主 provider 失败时应降级到下一个。"""
        call_log: list[str] = []

        async def _fake_single(provider, client, msgs, model, temp, max_tok):
            call_log.append(provider)
            if provider == "openai":
                return None  # 主 provider 失败
            return "fallback-reply"

        with patch.object(llm, "_chat_completion_single", side_effect=_fake_single):
            result = await llm.chat_completion(
                [llm.LLMMessage(role="user", content="hi")],
                provider="openai",
            )
        assert result == "fallback-reply"
        assert call_log[0] == "openai"
        assert "deepseek" in call_log  # 降级到了下一个

    @pytest.mark.asyncio
    async def test_fallback_stream_uses_try_except(self):
        """流式 fallback 应通过 try/except 驱动（修复 generator None 陷阱）。"""
        call_log: list[str] = []

        def _make_stream_gen(should_fail: bool):
            async def _gen(client, model, msgs, temp, max_tok):
                call_log.append(model)
                if should_fail:
                    raise OpenAIError("primary failed")  # type: ignore[arg-type]
                yield "ok"

            return _gen

        primary_client = MagicMock()
        fallback_client = MagicMock()

        def _get_client(provider, cfg):
            if provider == "openai":
                return primary_client
            return fallback_client

        with (
            patch.object(llm, "_get_client", side_effect=_get_client),
            patch.object(llm, "_stream_single", side_effect=_make_stream_gen(should_fail=False)),
        ):
            deltas = []
            async for d in llm.chat_completion_stream(
                [llm.LLMMessage(role="user", content="hi")],
                provider="openai",
            ):
                deltas.append(d)
        assert deltas == ["ok"]


class TestDebugMockFallback:
    @pytest.mark.asyncio
    async def test_debug_no_key_uses_mock(self):
        """debug 且无 key 时应返回 mock 回复（不报错）。"""
        cfg_module.set_config(cfg_module.MeditationConfig(debug=True, jwt_secret="t"))
        llm._providers = {}
        result = await llm.chat_completion(
            [llm.LLMMessage(role="user", content="hi")],
            enable_fallback=True,
        )
        assert isinstance(result, str)
        assert "小观" in result
