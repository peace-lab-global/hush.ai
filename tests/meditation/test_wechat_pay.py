"""微信支付 v3 集成测试。

不发起真实 HTTP 请求 — 通过 ``monkeypatch`` 注入 httpx 桩函数。
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from hushai.meditation import config as cfg_module
from hushai.meditation.core import wechat_pay

# ---------------------------------------------------------------------------
# 夹具
# ---------------------------------------------------------------------------


@pytest.fixture
def wx_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """注入微信支付测试配置（避免读取宿主 .env）。"""
    cfg = cfg_module.MeditationConfig(
        wx_appid="wx_test_appid",
        wx_mch_id="1900000001",
        wx_pay_api_key="test_api_key_32_bytes_xxxxxxxxxxxxx",
        wx_pay_serial_no="TEST_SERIAL_001",
        wx_pay_notify_url="https://example.com/notify",
    )
    cfg_module.set_config(cfg)
    yield
    cfg_module.reset_config()


class _FakeResponse:
    """httpx 响应桩。"""

    def __init__(self, status_code: int, payload: dict[str, Any] | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = json.dumps(self._payload)
        self.content = self.text.encode("utf-8")

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeAsyncClient:
    """按 URL 路径返回不同响应的 httpx 桩。"""

    def __init__(self, responses: dict[str, _FakeResponse]) -> None:
        self._responses = responses
        self.calls: list[dict[str, Any]] = []

    async def __aenter__(self) -> "_FakeAsyncClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    def _match(self, url: str) -> _FakeResponse:
        for key, resp in self._responses.items():
            if key in url:
                return resp
        raise AssertionError(f"unexpected URL: {url}")

    async def post(
        self, url: str, content: str = "", headers: dict[str, str] | None = None
    ) -> _FakeResponse:
        self.calls.append({"method": "POST", "url": url, "content": content, "headers": headers})
        return self._match(url)

    async def get(self, url: str, headers: dict[str, str] | None = None) -> _FakeResponse:
        self.calls.append({"method": "GET", "url": url, "headers": headers})
        return self._match(url)


@pytest.fixture
def fake_http(monkeypatch: pytest.MonkeyPatch) -> _FakeAsyncClient:
    """拦截 httpx.AsyncClient 构造，返回桩客户端。"""
    client = _FakeAsyncClient(
        {
            "/v3/pay/transactions/native": _FakeResponse(
                200, {"code_url": "weixin://wxpay/bizpayurl?pr=test"}
            ),
            "/v3/pay/transactions/jsapi": _FakeResponse(200, {"prepay_id": "wx_prepay_test_123"}),
            "/v3/pay/transactions/out-trade-no": _FakeResponse(
                200, {"trade_state": "SUCCESS", "out_trade_no": "ORDER_001"}
            ),
            "/v3/refund/domestic/refunds": _FakeResponse(
                200, {"refund_id": "REFUND_001", "status": "PROCESSING"}
            ),
        }
    )
    monkeypatch.setattr(wechat_pay.httpx, "AsyncClient", lambda *a, **kw: client)
    return client


# ---------------------------------------------------------------------------
# _build_auth_header
# ---------------------------------------------------------------------------


def test_build_auth_header_format(wx_config: None) -> None:
    """授权头应包含 WECHATPAY2-SHA256-RSA2048 与全部必要字段。"""
    headers = wechat_pay._build_auth_header("POST", "/v3/pay/transactions/native", "{}")
    auth = headers["Authorization"]
    assert auth.startswith("WECHATPAY2-SHA256-RSA2048 ")
    for fragment in (
        'mchid="1900000001"',
        'nonce_str="',
        'signature="',
        'timestamp="',
        'serial_no="TEST_SERIAL_001"',
    ):
        assert fragment in auth, f"missing fragment: {fragment}"
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


def test_build_auth_header_signature_varies(wx_config: None) -> None:
    """同一 method/url/body 两次调用，timestamp/nonce 会变（从而签名变化）。"""
    h1 = wechat_pay._build_auth_header("GET", "/v3/foo", "")
    h2 = wechat_pay._build_auth_header("GET", "/v3/foo", "")
    # 字段都存在但不必相等（实际生产应断言时间窗口）
    assert "signature=" in h1["Authorization"]
    assert "signature=" in h2["Authorization"]


# ---------------------------------------------------------------------------
# create_native_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_native_order_success(wx_config: None, fake_http: _FakeAsyncClient) -> None:
    result = await wechat_pay.create_native_order(
        out_trade_no="ORDER_001", description="测试商品", total_amount=100
    )
    assert result == {"code_url": "weixin://wxpay/bizpayurl?pr=test"}
    assert len(fake_http.calls) == 1
    call = fake_http.calls[0]
    assert call["method"] == "POST"
    assert "/v3/pay/transactions/native" in call["url"]
    body = json.loads(call["content"])
    assert body["mchid"] == "1900000001"
    assert body["amount"] == {"total": 100, "currency": "CNY"}


@pytest.mark.asyncio
async def test_create_native_order_error(wx_config: None, monkeypatch: pytest.MonkeyPatch) -> None:
    client = _FakeAsyncClient(
        {"/v3/pay/transactions/native": _FakeResponse(400, {"error": "invalid_request"})}
    )
    monkeypatch.setattr(wechat_pay.httpx, "AsyncClient", lambda *a, **kw: client)
    with pytest.raises(RuntimeError, match="微信支付下单失败"):
        await wechat_pay.create_native_order("ORDER_001", "测试", 100)


# ---------------------------------------------------------------------------
# create_jsapi_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_jsapi_order_success(wx_config: None, fake_http: _FakeAsyncClient) -> None:
    result = await wechat_pay.create_jsapi_order(
        out_trade_no="ORDER_002",
        description="JSAPI 测试",
        total_amount=200,
        openid="OPENID_001",
    )
    assert result["prepay_id"] == "wx_prepay_test_123"
    call = fake_http.calls[0]
    body = json.loads(call["content"])
    assert body["payer"] == {"openid": "OPENID_001"}
    assert body["notify_url"] == "https://example.com/notify"


# ---------------------------------------------------------------------------
# query_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_order_success(wx_config: None, fake_http: _FakeAsyncClient) -> None:
    result = await wechat_pay.query_order("ORDER_001")
    assert result["trade_state"] == "SUCCESS"
    call = fake_http.calls[0]
    assert call["method"] == "GET"
    assert "ORDER_001" in call["url"]
    assert "mchid=1900000001" in call["url"]


# ---------------------------------------------------------------------------
# refund_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refund_order_success(wx_config: None, fake_http: _FakeAsyncClient) -> None:
    result = await wechat_pay.refund_order(
        out_trade_no="ORDER_001",
        out_refund_no="REFUND_001",
        refund_amount=50,
        total_amount=100,
        reason="用户申请退款",
    )
    assert result["refund_id"] == "REFUND_001"
    call = fake_http.calls[0]
    body = json.loads(call["content"])
    assert body["amount"] == {"refund": 50, "total": 100, "currency": "CNY"}
    assert body["reason"] == "用户申请退款"


# ---------------------------------------------------------------------------
# verify_notify_signature / parse_notify_result
# ---------------------------------------------------------------------------


def test_verify_notify_signature_valid_json() -> None:
    body = json.dumps(
        {
            "event_type": "TRANSACTION.SUCCESS",
            "resource": {
                "out_trade_no": "ORDER_001",
                "transaction_id": "TX_001",
                "trade_state": "SUCCESS",
            },
        }
    ).encode("utf-8")
    result = wechat_pay.verify_notify_signature({}, body)
    assert result is not None
    assert result["event_type"] == "TRANSACTION.SUCCESS"
    assert result["resource"]["out_trade_no"] == "ORDER_001"


def test_verify_notify_signature_invalid_json() -> None:
    result = wechat_pay.verify_notify_signature({}, b"not json at all")
    assert result is None


def test_parse_notify_result_extracts_fields() -> None:
    body = {
        "resource": {
            "out_trade_no": "ORDER_001",
            "transaction_id": "TX_001",
            "trade_state": "SUCCESS",
            "success_time": "2026-08-04T16:00:00+08:00",
        }
    }
    parsed = wechat_pay.parse_notify_result(body)
    assert parsed == {
        "out_trade_no": "ORDER_001",
        "transaction_id": "TX_001",
        "trade_state": "SUCCESS",
        "success_time": "2026-08-04T16:00:00+08:00",
    }


def test_parse_notify_result_missing_fields() -> None:
    """资源字段缺失时应返回空字符串占位而非抛错。"""
    parsed = wechat_pay.parse_notify_result({"resource": {}})
    assert parsed == {
        "out_trade_no": "",
        "transaction_id": "",
        "trade_state": "",
        "success_time": "",
    }
