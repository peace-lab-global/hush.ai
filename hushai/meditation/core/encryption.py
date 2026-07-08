"""敏感数据加密工具。

使用 Fernet 对称加密保护咨询记录中的敏感字段（summary、counselor_notes）。
同时提供 PII 脱敏辅助函数。
"""

from __future__ import annotations

import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """懒加载 Fernet 实例，密钥从环境变量获取。"""
    global _fernet
    if _fernet is None:
        key = os.environ.get("MEDITATION_ENCRYPTION_KEY", "")
        if not key:
            # 未配置密钥时自动生成（仅适用于开发环境，生产环境必须显式配置）
            key = Fernet.generate_key().decode()
            os.environ["MEDITATION_ENCRYPTION_KEY"] = key
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_field(plaintext: Optional[str]) -> Optional[str]:
    """加密明文，返回密文（base64 字符串）。空值原样返回。"""
    if not plaintext:
        return plaintext
    f = _get_fernet()
    return f.encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt_field(ciphertext: Optional[str]) -> Optional[str]:
    """解密密文，返回明文。空值或解密失败时原样返回。"""
    if not ciphertext:
        return ciphertext
    try:
        f = _get_fernet()
        return f.decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except InvalidToken:
        return ciphertext


def mask_phone(phone: Optional[str]) -> Optional[str]:
    """手机号脱敏：138****1234"""
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def mask_id_number(id_number: Optional[str]) -> Optional[str]:
    """身份证号脱敏：110***********1234"""
    if not id_number or len(id_number) < 8:
        return id_number
    return id_number[:3] + "*" * (len(id_number) - 7) + id_number[-4:]


def mask_name(name: Optional[str]) -> Optional[str]:
    """姓名脱敏：张*三"""
    if not name:
        return name
    if len(name) <= 1:
        return name
    if len(name) == 2:
        return name[0] + "*"
    return name[0] + "*" * (len(name) - 2) + name[-1]


def reset_encryption() -> None:
    """重置加密实例（测试用）。"""
    global _fernet
    _fernet = None
