# -*- coding: utf-8 -*-
"""
加密解密工具
@Function: 提供AES加密解密能力，用于敏感数据存储
"""

import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("crypto")


def _get_or_create_key() -> bytes:
    """@Function: 获取或创建加密密钥

    Returns:
        Fernet加密密钥
    """
    key_file = Path(settings.DATA_DIR) / ".secret_key"

    if settings.ENCRYPTION_KEY:
        # 使用配置的密钥
        key = settings.ENCRYPTION_KEY.encode()
    elif key_file.exists():
        # 从文件读取密钥
        key = key_file.read_text().strip().encode()
    else:
        # 生成新密钥
        key = Fernet.generate_key()
        key_file.write_text(key.decode())
        logger.info("已生成新的加密密钥")

    # 确保密钥是正确的Fernet格式
    if len(key) < 32:
        # 如果密钥太短，使用SHA256哈希
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())

    return key


# 全局Fernet实例
_fernet = None


def get_fernet() -> Fernet:
    """@Function: 获取Fernet加密实例

    Returns:
        Fernet实例
    """
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_or_create_key())
    return _fernet


def encrypt(plain_text: str) -> str:
    """@Function: 加密文本

    Args:
        plain_text: 明文文本

    Returns:
        加密后的Base64编码字符串
    """
    if not plain_text:
        return ""
    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(plain_text.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"加密失败: {e}")
        return plain_text


def decrypt(encrypted_text: str) -> str:
    """@Function: 解密文本

    Args:
        encrypted_text: 加密的Base64编码字符串

    Returns:
        解密后的明文文本
    """
    if not encrypted_text:
        return ""
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(encrypted_text.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"解密失败: {e}")
        return encrypted_text


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """@Function: 脱敏处理，只显示部分字符

    Args:
        value: 原始值
        visible_chars: 可见字符数

    Returns:
        脱敏后的字符串
    """
    if not value or len(value) <= visible_chars:
        return "******"
    return value[:visible_chars] + "******"
