"""远程知识源测试 — 覆盖适配器配置解析、文件名提取、HTTP 抓取等纯逻辑。

不发起真实网络请求，httpx 桩由 ``monkeypatch`` 注入。
"""

from __future__ import annotations

from typing import Any

import pytest

from hushai.meditation.core import remote_knowledge as rk
from hushai.meditation.core.remote_knowledge import (
    CozeSourceAdapter,
    IMASourceAdapter,
    RemoteDocument,
    URLSourceAdapter,
    _resolve_filename_from_url,
)

# ---------------------------------------------------------------------------
# _resolve_filename_from_url（纯函数）
# ---------------------------------------------------------------------------


def test_resolve_filename_basic() -> None:
    assert _resolve_filename_from_url("https://example.com/path/to/doc.md") == "doc.md"


def test_resolve_filename_with_query() -> None:
    assert _resolve_filename_from_url("https://example.com/x.md?ref=1&v=2") == "x.md"


def test_resolve_filename_with_fragment() -> None:
    assert _resolve_filename_from_url("https://example.com/x.md#section") == "x.md"


def test_resolve_filename_trailing_slash() -> None:
    assert _resolve_filename_from_url("https://example.com/") == "remote_doc.md"


def test_resolve_filename_no_slash() -> None:
    """无路径段时直接返回原字符串（不是默认占位）。"""
    # 行为: 无 `/` 时 rsplit 仍返回原字符串
    assert _resolve_filename_from_url("not-a-url") == "not-a-url"


# ---------------------------------------------------------------------------
# URLSourceAdapter
# ---------------------------------------------------------------------------


def test_url_source_label() -> None:
    assert URLSourceAdapter().source_label() == "url"


@pytest.mark.asyncio
async def test_url_adapter_empty_config() -> None:
    docs = await URLSourceAdapter().list_documents({})
    assert docs == []


@pytest.mark.asyncio
async def test_url_adapter_blank_lines() -> None:
    docs = await URLSourceAdapter().list_documents({"urls": "   \n\n   \n"})
    assert docs == []


@pytest.mark.asyncio
async def test_url_adapter_with_comments_and_urls() -> None:
    config = {
        "urls": """
        # 这是注释
        https://example.com/a.md
        https://example.com/b.md

        # 另一个注释
        https://example.com/c.md
        """
    }
    docs = await URLSourceAdapter().list_documents(config)
    assert len(docs) == 3
    assert [d.url for d in docs] == [
        "https://example.com/a.md",
        "https://example.com/b.md",
        "https://example.com/c.md",
    ]
    for d in docs:
        assert d.source == "url"
        assert d.title == ""
        assert d.tags == []


# ---------------------------------------------------------------------------
# CozeSourceAdapter
# ---------------------------------------------------------------------------


def test_coze_source_label() -> None:
    assert CozeSourceAdapter().source_label() == "coze"


@pytest.mark.asyncio
async def test_coze_adapter_missing_token() -> None:
    """缺 token / dataset_id 应直接返回空列表，不发请求。"""
    docs = await CozeSourceAdapter().list_documents({"dataset_id": "ds1"})
    assert docs == []


@pytest.mark.asyncio
async def test_coze_adapter_missing_dataset() -> None:
    docs = await CozeSourceAdapter().list_documents({"api_token": "tok"})
    assert docs == []


class _CozeFakeClient:
    """按 URL 路径返回不同响应的 Coze API 桩。"""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []
        self._index = 0

    async def __aenter__(self) -> "_CozeFakeClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    async def get(self, url: str, headers: dict[str, str], params: dict[str, Any]) -> Any:
        self.calls.append({"url": url, "headers": headers, "params": params})
        if self._index >= len(self.responses):
            raise AssertionError("more calls than responses")
        resp = self.responses[self._index]
        self._index += 1

        class _Resp:
            def __init__(self, data: dict[str, Any]) -> None:
                self._data = data

            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict[str, Any]:
                return self._data

        return _Resp(resp)


