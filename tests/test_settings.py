"""配置与环境合并。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hushai.settings import (
    configure,
    default_config_path,
    get_api_key,
    get_max_retries,
    get_mode,
    get_model,
    get_timeout_seconds,
    reset_for_tests,
)


def _tmp_config_path(monkeypatch: pytest.MonkeyPatch) -> Path:
    """返回一个不存在的临时配置路径，避免测试读取本机配置文件。"""
    import tempfile

    return Path(tempfile.mkdtemp()) / "nonexistent_hush_config.json"


def test_invalid_json_raises(tmp_path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(RuntimeError, match="JSON"):
        configure(str(p))


def test_env_overrides_file(tmp_path, monkeypatch) -> None:
    p = tmp_path / "c.json"
    payload = {"llm_appkey": "from-file", "llm_model": "from-model"}
    p.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv("LLM_APPKEY", "from-env")
    configure(str(p))
    assert get_api_key() == "from-env"
    assert get_model() == "from-model"


def test_file_key_when_env_unset(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("LLM_APPKEY", raising=False)
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"llm_appkey": "k"}), encoding="utf-8")
    configure(str(p))
    assert get_api_key() == "k"


def test_defaults(monkeypatch) -> None:
    monkeypatch.delenv("LLM_APPKEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_TIMEOUT", raising=False)
    monkeypatch.delenv("LLM_MAX_RETRIES", raising=False)
    monkeypatch.delenv("HUSH_MODE", raising=False)
    monkeypatch.setattr(
        "hushai.settings.default_config_path",
        lambda: _tmp_config_path(monkeypatch),
    )
    reset_for_tests()
    configure(None)
    assert get_api_key() is None
    assert get_model() == "gpt-4o-mini"
    assert get_timeout_seconds() == 60.0
    assert get_max_retries() == 2
    assert get_mode() == "calm"


def test_mode_legacy_and_hush_mode_priority(monkeypatch) -> None:
    monkeypatch.delenv("HUSH_MODE", raising=False)
    monkeypatch.delenv("HUSH_CALM_MODE", raising=False)
    reset_for_tests()
    configure(None)
    assert get_mode() == "calm"

    monkeypatch.setenv("HUSH_CALM_MODE", "0")
    assert get_mode() == "plain"

    monkeypatch.setenv("HUSH_CALM_MODE", "1")
    assert get_mode() == "calm"

    monkeypatch.setenv("HUSH_MODE", "focus")
    assert get_mode() == "focus"


def test_pua_mode_alias(monkeypatch) -> None:
    monkeypatch.setenv("HUSH_MODE", "anti-pua")
    assert get_mode() == "pua"


def test_hush_mode_from_file(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("HUSH_MODE", raising=False)
    monkeypatch.delenv("HUSH_CALM_MODE", raising=False)
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"llm_appkey": "k", "hush_mode": "hype"}), encoding="utf-8")
    configure(str(p))
    assert get_mode() == "hype"


def test_invalid_hush_mode_env(monkeypatch) -> None:
    monkeypatch.setenv("HUSH_MODE", "nope")
    reset_for_tests()
    with pytest.raises(RuntimeError, match="无效模式"):
        configure(None)


def test_default_config_path_shape(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    p = default_config_path()
    assert p.name == "config.json"
    assert "hush" in p.parts
