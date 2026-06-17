# -*- coding: utf-8 -*-
"""
加密解密工具 / Encryption and decryption utility
@Function: 提供 AES 加密解密能力，用于敏感数据存储 / Provide AES encryption/decryption for sensitive data storage
"""

import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("crypto")


def _get_or_create_key() -> bytes:
    """@Function: 获取或创建加密密钥 / Get or create encryption key

    Returns:
        Fernet 加密密钥 / Fernet encryption key
    """
    key_file = Path(settings.DATA_DIR) / ".secret_key"

    if settings.ENCRYPTION_KEY:
        # 使用配置的密钥 / Use configured key
        key = settings.ENCRYPTION_KEY.encode()
    elif key_file.exists():
        # 从文件读取密钥 / Read key from file
        key = key_file.read_text().strip().encode()
    else:
        # 生成新密钥 / Generate new key
        key = Fernet.generate_key()
        key_file.write_text(key.decode())
        logger.info("已生成新的加密密钥 / New encryption key generated")

    # 确保密钥是正确的 Fernet 格式 / Ensure key is valid Fernet format
    if len(key) < 32:
        # 如果密钥太短，使用 SHA256 哈希 / If key too short, use SHA256 hash
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())

    return key


# 全局 Fernet 实例 / Global Fernet instance
_fernet = None


def get_fernet() -> Fernet:
    """@Function: 获取 Fernet 加密实例 / Get Fernet encryption instance

    Returns:
        Fernet 实例 / Fernet instance
    """
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_or_create_key())
    return _fernet


def encrypt(plain_text: str) -> str:
    """@Function: 加密文本 / Encrypt text

    Args:
        plain_text: 明文文本 / Plain text

    Returns:
        加密后的 Base64 编码字符串 / Encrypted Base64 encoded string
    """
    if not plain_text:
        return ""
    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(plain_text.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"加密失败 / Encryption failed: {e}")
        return plain_text


def decrypt(encrypted_text: str) -> str:
    """@Function: 解密文本 / Decrypt text

    Args:
        encrypted_text: 加密的 Base64 编码字符串 / Encrypted Base64 encoded string

    Returns:
        解密后的明文文本 / Decrypted plain text
    """
    if not encrypted_text:
        return ""
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(encrypted_text.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"解密失败 / Decryption failed: {e}")
        return encrypted_text


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """@Function: 脱敏处理，只显示部分字符 / Mask sensitive data, show only partial characters

    Args:
        value: 原始值 / Original value
        visible_chars: 可见字符数 / Number of visible characters

    Returns:
        脱敏后的字符串 / Masked string
    """
    if not value or len(value) <= visible_chars:
        return "******"
    return value[:visible_chars] + "******"
