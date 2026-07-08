"""微信支付 v3 API 集成。

封装 Native / JSAPI 支付的统一下单、查询、退款及回调验签。
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time as _time
from typing import Any, Optional

import httpx

from hushai.meditation.config import get_config

logger = logging.getLogger("hushai.meditation.wechat_pay")

WX_PAY_BASE_URL = "https://api.mch.weixin.qq.com"
WX_PAY_NATIVE_URL = f"{WX_PAY_BASE_URL}/v3/pay/transactions/native"
WX_PAY_JSAPI_URL = f"{WX_PAY_BASE_URL}/v3/pay/transactions/jsapi"
WX_PAY_QUERY_URL = f"{WX_PAY_BASE_URL}/v3/pay/transactions/out-trade-no"
WX_PAY_REFUND_URL = f"{WX_PAY_BASE_URL}/v3/refund/domestic/refunds"


def _build_auth_header(method: str, url_path: str, body: str) -> dict[str, str]:
    """构建微信支付 v3 请求头（WECHATPAY2-SHA256-RSA2048 签名）。

    注意：完整 RSA 签名需要商户私钥，此处预留签名占位。
    生产环境应使用 cryptography 库加载私钥完成签名。
    """
    cfg = get_config()
    timestamp = str(int(_time.time()))
    nonce_str = f"hushai_{int(_time.time() * 1000)}"

    message = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n{body}\n"
    # 生产环境：使用商户私钥 RSA-SHA256 签名
    # 此处使用 HMAC-SHA256 作为开发阶段占位
    sign_key = cfg.wx_pay_api_key.encode("utf-8") if cfg.wx_pay_api_key else b"dev_key"
    signature = hmac.new(sign_key, message.encode("utf-8"), hashlib.sha256).hexdigest()

    auth = (
        f'WECHATPAY2-SHA256-RSA2048 mchid="{cfg.wx_mch_id}",'
        f'nonce_str="{nonce_str}",'
        f'signature="{signature}",'
        f'timestamp="{timestamp}",'
        f'serial_no="{cfg.wx_pay_serial_no}"'
    )
    return {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


async def create_native_order(
    out_trade_no: str,
    description: str,
    total_amount: int,
) -> dict[str, Any]:
    """Native 支付下单（扫码支付），返回 code_url。"""
    cfg = get_config()
    body = {
        "appid": cfg.wx_appid,
        "mchid": cfg.wx_mch_id,
        "description": description,
        "out_trade_no": out_trade_no,
        "amount": {"total": total_amount, "currency": "CNY"},
    }
    body_str = json.dumps(body, ensure_ascii=False)
    headers = _build_auth_header("POST", "/v3/pay/transactions/native", body_str)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(WX_PAY_NATIVE_URL, content=body_str, headers=headers)
        if resp.status_code >= 400:
            logger.error("Native 下单失败: %s %s", resp.status_code, resp.text)
            raise RuntimeError(f"微信支付下单失败: {resp.text}")
        return resp.json()  # type: ignore[no-any-return]


async def create_jsapi_order(
    out_trade_no: str,
    description: str,
    total_amount: int,
    openid: str,
) -> dict[str, Any]:
    """JSAPI 支付下单（小程序/公众号），返回 prepay_id。"""
    cfg = get_config()
    body = {
        "appid": cfg.wx_appid,
        "mchid": cfg.wx_mch_id,
        "description": description,
        "out_trade_no": out_trade_no,
        "notify_url": cfg.wx_pay_notify_url,
        "amount": {"total": total_amount, "currency": "CNY"},
        "payer": {"openid": openid},
    }
    body_str = json.dumps(body, ensure_ascii=False)
    headers = _build_auth_header("POST", "/v3/pay/transactions/jsapi", body_str)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(WX_PAY_JSAPI_URL, content=body_str, headers=headers)
        if resp.status_code >= 400:
            logger.error("JSAPI 下单失败: %s %s", resp.status_code, resp.text)
            raise RuntimeError(f"微信支付下单失败: {resp.text}")
        return resp.json()  # type: ignore[no-any-return]


async def query_order(out_trade_no: str) -> dict[str, Any]:
    """查询订单状态。"""
    cfg = get_config()
    url = f"{WX_PAY_QUERY_URL}/{out_trade_no}?mchid={cfg.wx_mch_id}"
    headers = _build_auth_header(
        "GET", f"/v3/pay/transactions/out-trade-no/{out_trade_no}?mchid={cfg.wx_mch_id}", ""
    )

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code >= 400:
            logger.error("查询订单失败: %s %s", resp.status_code, resp.text)
            raise RuntimeError(f"微信支付查询失败: {resp.text}")
        return resp.json()  # type: ignore[no-any-return]


async def refund_order(
    out_trade_no: str,
    out_refund_no: str,
    refund_amount: int,
    total_amount: int,
    reason: str = "用户申请退款",
) -> dict[str, Any]:
    """申请退款。"""
    cfg = get_config()
    body = {
        "out_trade_no": out_trade_no,
        "out_refund_no": out_refund_no,
        "reason": reason,
        "notify_url": cfg.wx_pay_notify_url,
        "amount": {
            "refund": refund_amount,
            "total": total_amount,
            "currency": "CNY",
        },
    }
    body_str = json.dumps(body, ensure_ascii=False)
    headers = _build_auth_header("POST", "/v3/refund/domestic/refunds", body_str)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(WX_PAY_REFUND_URL, content=body_str, headers=headers)
        if resp.status_code >= 400:
            logger.error("退款失败: %s %s", resp.status_code, resp.text)
            raise RuntimeError(f"微信退款失败: {resp.text}")
        return resp.json()  # type: ignore[no-any-return]


def verify_notify_signature(
    headers: dict[str, str],
    body: bytes,
) -> Optional[dict[str, Any]]:
    """验证支付回调签名并解密通知内容。

    生产环境需要使用微信支付平台证书进行 RSA 验签。
    此处提供基础结构，返回解密后的 JSON。
    """
    # TODO: 生产环境完整验签逻辑
    # 1. 从 headers 提取 timestamp, nonce, serial, signature
    # 2. 使用微信平台公钥验证签名
    # 3. 使用 APIv3 密钥解密 resource 字段
    try:
        payload = json.loads(body)
        resource = payload.get("resource", {})
        # 开发阶段：直接返回（生产环境需解密 resource）
        return {
            "event_type": payload.get("event_type"),
            "resource": resource,
        }
    except (json.JSONDecodeError, KeyError):
        logger.exception("解析支付回调失败")
        return None


def parse_notify_result(body: dict[str, Any]) -> dict[str, Any]:
    """从回调通知中提取交易结果。"""
    resource = body.get("resource", {})
    # 生产环境解密后的 JSON 结构
    return {
        "out_trade_no": resource.get("out_trade_no", ""),
        "transaction_id": resource.get("transaction_id", ""),
        "trade_state": resource.get("trade_state", ""),
        "success_time": resource.get("success_time", ""),
    }
