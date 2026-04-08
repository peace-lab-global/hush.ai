"""多模型 LLM 路由。"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from hushai.meditation.config import MeditationConfig, get_config

_providers: dict[str, dict[str, str]] = {}


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
    }
    if cfg.llm_providers:
        for name, conf in cfg.llm_providers.items():
            _providers[name] = conf


@dataclass
class LLMMessage:
    role: str
    content: str


def _get_client(provider: str, cfg: MeditationConfig) -> AsyncOpenAI:
    _init_providers()
    p = _providers.get(provider)
    if not p or not p.get("api_key"):
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


async def chat_completion(
    messages: list[LLMMessage],
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = False,
) -> str:
    cfg = get_config()
    provider = provider or cfg.default_llm_provider
    client = _get_client(provider, cfg)
    model = model or _get_model(provider)
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": msg_dicts,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }
    resp = await client.chat.completions.create(**kwargs)
    if stream:
        parts: list[str] = []
        async for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:
                parts.append(delta)
        return "".join(parts)
    return resp.choices[0].message.content or ""


async def chat_completion_stream(
    messages: list[LLMMessage],
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> AsyncGenerator[str, None]:
    cfg = get_config()
    provider = provider or cfg.default_llm_provider
    client = _get_client(provider, cfg)
    model = model or _get_model(provider)
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
    resp = await client.chat.completions.create(
        model=model,
        messages=msg_dicts,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    async for chunk in resp:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
