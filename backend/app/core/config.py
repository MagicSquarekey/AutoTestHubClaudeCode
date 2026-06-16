# -*- coding: utf-8 -*-
"""
应用配置管理
@Function: 读取环境变量和配置文件，提供全局配置访问
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "AutoTest Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8686

    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'autotest.db'}"

    # 安全配置
    SECRET_KEY: str = "autotest-hub-secret-key-change-in-production"
    ENCRYPTION_KEY: str = ""  # AES加密密钥，首次运行自动生成

    # 文件存储配置
    DATA_DIR: str = str(Path(__file__).parent.parent.parent / "data")
    LOG_DIR: str = str(Path(__file__).parent.parent.parent / "logs")
    REPORT_DIR: str = str(Path(__file__).parent.parent.parent / "data" / "reports")
    SCREENSHOT_DIR: str = str(Path(__file__).parent.parent.parent / "data" / "screenshots")

    # 执行引擎配置
    DEFAULT_TIMEOUT: int = 30  # 默认超时时间（秒）
    DEFAULT_RETRY_COUNT: int = 3  # 默认重试次数
    MAX_PARALLEL_TASKS: int = 5  # 最大并行任务数
    ENABLE_SCREENSHOT: bool = True  # 是否启用截图
    ENABLE_VIDEO: bool = False  # 是否启用录屏

    # Web驱动配置
    BROWSER_TYPE: str = "chromium"  # chromium/firefox/webkit
    HEADLESS: bool = False  # 是否无头模式
    BROWSER_TIMEOUT: int = 30000  # 浏览器超时（毫秒）

    # Android驱动配置
    APPIUM_SERVER: str = "http://127.0.0.1:4723"
    ADB_PATH: str = ""  # ADB路径，留空自动检测

    # iOS驱动配置
    WDA_BUNDLE_ID: str = ""
    TIDEVICE_PATH: str = ""

    # AI配置
    AI_API_KEY: str = ""
    AI_API_URL: str = ""
    AI_MODEL: str = "gpt-3.5-turbo"

    # 通知配置
    FEISHU_WEBHOOK: str = ""
    WECOM_WEBHOOK: str = ""
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 465
    EMAIL_SENDER: str = ""
    EMAIL_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()

# 确保目录存在
for dir_path in [settings.DATA_DIR, settings.LOG_DIR, settings.REPORT_DIR, settings.SCREENSHOT_DIR]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
