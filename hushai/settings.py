"""配置解析：环境变量优先于配置文件（JSON）。"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Final

_CONFIG_DATA: dict[str, Any] = {}
_CONFIG_PATH: Path | None = None

# 对话模式：calm 反焦虑 | focus 反拖延 | hype 激励 | plain 仅基础 | pua 反PUA演练
VALID_MODES: Final[frozenset[str]] = frozenset({"calm", "focus", "hype", "plain", "pua"})
_DEFAULT_MODE: Final[str] = "calm"


def _env(name: str) -> str | None:
    v = os.environ.get(name)
    if v is None:
        return None
    v = v.strip()
    return v if v else None


def _truthy_string(s: str, *, default: bool) -> bool:
    sl = s.strip().lower()
    if sl in ("1", "true", "yes", "on", "y"):
        return True
    if sl in ("0", "false", "no", "off", "n"):
        return False
    return default


def _parse_mode_strict(raw: str) -> str:
    s = raw.strip().lower()
    aliases = {
        "anti-anxiety": "calm",
        "anxiety": "calm",
        "anti-procrastination": "focus",
        "procrastination": "focus",
        "pump": "hype",
        "energy": "hype",
        "none": "plain",
        "zen": "plain",
        "anti-pua": "pua",
        "antipua": "pua",
        "drill": "pua",
    }
    s = aliases.get(s, s)
    if s in VALID_MODES:
        return s
    raise RuntimeError(f"无效模式: {raw!r}。可选: calm, focus, hype, plain, pua（反PUA演练）")


def default_config_path() -> Path:
    """默认配置文件路径（Linux/macOS：`~/.config/hush/config.json`；Windows：`%APPDATA%\\hush\\config.json`）。"""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "hush" / "config.json"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "hush" / "config.json"
    return Path.home() / ".config" / "hush" / "config.json"


def _resolve_path(cli_config: str | None) -> tuple[Path | None, bool]:
    """
    返回 (路径或 None, 是否为用户显式指定)。
    显式路径缺失时在 configure() 中报错。
    """
    if cli_config:
        return Path(cli_config).expanduser(), True
    env_p = _env("HUSH_CONFIG")
    if env_p:
        return Path(env_p).expanduser(), True
    default = default_config_path()
    if default.is_file():
        return default, False
    return None, False


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"配置文件 JSON 无效: {path}: {e}"
        raise RuntimeError(msg) from None
    if not isinstance(raw, dict):
        msg = f"配置文件必须是 JSON 对象: {path}"
        raise RuntimeError(msg)
    return raw


def configure(cli_config: str | None) -> None:
    """在进程入口调用一次：解析并缓存配置文件内容。"""
    global _CONFIG_DATA, _CONFIG_PATH
    path, explicit = _resolve_path(cli_config)
    if explicit and path is not None and not path.is_file():
        msg = f"配置文件不存在: {path}"
        raise RuntimeError(msg)
    _CONFIG_PATH = path
    _CONFIG_DATA = _load_json(path) if path is not None and path.is_file() else {}
    try:
        get_mode()
    except RuntimeError:
        _CONFIG_DATA = {}
        _CONFIG_PATH = None
        raise


def config_path() -> Path | None:
    return _CONFIG_PATH


def _from_file(key: str) -> Any | None:
    return _CONFIG_DATA.get(key)


def get_api_key() -> str | None:
    v = _env("LLM_APPKEY")
    if v is not None:
        return v
    x = _from_file("llm_appkey")
    if x is None:
        return None
    s = str(x).strip()
    return s if s else None


def get_base_url() -> str | None:
    v = _env("OPENAI_BASE_URL")
    if v is not None:
        return v
    x = _from_file("openai_base_url")
    if x is None:
        return None
    s = str(x).strip()
    return s if s else None


def get_mode() -> str:
    """
    对话模式。

    优先级：HUSH_MODE > hush_mode（文件）> 旧版 HUSH_CALM_MODE / hush_calm_mode > 默认 calm。

    calm / focus / hype / plain / pua 含义见 README。
    """
    v = _env("HUSH_MODE")
    if v is not None:
        return _parse_mode_strict(v)
    x = _from_file("hush_mode")
    if x is not None:
        return _parse_mode_strict(str(x))
    # 兼容旧版布尔开关
    cm = _env("HUSH_CALM_MODE")
    if cm is not None:
        return "calm" if _truthy_string(cm, default=True) else "plain"
    xc = _from_file("hush_calm_mode")
    if xc is not None:
        if isinstance(xc, bool):
            return "calm" if xc else "plain"
        if isinstance(xc, (int, float)):
            return "calm" if xc else "plain"
        if isinstance(xc, str):
            return "calm" if _truthy_string(xc, default=True) else "plain"
    return _DEFAULT_MODE


def get_model() -> str:
    v = _env("LLM_MODEL")
    if v is not None:
        return v
    x = _from_file("llm_model")
    if x is None:
        return "gpt-4o-mini"
    s = str(x).strip()
    return s if s else "gpt-4o-mini"


_DEFAULT_TIMEOUT: Final[float] = 60.0
_DEFAULT_RETRIES: Final[int] = 2


def get_timeout_seconds() -> float:
    v = _env("LLM_TIMEOUT")
    if v is not None:
        try:
            return max(1.0, float(v))
        except ValueError:
            return _DEFAULT_TIMEOUT
    x = _from_file("llm_timeout")
    if x is not None:
        try:
            return max(1.0, float(x))
        except (TypeError, ValueError):
            return _DEFAULT_TIMEOUT
    return _DEFAULT_TIMEOUT


def get_max_retries() -> int:
    v = _env("LLM_MAX_RETRIES")
    if v is not None:
        try:
            return max(0, int(v))
        except ValueError:
            return _DEFAULT_RETRIES
    x = _from_file("llm_max_retries")
    if x is not None:
        try:
            return max(0, int(x))
        except (TypeError, ValueError):
            return _DEFAULT_RETRIES
    return _DEFAULT_RETRIES


def reset_for_tests() -> None:
    """测试用：清空缓存。"""
    global _CONFIG_DATA, _CONFIG_PATH
    _CONFIG_DATA = {}
    _CONFIG_PATH = None