@pytest.mark.asyncio
async def test_coze_adapter_success_single_page(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _CozeFakeClient(
        [
            {
                "code": 0,
                "data": {
                    "total": 2,
                    "document_list": [
                        {"document_id": "doc-1", "name": "文档一"},
                        {"document_id": "doc-2", "title": "文档二"},
                    ],
                },
            }
        ]
    )
    monkeypatch.setattr(rk.httpx, "AsyncClient", lambda *a, **kw: client)
    docs = await CozeSourceAdapter().list_documents(
        {
            "api_token": "pat_xxx",
            "dataset_id": "ds-42",
            "api_base": "https://api.coze.cn/",  # 末尾 / 测试裁剪
        }
    )
    assert len(docs) == 2
    assert docs[0].title == "文档一"
    assert docs[0].url.endswith("/v1/knowledge/document/doc-1")
    assert docs[0].tags == ["coze"]
    assert docs[0].source == "coze"
    # 末尾 / 被裁剪
    assert client.calls[0]["url"].startswith("https://api.coze.cn/v1/")


@pytest.mark.asyncio
async def test_coze_adapter_pagination(monkeypatch: pytest.MonkeyPatch) -> None:
    """分页：page_size=50，total=120 → 需要 3 次请求。"""
    client = _CozeFakeClient(
        [
            {
                "code": 0,
                "data": {
                    "total": 120,
                    "document_list": [
                        {"document_id": f"d-{i}", "name": f"D{i}"} for i in range(50)
                    ],
                },
            },
            {
                "code": 0,
                "data": {
                    "total": 120,
                    "document_list": [
                        {"document_id": f"d-{i}", "name": f"D{i}"} for i in range(50, 100)
                    ],
                },
            },
            {
                "code": 0,
                "data": {
                    "total": 120,
                    "document_list": [
                        {"document_id": f"d-{i}", "name": f"D{i}"} for i in range(100, 120)
                    ],
                },
            },
        ]
    )
    monkeypatch.setattr(rk.httpx, "AsyncClient", lambda *a, **kw: client)
    docs = await CozeSourceAdapter().list_documents({"api_token": "tok", "dataset_id": "ds"})
    assert len(docs) == 120
    assert len(client.calls) == 3
    assert client.calls[1]["params"]["page_num"] == 2
    assert client.calls[2]["params"]["page_num"] == 3


@pytest.mark.asyncio
async def test_coze_adapter_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """code != 0 时立即停止。"""
    client = _CozeFakeClient(
        [
            {"code": 4001, "msg": "rate limited", "data": {}},
        ]
    )
    monkeypatch.setattr(rk.httpx, "AsyncClient", lambda *a, **kw: client)
    docs = await CozeSourceAdapter().list_documents({"api_token": "tok", "dataset_id": "ds"})
    assert docs == []


@pytest.mark.asyncio
async def test_coze_adapter_http_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """网络异常时停止并返回已收集的文档。"""

    class _ExplodingClient:
        async def __aenter__(self) -> "_ExplodingClient":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("network down")

    monkeypatch.setattr(rk.httpx, "AsyncClient", lambda *a, **kw: _ExplodingClient())
    docs = await CozeSourceAdapter().list_documents({"api_token": "tok", "dataset_id": "ds"})
    assert docs == []


# ---------------------------------------------------------------------------
# IMASourceAdapter
# ---------------------------------------------------------------------------


def test_ima_source_label() -> None:
    assert IMASourceAdapter().source_label() == "ima"


@pytest.mark.asyncio
async def test_ima_adapter_empty() -> None:
    docs = await IMASourceAdapter().list_documents({})
    assert docs == []


@pytest.mark.asyncio
async def test_ima_adapter_uses_urls_field() -> None:
    """IMA 适配器从 urls 字段读 URL。"""
    config = {"urls": "https://ima.qq.com/a\nhttps://ima.qq.com/b\n# 注释\n\nhttps://ima.qq.com/c"}
    docs = await IMASourceAdapter().list_documents(config)
    assert len(docs) == 3
    assert all(d.source == "ima" and d.tags == ["ima"] for d in docs)


@pytest.mark.asyncio
async def test_ima_adapter_skips_comments() -> None:
    docs = await IMASourceAdapter().list_documents(
        {"urls": "# 顶部注释\nhttps://ima.qq.com/x\n# 另一个\nhttps://ima.qq.com/y"}
    )
    assert [d.url for d in docs] == ["https://ima.qq.com/x", "https://ima.qq.com/y"]


# ---------------------------------------------------------------------------
# _fetch_single
# ---------------------------------------------------------------------------


class _FetchFakeClient:
    def __init__(self, response: Any) -> None:
        self._response = response
        self.calls: list[dict[str, Any]] = []

    async def __aenter__(self) -> "_FetchFakeClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    async def get(self, url: str, headers: dict[str, str] | None = None, **kwargs: Any) -> Any:
        self.calls.append({"url": url, "headers": headers})
        return self._response


@pytest.mark.asyncio
async def test_fetch_single_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        status_code = 200
        text = "# 标题\n\n正文内容"
        headers = {"Content-Type": "text/markdown"}

        def raise_for_status(self) -> None:
            pass

    client = _FetchFakeClient(_Resp())
    monkeypatch.setattr(rk.httpx, "AsyncClient", lambda *a, **kw: client)
    result = await rk._fetch_single(client, RemoteDocument(url="https://x/y.md", source="url"))
    assert result is not None
    content, title, tags, source = result
    assert content == "# 标题\n\n正文内容"
    assert source == "url"
    assert "User-Agent" in (client.calls[0]["headers"] or {})


@pytest.mark.asyncio
async def test_fetch_single_http_error_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        status_code = 404
        text = "not found"

        def raise_for_status(self) -> None:
            raise RuntimeError("404")

    client = _FetchFakeClient(_Resp())
    monkeypatch.setattr(rk.httpx, "AsyncClient", lambda *a, **kw: client)
    result = await rk._fetch_single(
        client, RemoteDocument(url="https://x/missing.md", source="url")
    )
    assert result is None


# ---------------------------------------------------------------------------
# _ADAPTERS registry
# ---------------------------------------------------------------------------


def test_adapters_registry() -> None:
    """注册表应包含全部三个内置适配器。"""
    assert "url" in rk._ADAPTERS
    assert "coze" in rk._ADAPTERS
    assert "ima" in rk._ADAPTERS
    assert rk._ADAPTERS["url"].source_label() == "url"
    assert rk._ADAPTERS["coze"].source_label() == "coze"
    assert rk._ADAPTERS["ima"].source_label() == "ima"
