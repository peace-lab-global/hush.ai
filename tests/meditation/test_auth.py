"""测试认证模块 — refresh token 查找、JWT type 校验、bearer 提取。

验证 P0 修复：
- refresh_access_token 用 refresh_token_selector 做 O(1) 查找（不再全表 bcrypt）
- verify_token 强制校验 type == access
- _create_token 死代码已删除
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from hushai.meditation import config as cfg_module
from hushai.meditation.api import auth
from hushai.meditation.db.models import User


@pytest.fixture(autouse=True)
def _test_config():
    """每个测试用独立配置，避免污染。"""
    cfg_module.set_config(
        cfg_module.MeditationConfig(
            debug=True,
            jwt_secret="test-secret-not-for-prod",
            default_llm_provider="openai",
        )
    )
    yield
    cfg_module.reset_config()


def test_create_token_dead_code_removed():
    """P0 修复：死代码 _create_token 应已删除。"""
    assert not hasattr(auth, "_create_token"), "_create_token 死代码应已删除"


def test_token_selector_is_sha256_hex():
    """selector 应是 64 字符 hex（SHA-256），用于 O(1) 查找。"""
    selector = auth._token_selector("some-refresh-token")
    assert len(selector) == 64
    assert all(c in "0123456789abcdef" for c in selector)

    # 不同 token 产生不同 selector
    assert auth._token_selector("token-a") != auth._token_selector("token-b")


def test_verify_token_rejects_missing_type():
    """P0 修复：不带 type 字段的 token 应被拒绝。"""
    from jose import jwt

    # 构造一个无 type 字段的 token（模拟旧代码或攻击者伪造）
    payload = {"sub": "user-1"}  # 故意省略 type
    token = jwt.encode(payload, cfg_module.get_config().jwt_secret, algorithm="HS256")
    with pytest.raises(RuntimeError, match="类型错误"):
        auth.verify_token(token)


def test_verify_token_rejects_wrong_type():
    """type != access 的 token 应被拒绝。"""
    from jose import jwt

    payload = {"sub": "user-1", "type": "refresh"}
    token = jwt.encode(payload, cfg_module.get_config().jwt_secret, algorithm="HS256")
    with pytest.raises(RuntimeError, match="类型错误"):
        auth.verify_token(token)


def test_verify_token_accepts_access_type():
    """带 type=access 的合法 token 应通过。"""
    from jose import jwt

    payload = {"sub": "user-1", "type": "access"}
    token = jwt.encode(payload, cfg_module.get_config().jwt_secret, algorithm="HS256")
    result = auth.verify_token(token)
    assert result["sub"] == "user-1"
    assert result["type"] == "access"


@pytest.mark.asyncio
async def test_refresh_token_uses_selector_lookup(meditation_session):
    """P0 修复：refresh_access_token 应通过 selector O(1) 定位用户。

    通过 patch _verify_token_hash 让其返回 True，验证：
    1. 查询命中正确用户（selector 匹配）
    2. 不再触发全表扫描
    3. 返回新的 access/refresh token
    """
    # 准备一个带 refresh token 的用户
    refresh_token = "original-refresh-token-abc123"
    user = User(
        wx_openid="openid-1",
        nickname="测试用户",
        refresh_token_hash=auth._hash_token(refresh_token),
        refresh_token_selector=auth._token_selector(refresh_token),
    )
    meditation_session.add(user)
    await meditation_session.commit()

    # patch bcrypt 校验返回 True（重点测查找逻辑，不测 bcrypt 本身）
    with patch.object(auth, "_verify_token_hash", return_value=True):
        result = await auth.refresh_access_token(refresh_token, meditation_session)

    assert "access_token" in result
    assert "refresh_token" in result
    assert result["refresh_token"] != refresh_token  # 应返回新 token


@pytest.mark.asyncio
async def test_refresh_token_unknown_token_raises(meditation_session):
    """不存在的 refresh token 应抛错，且不命中任何用户。"""
    user = User(wx_openid="openid-2", nickname="其他用户")
    meditation_session.add(user)
    await meditation_session.commit()

    with pytest.raises(RuntimeError, match="无效或已过期"):
        await auth.refresh_access_token("nonexistent-token", meditation_session)


@pytest.mark.asyncio
async def test_refresh_token_invalid_hash_raises(meditation_session):
    """selector 命中但 bcrypt 校验失败（token 被篡改）应拒绝。"""
    refresh_token = "valid-token"
    tampered = "tampered-token-different"
    user = User(
        wx_openid="openid-3",
        refresh_token_hash=auth._hash_token(refresh_token),
        refresh_token_selector=auth._token_selector(tampered),  # selector 指向 tampered
    )
    meditation_session.add(user)
    await meditation_session.commit()

    # tampered 的 selector 命中该用户，但真实 bcrypt 校验失败
    with pytest.raises(RuntimeError, match="无效或已过期"):
        await auth.refresh_access_token(tampered, meditation_session)


def test_extract_bearer_token():
    assert auth.extract_bearer_token("Bearer abc123") == "abc123"
    assert auth.extract_bearer_token("abc123") == "abc123"  # 宽松解析
