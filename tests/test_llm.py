"""LLM 调用单元测试（mock OpenAI 客户端，无网络）。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_chat_once_returns_message_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")

    fake_msg = MagicMock()
    fake_msg.content = "一句答。"
    fake_choice = MagicMock()
    fake_choice.message = fake_msg
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]
    mock_create = MagicMock(return_value=fake_resp)
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("hushai.llm.OpenAI", return_value=mock_client):
        from hushai.llm import chat_once

        assert chat_once("问题") == "一句答。"
    mock_create.assert_called_once()
    kwargs = mock_create.call_args.kwargs
    assert kwargs["model"]
    assert len(kwargs["messages"]) == 2
    sys0 = kwargs["messages"][0]["content"]
    assert "反焦虑" in sys0


def test_chat_once_pua_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setenv("HUSH_MODE", "pua")

    fake_msg = MagicMock()
    fake_msg.content = "一句答。"
    fake_choice = MagicMock()
    fake_choice.message = fake_msg
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]
    mock_create = MagicMock(return_value=fake_resp)
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("hushai.llm.OpenAI", return_value=mock_client):
        from hushai.llm import chat_once

        assert chat_once("问题") == "一句答。"
    sys0 = mock_create.call_args.kwargs["messages"][0]["content"]
    assert "反PUA" in sys0
    assert "哲理老人" not in sys0


def test_chat_once_respects_plain_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")
    monkeypatch.setenv("HUSH_MODE", "plain")

    fake_msg = MagicMock()
    fake_msg.content = "一句答。"
    fake_choice = MagicMock()
    fake_choice.message = fake_msg
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]
    mock_create = MagicMock(return_value=fake_resp)
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("hushai.llm.OpenAI", return_value=mock_client):
        from hushai.llm import chat_once

        assert chat_once("问题") == "一句答。"
    sys0 = mock_create.call_args.kwargs["messages"][0]["content"]
    assert "反焦虑" not in sys0


def test_chat_once_focus_and_hype_suffix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")

    fake_msg = MagicMock()
    fake_msg.content = "x。"
    fake_choice = MagicMock()
    fake_choice.message = fake_msg
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]
    mock_create = MagicMock(return_value=fake_resp)
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    for mode, needle in (("focus", "反拖延"), ("hype", "激励")):
        monkeypatch.setenv("HUSH_MODE", mode)
        with patch("hushai.llm.OpenAI", return_value=mock_client):
            from hushai.llm import chat_once

            chat_once("?")
        sys0 = mock_create.call_args.kwargs["messages"][0]["content"]
        assert needle in sys0


def test_chat_once_none_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_APPKEY", "sk-test")

    fake_msg = MagicMock()
    fake_msg.content = None
    fake_choice = MagicMock()
    fake_choice.message = fake_msg
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(return_value=fake_resp)

    with patch("hushai.llm.OpenAI", return_value=mock_client):
        from hushai.llm import chat_once

        assert chat_once("x") == ""
