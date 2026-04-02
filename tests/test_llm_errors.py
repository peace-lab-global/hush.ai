"""OpenAI 异常文案映射。"""

from __future__ import annotations

import httpx
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    RateLimitError,
)

from hushai.llm import format_openai_error


def _req() -> httpx.Request:
    return httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def _resp(status: int) -> httpx.Response:
    return httpx.Response(status, request=_req())


def test_format_timeout() -> None:
    exc = APITimeoutError(request=_req())
    assert "超时" in format_openai_error(exc)


def test_format_connection() -> None:
    exc = APIConnectionError(message="x", request=_req())
    assert "连接" in format_openai_error(exc)


def test_format_rate_limit() -> None:
    exc = RateLimitError(message="rl", response=_resp(429), body=None)
    assert "频繁" in format_openai_error(exc)


def test_format_auth() -> None:
    exc = AuthenticationError("bad", response=_resp(401), body=None)
    assert "密钥" in format_openai_error(exc)


def test_format_permission_denied() -> None:
    exc = PermissionDeniedError("pd", response=_resp(403), body=None)
    assert "权限" in format_openai_error(exc)


def test_format_status_generic() -> None:
    exc = InternalServerError(message="ise", response=_resp(502), body=None)
    assert "502" in format_openai_error(exc)


def test_format_non_openai_error() -> None:
    out = format_openai_error(ValueError("x"))
    assert "请求失败" in out
