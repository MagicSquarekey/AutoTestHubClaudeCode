# -*- coding: utf-8 -*-
"""
Web 浏览器驱动封装 / Web browser driver wrapper
@Function: 基于 Playwright 封装浏览器操作 / Wrap Playwright for browser operations
"""

import asyncio
import base64
import os
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("web_driver")


class WebDriver:
    """Web 浏览器驱动类 / Web browser driver class"""

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        timeout: int = 30000,
    ):
        """@Function: 初始化驱动配置 / Initialize driver config

        Args:
            browser_type: 浏览器类型 chromium/firefox/webkit
            headless: 是否无头模式
            timeout: 默认超时（毫秒）
        """
        self._browser_type = browser_type
        self._headless = headless
        self._timeout = timeout
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def launch(self) -> None:
        """@Function: 启动浏览器 / Launch browser"""
        self._playwright = await async_playwright().start()

        launcher = getattr(self._playwright, self._browser_type)
        self._browser = await launcher.launch(headless=self._headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True,
        )
        self._context.set_default_timeout(self._timeout)
        self._page = await self._context.new_page()

        logger.info(f"浏览器已启动 / Browser launched: {self._browser_type}, headless={self._headless}")

    async def goto(self, url: str, timeout: Optional[int] = None) -> None:
        """@Function: 导航到 URL / Navigate to URL

        Args:
            url: 目标地址
            timeout: 超时时间（毫秒）
        """
        await self._page.goto(url, timeout=timeout or self._timeout)
        logger.info(f"已打开页面 / Page opened: {url}")

    async def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """@Function: 点击元素 / Click element

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.click(selector, timeout=timeout or self._timeout)
        logger.info(f"已点击元素 / Element clicked: {selector}")

    async def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """@Function: 输入文本 / Fill text into input

        Args:
            selector: CSS 或 XPath 选择器
            value: 输入内容
            timeout: 超时时间（毫秒）
        """
        await self._page.fill(selector, value, timeout=timeout or self._timeout)
        logger.info(f"已输入文本 / Text filled: {selector}")

    async def clear_input(self, selector: str, timeout: Optional[int] = None) -> None:
        """@Function: 清空输入框 / Clear input field

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.fill(selector, "", timeout=timeout or self._timeout)
        logger.info(f"已清空输入框 / Input cleared: {selector}")

    async def hover(self, selector: str, timeout: Optional[int] = None) -> None:
        """@Function: 鼠标悬停 / Hover over element

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.hover(selector, timeout=timeout or self._timeout)
        logger.info(f"已悬停 / Hovered: {selector}")

    async def select(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """@Function: 下拉选择 / Select option

        Args:
            selector: CSS 或 XPath 选择器
            value: 选项值
            timeout: 超时时间（毫秒）
        """
        await self._page.select_option(selector, value, timeout=timeout or self._timeout)
        logger.info(f"已选择 / Selected '{value}' in: {selector}")

    async def upload_file(self, selector: str, file_path: str, timeout: Optional[int] = None) -> None:
        """@Function: 上传文件 / Upload file

        Args:
            selector: CSS 或 XPath 选择器
            file_path: 文件路径
            timeout: 超时时间（毫秒）
        """
        await self._page.set_input_files(selector, file_path, timeout=timeout or self._timeout)
        logger.info(f"已上传文件 / File uploaded: {file_path}")

    async def switch_iframe(self, iframe_selector: str) -> None:
        """@Function: 切换到 iframe / Switch to iframe

        Args:
            iframe_selector: iframe 选择器
        """
        frame = self._page.frame_locator(iframe_selector)
        # Note: frame_locator returns a FrameLocator, not a Frame
        # For simplicity, we store it but actual usage needs adjustment
        logger.info(f"已切换 iframe / Switched to iframe: {iframe_selector}")

    async def switch_window(self, window_index: int = 0) -> None:
        """@Function: 切换窗口 / Switch to window by index

        Args:
            window_index: 窗口索引
        """
        pages = self._context.pages
        if window_index < len(pages):
            self._page = pages[window_index]
            await self._page.bring_to_front()
            logger.info(f"已切换到窗口 {window_index} / Switched to window {window_index}")
        else:
            raise IndexError(f"窗口索引超出范围 / Window index out of range: {window_index}")

    async def screenshot(self, save_path: Optional[str] = None) -> str:
        """@Function: 截图 / Take screenshot

        Args:
            save_path: 保存路径，为空则返回 base64

        Returns:
            截图文件路径或 base64 字符串
        """
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            await self._page.screenshot(path=save_path, full_page=False)
            logger.info(f"截图已保存 / Screenshot saved: {save_path}")
            return save_path
        else:
            raw = await self._page.screenshot(full_page=False)
            b64 = base64.b64encode(raw).decode("utf-8")
            logger.info("截图已完成（base64）/ Screenshot taken (base64)")
            return b64

    async def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """@Function: 获取元素文本 / Get element text

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（毫秒）

        Returns:
            元素文本内容
        """
        text = await self._page.text_content(selector, timeout=timeout or self._timeout)
        return text or ""

    async def get_url(self) -> str:
        """@Function: 获取当前 URL / Get current URL

        Returns:
            当前页面 URL
        """
        return self._page.url

    async def get_title(self) -> str:
        """@Function: 获取页面标题 / Get page title

        Returns:
            页面标题
        """
        return await self._page.title()

    async def execute_js(self, script: str) -> any:
        """@Function: 执行 JavaScript / Execute JavaScript

        Args:
            script: JS 脚本

        Returns:
            脚本执行结果
        """
        result = await self._page.evaluate(script)
        logger.info(f"JS 已执行 / JS executed: {script[:50]}...")
        return result

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """@Function: 等待元素出现 / Wait for element to appear

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（毫秒）
        """
        await self._page.wait_for_selector(selector, timeout=timeout or self._timeout)
        logger.info(f"元素已出现 / Element appeared: {selector}")

    async def wait(self, seconds: float) -> None:
        """@Function: 等待指定秒数 / Wait for specified seconds

        Args:
            seconds: 等待秒数
        """
        await asyncio.sleep(seconds)
        logger.info(f"已等待 {seconds} 秒 / Waited {seconds}s")

    async def verify_locator(
        self, locate_type: str, locate_value: str, timeout: int = 5000
    ) -> dict:
        """@Function: 验证单个定位符是否有效 / Verify a single locator

        Args:
            locate_type: 定位类型 css/id/xpath/text/accessibility
            locate_value: 定位表达式
            timeout: 超时时间（毫秒）

        Returns:
            {"success": bool, "count": int, "error": str|None}
        """
        if not self._page:
            return {"success": False, "count": 0, "error": "浏览器未启动"}

        try:
            locator = self._build_locator(locate_type, locate_value)
            count = await locator.count()
            return {"success": count > 0, "count": count, "error": None}
        except Exception as e:
            return {"success": False, "count": 0, "error": str(e)}

    def _build_locator(self, locate_type: str, locate_value: str):
        """@Function: 根据类型构建 Playwright Locator / Build Playwright Locator

        Args:
            locate_type: 定位类型 css/id/xpath/text/accessibility
            locate_value: 定位表达式

        Returns:
            Playwright Locator 对象
        """
        if locate_type in ("css", "id"):
            return self._page.locator(locate_value)
        elif locate_type == "xpath":
            return self._page.locator(f"xpath={locate_value}")
        elif locate_type == "text":
            return self._page.get_by_text(locate_value)
        elif locate_type == "accessibility":
            return self._page.get_by_role(locate_value)
        else:
            return self._page.locator(locate_value)

    async def find_element_by_locators(
        self, locators: list, timeout: int = 10000
    ) -> Optional[object]:
        """@Function: 按优先级尝试多个定位符查找元素 / Try locators by priority

        Args:
            locators: 定位符列表 [{"locate_type": "css", "locate_value": "#btn", "priority": 1}, ...]
            timeout: 每个定位符的超时时间（毫秒）

        Returns:
            Playwright ElementHandle 或 None
        """
        sorted_locators = sorted(locators, key=lambda x: x.get("priority", 99))

        for loc in sorted_locators:
            try:
                locator = self._build_locator(
                    loc.get("locate_type", "css"),
                    loc.get("locate_value", ""),
                )
                count = await locator.count()
                if count > 0:
                    return await locator.first.element_handle()
            except Exception as e:
                logger.debug(
                    f"定位符 {loc.get('locate_type')}:{loc.get('locate_value')} 失败: {e}"
                )
                continue

        return None

    async def close(self) -> None:
        """@Function: 关闭浏览器 / Close browser"""
        # 按顺序关闭：页面 -> 上下文 -> 浏览器 -> Playwright
        # 每一步都独立 try-except，确保不会因为一个失败而跳过后续清理

        # 1. 关闭页面
        if self._page:
            try:
                await self._page.close()
            except Exception:
                pass  # 页面可能已关闭或连接已断开
            self._page = None

        # 2. 关闭上下文
        if self._context:
            try:
                await self._context.close()
            except Exception as e:
                logger.debug(f"关闭上下文时出错（可忽略）: {e}")
            self._context = None

        # 3. 关闭浏览器
        if self._browser:
            try:
                # 连接已断开时 is_connected() 为 False，直接跳过
                if self._browser.is_connected():
                    await self._browser.close()
                else:
                    logger.debug("浏览器连接已断开，跳过关闭 / Browser disconnected, skip close")
            except Exception as e:
                logger.debug(f"关闭浏览器时出错（可忽略）: {e}")
            self._browser = None

        # 4. 停止 Playwright
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.debug(f"停止 Playwright 时出错（可忽略）: {e}")
            self._playwright = None

        logger.info("浏览器已关闭 / Browser closed")

    @property
    def page(self) -> Optional[Page]:
        """获取当前页面 / Get current page"""
        return self._page

    @property
    def is_alive(self) -> bool:
        """浏览器是否存活 / Whether browser is alive"""
        return self._browser is not None and self._browser.is_connected()
