# -*- coding: utf-8 -*-
"""
日志管理工具
@Function: 统一日志配置，支持文件和控制台输出
"""

import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


# 移除默认处理器
logger.remove()

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)

# 文件输出 - 一般日志
logger.add(
    Path(settings.LOG_DIR) / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)

# 文件输出 - 错误日志
logger.add(
    Path(settings.LOG_DIR) / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="00:00",
    retention="60 days",
    compression="zip",
    encoding="utf-8",
)

# 文件输出 - 执行日志
logger.add(
    Path(settings.LOG_DIR) / "exec_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",
    retention="7 days",
    compression="zip",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("module") == "exec",
)


def get_logger(module: str = "app"):
    """@Function: 获取指定模块的日志记录器

    Args:
        module: 模块名称

    Returns:
        绑定模块名称的日志记录器
    """
    return logger.bind(module=module)
