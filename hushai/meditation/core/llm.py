"""多模型 LLM 路由，支持自动降级。"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

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


async def _mock_chat_completion(messages: list[LLMMessage]) -> str:
    """调试模式下无 API Key 时的模拟回复。"""
    return "你好，我是小观。此刻，让我们先回到呼吸上——感受空气轻轻进入身体，又缓缓离开。我在这里陪伴你，慢慢来，不着急。"


async def _mock_chat_completion_stream(
    messages: list[LLMMessage],
) -> AsyncGenerator[str, None]:
    """调试模式下无 API Key 时的模拟流式回复。"""
    text = "你好，我是小观。此刻，让我们先回到呼吸上——感受空气轻轻进入身体，又缓缓离开。我在这里陪伴你，慢慢来，不着急。"
    for word in text:
        yield word


def _get_model(provider: str) -> str:
    _init_providers()
    p = _providers.get(provider)
    if not p:
        raise RuntimeError(f"未知的 LLM 提供商: {provider!r}")
    return p.get("model", "gpt-4o-mini")


async def _chat_completion_single(
    provider: str,
    messages: list[dict[str, str]],
    model: str | None,
    temperature: float,
    max_tokens: int,
) -> str | None:
    cfg = get_config()
    client = _get_client(provider, cfg)
    if client is None:
        return None
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
        tried: set[str] = set()
        providers_to_try = [primary_provider] + [
            p for p in DEFAULT_PROVIDER_ORDER if p != primary_provider and p not in tried
        ]

        for p in providers_to_try:
            tried.add(p)
            result = await _chat_completion_single(p, msg_dicts, model, temperature, max_tokens)
            if result is not None:
                if p != primary_provider:
                    logger.info("LLM fallback: %s -> %s", primary_provider, p)
                return result

        client = _get_client(primary_provider, cfg)
        if client is None:
            return await _mock_chat_completion(messages)
        raise RuntimeError("所有 LLM 提供商均不可用")

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


async def _chat_completion_stream_single(
    provider: str,
    messages: list[dict[str, str]],
    model: str | None,
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None] | None:
    cfg = get_config()
    client = _get_client(provider, cfg)
    if client is None:
        return
    actual_model = model or _get_model(provider)
    try:
        resp = await client.chat.completions.create(
            model=actual_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
        return
    except OpenAIError as exc:
        logger.warning("LLM stream provider %s failed: %s", provider, exc)
        return


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
        tried: set[str] = set()
        providers_to_try = [primary_provider] + [
            p for p in DEFAULT_PROVIDER_ORDER if p != primary_provider and p not in tried
        ]

        for p in providers_to_try:
            tried.add(p)
            result_gen = await _chat_completion_stream_single(
                p, msg_dicts, model, temperature, max_tokens
            )
            if result_gen is not None:
                if p != primary_provider:
                    logger.info("LLM stream fallback: %s -> %s", primary_provider, p)
                async for chunk in result_gen:
                    yield chunk
                return

        async for chunk in _mock_chat_completion_stream(messages):
            yield chunk
        return

    client = _get_client(primary_provider, cfg)
    if client is None:
        async for chunk in _mock_chat_completion_stream(messages):
            yield chunk
        return
    actual_model = model or _get_model(primary_provider)
    try:
        resp = await client.chat.completions.create(
            model=actual_model,
            messages=msg_dicts,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except OpenAIError as exc:
        raise RuntimeError(format_openai_error(exc)) from None
