"""冥想模块专用配置。"""

from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MeditationConfig:
    postgres_url: str = ""
    chroma_persist_dir: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    wx_appid: str = ""
    wx_secret: str = ""
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    openai_base_url: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    zhipu_api_key: str = ""
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    zhipu_model: str = "glm-4-flash"
    memory_top_k: int = 5
    knowledge_top_k: int = 3
    conversation_max_turns: int = 20
    memory_extraction_model: str = ""
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = field(default_factory=list)
    llm_providers: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> MeditationConfig:
        d: dict[str, Any] = {}
        mapping = {
            "MEDITATION_POSTGRES_URL": ("postgres_url", str),
            "MEDITATION_CHROMA_DIR": ("chroma_persist_dir", str),
            "MEDITATION_JWT_SECRET": ("jwt_secret", str),
            "MEDITATION_JWT_ALGORITHM": ("jwt_algorithm", str),
            "MEDITATION_JWT_EXPIRE_MINUTES": ("jwt_expire_minutes", int),
            "MEDITATION_WX_APPID": ("wx_appid", str),
            "MEDITATION_WX_SECRET": ("wx_secret", str),
            "MEDITATION_DEFAULT_LLM_PROVIDER": ("default_llm_provider", str),
            "MEDITATION_DEFAULT_LLM_MODEL": ("default_llm_model", str),
            "MEDITATION_OPENAI_API_KEY": ("openai_api_key", str),
            "MEDITATION_OPENAI_BASE_URL": ("openai_base_url", str),
            "MEDITATION_DEEPSEEK_API_KEY": ("deepseek_api_key", str),
            "MEDITATION_DEEPSEEK_BASE_URL": ("deepseek_base_url", str),
            "MEDITATION_DEEPSEEK_MODEL": ("deepseek_model", str),
            "MEDITATION_ZHIPU_API_KEY": ("zhipu_api_key", str),
            "MEDITATION_ZHIPU_BASE_URL": ("zhipu_base_url", str),
            "MEDITATION_ZHIPU_MODEL": ("zhipu_model", str),
            "MEDITATION_MEMORY_TOP_K": ("memory_top_k", int),
            "MEDITATION_KNOWLEDGE_TOP_K": ("knowledge_top_k", int),
            "MEDITATION_CONVERSATION_MAX_TURNS": ("conversation_max_turns", int),
            "MEDITATION_EMBEDDING_PROVIDER": ("embedding_provider", str),
            "MEDITATION_EMBEDDING_MODEL": ("embedding_model", str),
            "MEDITATION_EMBEDDING_API_KEY": ("embedding_api_key", str),
            "MEDITATION_EMBEDDING_BASE_URL": ("embedding_base_url", str),
            "MEDITATION_HOST": ("host", str),
            "MEDITATION_PORT": ("port", int),
            "MEDITATION_DEBUG": ("debug", bool),
        }
        for env_key, (field_name, typ) in mapping.items():
            val = os.environ.get(env_key)
            if val is None:
                continue
            if typ is bool:
                d[field_name] = val.lower() in ("1", "true", "yes", "on")
            elif typ is int:
                with contextlib.suppress(ValueError):
                    d[field_name] = int(val)
            else:
                d[field_name] = val
        return cls(**d)


_config: MeditationConfig | None = None


def get_config() -> MeditationConfig:
    global _config
    if _config is None:
        _config = MeditationConfig.from_env()
    return _config


def set_config(cfg: MeditationConfig) -> None:
    global _config
    _config = cfg


def reset_config() -> None:
    global _config
    _config = None
