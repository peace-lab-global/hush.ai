"""CLI 行为测试（网络调用已 mock）。"""

from __future__ import annotations

import io
import os
from unittest.mock import patch

import pytest

from hushai.cli import main, run_repl


class _FakeTTYStdin:
    """模拟交互式终端 stdin（isatty 为 True）。"""

    def isatty(self) -> bool:
        return True

    def read(self) -> str:
        return ""


def test_main_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: pytest.TempPathFactory,
) -> None:
    monkeypatch.delenv("LLM_APPKEY", raising=False)
    monkeypatch.setattr(
        "hushai.settings.default_config_path",
        lambda: tmp_path / "nonexistent.json",  # type: ignore[operator]
    )
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())
    assert main(["hello"]) == 1
    err = capsys.readouterr().err
    assert "未配置" in err or "LLM_APPKEY" in err


def test_main_invokes_repl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())

    def fake_repl(*, json_errors: bool = False) -> int:
        return 42

    monkeypatch.setattr("hushai.cli.run_repl", fake_repl)
    assert main([]) == 42


def test_main_one_shot_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    with patch("hushai.cli.chat_once", return_value="悟了。其余不必说。"):
        code = main(["你好"])
    assert code == 0
    out = capsys.readouterr().out.strip()
    assert out == "悟了。"


def test_main_version() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_main_stdin_pipe(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setattr("hushai.cli.sys.stdin", io.StringIO("管道提问"))
    with patch("hushai.cli.chat_once", return_value="答。"):
        assert main([]) == 0
    assert capsys.readouterr().out.strip() == "答。"


def test_main_stdin_empty(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("hushai.cli.sys.stdin", io.StringIO("   "))
    assert main([]) == 1
    assert "空" in capsys.readouterr().err


def test_main_json_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: pytest.TempPathFactory,
) -> None:
    monkeypatch.delenv("LLM_APPKEY", raising=False)
    monkeypatch.setattr(
        "hushai.settings.default_config_path",
        lambda: tmp_path / "nonexistent.json",  # type: ignore[operator]
    )
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())
    assert main(["--json-errors", "hi"]) == 1
    err = capsys.readouterr().err.strip()
    assert '"error"' in err


def test_main_config_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())
    assert main(["--config", "/nonexistent/hush-config.json"]) == 1
    assert "不存在" in capsys.readouterr().err


def test_main_key_from_config_file(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("LLM_APPKEY", raising=False)
    p = tmp_path / "c.json"
    p.write_text('{"llm_appkey": "sk-file"}', encoding="utf-8")
    with patch("hushai.cli.chat_once", return_value="好。"):
        assert main(["--config", str(p), "问"]) == 0
    assert capsys.readouterr().out.strip() == "好。"


def test_repl_quit_immediately(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    assert run_repl() == 0


def test_repl_banner_calm_on_by_default(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.delenv("HUSH_CALM_MODE", raising=False)
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    assert run_repl() == 0
    assert "慢慢来" in capsys.readouterr().out


def test_repl_banner_plain_mode(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setenv("HUSH_MODE", "plain")
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    assert run_repl() == 0
    out = capsys.readouterr().out
    assert "问一句，答一句" in out
    assert "慢慢来" not in out


def test_main_no_calm_flag_sets_hush_mode_plain(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    with patch("hushai.cli.chat_once", return_value="嗯。"):
        assert main(["--no-calm"]) == 0
    assert os.environ.get("HUSH_MODE") == "plain"


def test_main_mode_focus_banner(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    assert main(["--mode", "focus"]) == 0
    assert "最小一步" in capsys.readouterr().out


def test_main_mode_pua_banner(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setattr("hushai.cli.sys.stdin", _FakeTTYStdin())
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    assert main(["--mode", "pua"]) == 0
    assert "反PUA" in capsys.readouterr().out


def test_repl_skips_empty_input(monkeypatch: pytest.MonkeyPatch) -> None:
    seq = iter(["", "  ", "q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(seq))
    assert run_repl() == 0


def test_repl_eof(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", boom)
    assert run_repl() == 0


def test_repl_runtime_error_from_llm(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setattr("builtins.input", lambda _="": "问")
    with patch("hushai.cli.chat_once", side_effect=RuntimeError("服务不可用")):
        assert run_repl() == 1
    err = capsys.readouterr().err
    assert "服务不可用" in err


def test_repl_one_round_then_quit(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    seq = iter(["你好", "q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(seq))
    with patch("hushai.cli.chat_once", return_value="嗯。"):
        assert run_repl() == 0
    out = capsys.readouterr().out
    assert "嗯。" in out


def test_main_non_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    with patch("hushai.cli.chat_once", side_effect=ValueError("bad")):
        assert main(["x"]) == 1
    assert "请求失败" in capsys.readouterr().err


def test_repl_generic_api_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")

    def once() -> str:
        raise RuntimeError("network down")

    monkeypatch.setattr("builtins.input", lambda _="": "问一句")
    with patch("hushai.cli.chat_once", side_effect=once):
        assert run_repl() == 1
    err = capsys.readouterr().err
    assert "请求失败" in err
