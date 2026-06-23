# -*- coding: utf-8 -*-
"""
执行引擎核心 / Execution engine core
@Function: 调度驱动和关键字，管理执行生命周期 / Dispatch drivers and keywords, manage execution lifecycle
"""

import asyncio
import base64
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from app.driver.web_driver import WebDriver
from plugins.keywords.web_keywords import execute_keyword, KEYWORD_MAP
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("engine")


class ExecutionEngine:
    """执行引擎类 / Execution engine class

    支持暂停/恢复能力，用于人工介入场景（如验证码识别失败时等待用户手动输入）
    """

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

        # 暂停/恢复支持 / Pause/resume support
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # 初始状态：未暂停
        self._manual_input_callback: Optional[Callable[..., Awaitable[str]]] = None
        self._pending_manual_input: Optional[Dict[str, Any]] = None

    def set_manual_input_callback(self, callback: Callable[..., Awaitable[str]]) -> None:
        """@Function: 设置人工介入回调 / Set manual input callback

        Args:
            callback: 异步回调函数，接收参数 (screenshot_base64, captcha_selector, input_selector)
                      返回用户输入的验证码文本
        """
        self._manual_input_callback = callback

    async def pause_for_manual_input(
        self,
        screenshot_path: str,
        captcha_selector: str,
        input_selector: str,
        task_id: Optional[int] = None,
    ) -> str:
        """@Function: 暂停执行等待人工输入 / Pause execution for manual input

        Args:
            screenshot_path: 验证码截图路径
            captcha_selector: 验证码图片选择器
            input_selector: 验证码输入框选择器
            task_id: 调试任务ID（用于前端推送）

        Returns:
            用户手动输入的验证码文本
        """
        logger.info("[ExecutionEngine] 暂停执行，等待人工输入验证码...")

        # 读取截图并转为 base64
        with open(screenshot_path, "rb") as f:
            screenshot_base64 = base64.b64encode(f.read()).decode("utf-8")

        # 存储待处理的人工输入请求
        # 注意：记录当前事件循环，以便 submit_manual_input 跨线程安全唤醒
        self._pending_manual_input = {
            "screenshot_base64": screenshot_base64,
            "captcha_selector": captcha_selector,
            "input_selector": input_selector,
            "task_id": task_id,
            "event": asyncio.Event(),
            "loop": asyncio.get_running_loop(),
            "result": None,
        }

        # 暂停执行
        self._pause_event.clear()

        # 通知前端（如果有回调）
        # 注意：task_id 不传给回调，因为回调闭包已捕获 task_id
        if self._manual_input_callback:
            try:
                await self._manual_input_callback(
                    screenshot_base64=screenshot_base64,
                    captcha_selector=captcha_selector,
                    input_selector=input_selector,
                )
            except Exception as e:
                logger.warning(f"[ExecutionEngine] 通知前端失败: {e}")

        # 等待用户输入
        logger.info("[ExecutionEngine] 等待用户输入验证码...")
        await self._pending_manual_input["event"].wait()

        # 获取用户输入
        user_input = self._pending_manual_input.get("result", "")
        self._pending_manual_input = None

        # 恢复执行
        self._pause_event.set()
        logger.info(f"[ExecutionEngine] 收到用户输入: {user_input}，继续执行")

        return user_input

    def submit_manual_input(self, captcha_text: str) -> bool:
        """@Function: 提交人工输入的验证码 / Submit manually entered captcha

        注意：此方法可能从不同的线程/事件循环调用（如 FastAPI 主线程），
        需要使用 call_soon_threadsafe 安全唤醒等待中的协程。

        Args:
            captcha_text: 用户输入的验证码文本

        Returns:
            是否提交成功
        """
        if self._pending_manual_input:
            self._pending_manual_input["result"] = captcha_text
            event = self._pending_manual_input["event"]
            loop = self._pending_manual_input.get("loop")

            if not event.is_set():
                # 跨线程安全唤醒：在正确的事件循环中设置 event
                if loop and loop.is_running():
                    loop.call_soon_threadsafe(event.set)
                else:
                    event.set()
                logger.info(f"[ExecutionEngine] 验证码已提交: {captcha_text}")
                return True
            else:
                logger.info(f"[ExecutionEngine] 验证码已更新: {captcha_text}")
                return True
        return False

    @property
    def is_paused(self) -> bool:
        """是否处于暂停状态 / Whether engine is paused"""
        return not self._pause_event.is_set()

    @property
    def pending_manual_input(self) -> Optional[Dict[str, Any]]:
        """获取待处理的人工输入请求 / Get pending manual input request"""
        return self._pending_manual_input

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

        # 等待暂停恢复（如果处于暂停状态）
        await self._pause_event.wait()

        keyword = step.get("keyword", "")
        params = dict(step.get("params", {}))  # 复制 params 避免污染原始数据
        step_timeout = step.get("timeout", 30) * 1000  # 秒转毫秒

        # 为 solve_captcha 关键字自动注入 engine 和 task_id（人工介入时需要）
        if keyword == "solve_captcha":
            params["engine"] = self
            params["task_id"] = step.get("_task_id")

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
        # 如果正在暂停等待人工输入，先恢复
        if self._pending_manual_input and not self._pending_manual_input["event"].is_set():
            self._pending_manual_input["result"] = ""
            self._pending_manual_input["event"].set()
        self._pause_event.set()

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
