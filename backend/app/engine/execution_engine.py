# -*- coding: utf-8 -*-
"""
执行引擎核心 / Execution engine core
@Function: 调度驱动和关键字，管理执行生命周期 / Dispatch drivers and keywords, manage execution lifecycle
"""

import asyncio
import time
from typing import Dict, Any, Optional
from app.driver.web_driver import WebDriver
from plugins.keywords.web_keywords import execute_keyword, KEYWORD_MAP
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("engine")


class ExecutionEngine:
    """执行引擎类 / Execution engine class"""

    def __init__(
        self,
        platform: str = "web",
        browser_type: str = "chromium",
        headless: bool = False,
        timeout: int = 30000,
    ):
        """@Function: 初始化执行引擎 / Initialize execution engine

        Args:
            platform: 平台类型 web/android/ios
            browser_type: 浏览器类型 chromium/firefox/webkit
            headless: 是否无头模式
            timeout: 默认超时（毫秒）
        """
        self._platform = platform
        self._browser_type = browser_type
        self._headless = headless
        self._timeout = timeout
        self._driver: Optional[WebDriver] = None

    async def start(self) -> None:
        """@Function: 启动执行引擎（初始化驱动）/ Start engine (initialize driver)"""
        if self._platform == "web":
            self._driver = WebDriver(
                browser_type=self._browser_type,
                headless=self._headless,
                timeout=self._timeout,
            )
            await self._driver.launch()
            logger.info("执行引擎已启动 / Execution engine started")
        else:
            raise NotImplementedError(f"暂不支持平台: {self._platform}")

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 执行单个步骤 / Execute a single step

        Args:
            step: 步骤信息，包含 keyword、params 等

        Returns:
            执行结果 {"status": "passed"|"failed", "message": str, "duration": float, ...}
        """
        if not self._driver:
            return {
                "status": "failed",
                "message": "执行引擎未启动",
                "duration": 0,
            }

        keyword = step.get("keyword", "")
        params = step.get("params", {})
        step_timeout = step.get("timeout", 30) * 1000  # 秒转毫秒

        start_time = time.time()

        try:
            result = await execute_keyword(self._driver, keyword, params, timeout=step_timeout)
            duration = round(time.time() - start_time, 2)

            if result["success"]:
                return {
                    "status": "passed",
                    "message": result.get("message", "执行成功"),
                    "duration": duration,
                    "data": result.get("data"),
                }
            else:
                return {
                    "status": "failed",
                    "message": result.get("message", "执行失败"),
                    "duration": duration,
                }
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            logger.error(f"步骤执行异常 / Step execution error: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "duration": duration,
            }

    async def stop(self) -> None:
        """@Function: 停止执行引擎（关闭驱动）/ Stop engine (close driver)"""
        if self._driver:
            await self._driver.close()
            self._driver = None
        logger.info("执行引擎已停止 / Execution engine stopped")

    @property
    def driver(self) -> Optional[WebDriver]:
        """获取当前驱动 / Get current driver"""
        return self._driver

    @property
    def is_alive(self) -> bool:
        """引擎是否存活 / Whether engine is alive"""
        return self._driver is not None and self._driver.is_alive
