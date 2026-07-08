"""多模型 LLM 路由，支持自动降级。"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from openai import AsyncOpenAI, OpenAIError

from hushai.llm import format_openai_error
from hushai.meditation.config import MeditationConfig, get_config

logger = logging.getLogger(__name__)

_providers: dict[str, dict[str, str]] = {}

DEFAULT_PROVIDER_ORDER = ["deepseek", "zhipu", "kimi", "openai"]


def _init_providers() -> None:
    global _providers
    if _providers:
        return
    cfg = get_config()
    _providers = {
        "openai": {
            "api_key": cfg.openai_api_key,
            "base_url": cfg.openai_base_url or "https://api.openai.com/v1",
            "model": cfg.default_llm_model,
        },
        "deepseek": {
            "api_key": cfg.deepseek_api_key,
            "base_url": cfg.deepseek_base_url,
            "model": cfg.deepseek_model,
        },
        "zhipu": {
            "api_key": cfg.zhipu_api_key,
            "base_url": cfg.zhipu_base_url,
            "model": cfg.zhipu_model,
        },
        "kimi": {
            "api_key": cfg.kimi_api_key,
            "base_url": cfg.kimi_base_url,
            "model": cfg.kimi_model,
        },
    }
    if cfg.llm_providers:
        for name, conf in cfg.llm_providers.items():
            _providers[name] = conf


@dataclass
class LLMMessage:
    role: str
    content: str


def _get_client(provider: str, cfg: MeditationConfig) -> AsyncOpenAI | None:
    """返回配置好的客户端；debug 且无 key 时返回 None（由调用方走 mock 分支）。"""
    _init_providers()
    p = _providers.get(provider)
    if not p or not p.get("api_key"):
        if cfg.debug:
            return None
        raise RuntimeError(f"LLM 提供商 {provider!r} 未配置 API Key")
    return AsyncOpenAI(
        api_key=p["api_key"],
        base_url=p.get("base_url"),
        timeout=120.0 if cfg.debug else 60.0,
    )


def _get_model(provider: str) -> str:
    _init_providers()
    p = _providers.get(provider)
    if not p:
        raise RuntimeError(f"未知的 LLM 提供商: {provider!r}")
    return p.get("model", "gpt-4o-mini")


def _build_fallback_order(primary_provider: str) -> list[str]:
    """构造降级顺序：主 provider 在前，其余按 DEFAULT_PROVIDER_ORDER 补齐并去重。"""
    seen: set[str] = {primary_provider}
    order = [primary_provider]
    for p in DEFAULT_PROVIDER_ORDER:
        if p not in seen:
            seen.add(p)
            order.append(p)
    return order


async def _mock_chat_completion(messages: list[LLMMessage]) -> str:
    """调试模式下无 API Key 时的模拟回复。"""
    return (
        "你好，我是小观。此刻，让我们先回到呼吸上——感受空气轻轻进入身体，"
        "又缓缓离开。我在这里陪伴你，慢慢来，不着急。"
    )


async def _mock_chat_completion_stream(
    messages: list[LLMMessage],
) -> AsyncGenerator[str, None]:
    """调试模式下无 API Key 时的模拟流式回复。"""
    text = (
        "你好，我是小观。此刻，让我们先回到呼吸上——感受空气轻轻进入身体，"
        "又缓缓离开。我在这里陪伴你，慢慢来，不着急。"
    )
    for word in text:
        yield word


async def _chat_completion_single(
    provider: str,
    client: AsyncOpenAI,
    messages: list[dict[str, str]],
    model: str | None,
    temperature: float,
    max_tokens: int,
) -> str | None:
    """单次非流式调用。返回 None 表示该 provider 失败，可继续降级。"""
    actual_model = model or _get_model(provider)
    try:
        resp = await client.chat.completions.create(
            model=actual_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
    except OpenAIError as exc:
        logger.warning("LLM provider %s failed: %s", provider, exc)
        return None


async def chat_completion(
    messages: list[LLMMessage],
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = False,
    enable_fallback: bool = True,
) -> str:
    cfg = get_config()
    primary_provider = provider or cfg.default_llm_provider
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]

    if enable_fallback:
        for p in _build_fallback_order(primary_provider):
            client = _get_client(p, cfg)
            if client is None:
                continue  # debug 且无 key：跳过，尝试下一个 provider
            result = await _chat_completion_single(
                p, client, msg_dicts, model, temperature, max_tokens
            )
            if result is not None:
                if p != primary_provider:
                    logger.info("LLM fallback: %s -> %s", primary_provider, p)
                return result
        # 全部 provider 都无 key（仅 debug 模式可能）或全部失败
        return await _mock_chat_completion(messages)

    client = _get_client(primary_provider, cfg)
    if client is None:
        return await _mock_chat_completion(messages)
    actual_model = model or _get_model(primary_provider)
    try:
        resp = await client.chat.completions.create(
            model=actual_model,
            messages=msg_dicts,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
    except OpenAIError as exc:
        raise RuntimeError(format_openai_error(exc)) from None


async def _stream_single(
    client: AsyncOpenAI,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    """单次流式调用。失败时抛 OpenAIError，由调用方驱动降级。

    注意：本函数含 ``yield``，因此**始终返回一个 generator**，绝不会返回 None。
    旧的实现用 ``return`` 表达「无客户端」，与 generator 语义冲突且使降级
    判定 ``result_gen is not None`` 永远成立——已修正为「客户端是否存在」
    由调用方在调用前用 ``_get_client`` 判断。
    """
    resp = await client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore[arg-type]
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    async for chunk in resp:  # type: ignore[union-attr]
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def chat_completion_stream(
    messages: list[LLMMessage],
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    enable_fallback: bool = True,
) -> AsyncGenerator[str, None]:
    cfg = get_config()
    primary_provider = provider or cfg.default_llm_provider
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]

    if enable_fallback:
        last_exc: OpenAIError | None = None
        for p in _build_fallback_order(primary_provider):
            client = _get_client(p, cfg)
            if client is None:
                continue
            actual_model = model or _get_model(p)
            try:
                if p != primary_provider:
                    logger.info("LLM stream fallback: %s -> %s", primary_provider, p)
                async for chunk in _stream_single(
                    client, actual_model, msg_dicts, temperature, max_tokens
                ):
                    yield chunk
                return
            except OpenAIError as exc:
                logger.warning("LLM stream provider %s failed: %s", p, exc)
                last_exc = exc
                continue
        # 全部 provider 都无 key（仅 debug 模式）或全部失败 → mock
        if last_exc is None:
            async for chunk in _mock_chat_completion_stream(messages):
                yield chunk
            return
        raise RuntimeError(format_openai_error(last_exc)) from None

    client = _get_client(primary_provider, cfg)
    if client is None:
        async for chunk in _mock_chat_completion_stream(messages):
            yield chunk
        return
    actual_model = model or _get_model(primary_provider)
    try:
        async for chunk in _stream_single(client, actual_model, msg_dicts, temperature, max_tokens):
            yield chunk
    except OpenAIError as exc:
        raise RuntimeError(format_openai_error(exc)) from None
