# -*- coding: utf-8 -*-
"""
录制引擎 / Recording engine
@Function: 基于 Playwright 实现浏览器操作录制 / Implement browser action recording using Playwright
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("recording_engine")

# 事件监听脚本 / Event listener script
EVENT_LISTENER_SCRIPT = """
(() => {
    // 防止重复注入 / Prevent duplicate injection
    if (window.__recording_engine_initialized) return;
    window.__recording_engine_initialized = true;

    // 存储录制的操作 / Store recorded actions
    window.__recorded_actions = [];

    // 生成元素的多种定位符 / Generate multiple locators for element
    function generateLocators(element) {
        const locators = {};

        // 1. 尝试获取 data-testid / Try data-testid
        const testId = element.getAttribute('data-testid');
        if (testId) {
            locators['data-testid'] = testId;
        }

        // 2. 尝试获取 id / Try id
        if (element.id) {
            locators['id'] = element.id;
        }

        // 3. 尝试获取 name / Try name
        const name = element.getAttribute('name');
        if (name) {
            locators['name'] = name;
        }

        // 4. 尝试获取 placeholder / Try placeholder
        const placeholder = element.getAttribute('placeholder');
        if (placeholder) {
            locators['placeholder'] = placeholder;
        }

        // 5. 生成 CSS Selector / Generate CSS Selector
        try {
            const cssSelector = generateCssSelector(element);
            if (cssSelector) {
                locators['css'] = cssSelector;
            }
        } catch (e) {}

        // 6. 生成 XPath / Generate XPath
        try {
            const xpath = generateXPath(element);
            if (xpath) {
                locators['xpath'] = xpath;
            }
        } catch (e) {}

        // 7. 获取文本内容 / Get text content
        const text = element.textContent?.trim();
        if (text && text.length < 50) {
            locators['text'] = text;
        }

        // 8. 获取标签和类型 / Get tag and type
        locators['tag'] = element.tagName.toLowerCase();
        const type = element.getAttribute('type');
        if (type) {
            locators['type'] = type;
        }

        return locators;
    }

    // 生成 CSS Selector / Generate CSS Selector
    function generateCssSelector(element) {
        if (element.id) {
            return '#' + CSS.escape(element.id);
        }

        const parts = [];
        let current = element;
        let depth = 0;

        while (current && current !== document.body && depth < 5) {
            let selector = current.tagName.toLowerCase();

            if (current.id) {
                selector = '#' + CSS.escape(current.id);
                parts.unshift(selector);
                break;
            }

            if (current.className && typeof current.className === 'string') {
                const classes = current.className.trim().split(/\\s+/)
                    .filter(c => c && !c.includes('--'))
                    .slice(0, 2)
                    .map(c => '.' + CSS.escape(c));
                if (classes.length) {
                    selector += classes.join('');
                }
            }

            // 添加 nth-child 如果有多个同级元素 / Add nth-child if multiple siblings
            const parent = current.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children).filter(
                    s => s.tagName === current.tagName
                );
                if (siblings.length > 1) {
                    const index = siblings.indexOf(current) + 1;
                    selector += `:nth-child(${index})`;
                }
            }

            parts.unshift(selector);
            current = current.parentElement;
            depth++;
        }

        return parts.join(' > ');
    }

    // 生成 XPath / Generate XPath
    function generateXPath(element) {
        const parts = [];
        let current = element;

        while (current && current !== document.body) {
            let selector = current.tagName.toLowerCase();

            if (current.id) {
                selector = `[@id="${current.id}"]`;
                parts.unshift(selector);
                break;
            }

            const parent = current.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children).filter(
                    s => s.tagName === current.tagName
                );
                if (siblings.length > 1) {
                    const index = siblings.indexOf(current) + 1;
                    selector += `[${index}]`;
                }
            }

            parts.unshift(selector);
            current = current.parentElement;
        }

        return '//' + parts.join('/');
    }

    // 获取元素描述名称 / Get element description name
    function getElementName(element) {
        // 优先使用文本内容 / Prefer text content
        const text = element.textContent?.trim();
        if (text && text.length < 30) {
            return text;
        }

        // 尝试使用 aria-label / Try aria-label
        const ariaLabel = element.getAttribute('aria-label');
        if (ariaLabel) {
            return ariaLabel;
        }

        // 尝试使用 placeholder / Try placeholder
        const placeholder = element.getAttribute('placeholder');
        if (placeholder) {
            return placeholder;
        }

        // 尝试使用 title / Try title
        const title = element.getAttribute('title');
        if (title) {
            return title;
        }

        // 使用标签名和类名 / Use tag and class
        let name = element.tagName.toLowerCase();
        if (element.className && typeof element.className === 'string') {
            const mainClass = element.className.trim().split(/\\s+/)[0];
            if (mainClass) {
                name += '.' + mainClass;
            }
        }

        return name;
    }

    // 记录操作 / Record action
    function recordAction(actionType, element, value = '') {
        const action = {
            action_type: actionType,
            element_locators: generateLocators(element),
            element_name: getElementName(element),
            input_value: value,
            page_url: window.location.href,
            timestamp: Date.now()
        };

        window.__recorded_actions.push(action);

        // 通知录制引擎 / Notify recording engine
        window.dispatchEvent(new CustomEvent('__record_action', { detail: action }));
    }

    // 监听点击事件 / Listen to click events
    document.addEventListener('click', (event) => {
        const element = event.target;
        // 忽略 body 和 html / Ignore body and html
        if (element === document.body || element === document.documentElement) return;
        // 忽略录制控件本身 / Ignore recording controls
        if (element.closest('[data-recording-control]')) return;

        recordAction('click', element);
    }, true);

    // 监听输入事件 / Listen to input events
    document.addEventListener('input', (event) => {
        const element = event.target;
        if (element === document.body || element === document.documentElement) return;
        if (element.closest('[data-recording-control]')) return;

        recordAction('input', element, element.value);
    }, true);

    // 监听 change 事件（用于 select）/ Listen to change events (for select)
    document.addEventListener('change', (event) => {
        const element = event.target;
        if (element.tagName === 'SELECT') {
            recordAction('select', element, element.value);
        }
    }, true);

    // 监听键盘事件（Enter, Tab, Escape）/ Listen to keyboard events
    document.addEventListener('keydown', (event) => {
        if (['Enter', 'Tab', 'Escape'].includes(event.key)) {
            const element = event.target;
            if (element === document.body || element === document.documentElement) return;
            if (element.closest('[data-recording-control]')) return;

            recordAction('keyboard', element, event.key);
        }
    }, true);

    console.log('[Recording Engine] Event listeners initialized');
})();
"""


class RecordingEngine:
    """录制引擎类 / Recording engine class"""

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        timeout: int = 30000,
    ):
        """@Function: 初始化录制引擎配置 / Initialize recording engine config

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
        self._is_recording = False
        self._recorded_actions: List[Dict[str, Any]] = []
        self._on_action_callback: Optional[Callable] = None
        self._screenshot_dir = ""
        self._polling_task: Optional[asyncio.Task] = None

    async def launch(self) -> None:
        """@Function: 启动浏览器 / Launch browser"""
        logger.info(f"正在启动浏览器: {self._browser_type}, headless={self._headless}")
        self._playwright = await async_playwright().start()

        launcher = getattr(self._playwright, self._browser_type)
        self._browser = await launcher.launch(headless=self._headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True,
        )
        self._context.set_default_timeout(self._timeout)
        self._page = await self._context.new_page()

        # 创建截图目录 / Create screenshot directory
        self._screenshot_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "screenshots", f"record_{int(time.time())}"
        )
        os.makedirs(self._screenshot_dir, exist_ok=True)

        logger.info(f"录制引擎浏览器已启动成功: {self._browser_type}")

    async def start_recording(self, target_url: str = "") -> None:
        """@Function: 开始录制 / Start recording

        Args:
            target_url: 目标URL，为空则在当前页面开始 / Target URL, empty to start on current page
        """
        if not self._page:
            raise RuntimeError("浏览器未启动，请先调用 launch()")

        # 导航到目标URL / Navigate to target URL
        if target_url:
            logger.info(f"正在导航到目标页面: {target_url}")
            await self._page.goto(target_url, wait_until="domcontentloaded")
            logger.info(f"已打开目标页面: {target_url}")

        # 注入事件监听脚本 / Inject event listener script
        logger.info("正在注入事件监听脚本...")
        await self._inject_event_listeners()

        # 设置事件监听 / Setup event listeners
        await self._setup_action_listener()

        self._is_recording = True

        # 启动轮询任务 / Start polling task
        self._polling_task = asyncio.create_task(self._start_polling())

        logger.info("录制已开始，等待用户操作...")

    async def stop_recording(self) -> List[Dict[str, Any]]:
        """@Function: 停止录制并返回录制的操作 / Stop recording and return recorded actions

        Returns:
            录制的操作列表 / List of recorded actions
        """
        self._is_recording = False

        # 停止轮询 / Stop polling
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        # 从页面获取录制的操作 / Get recorded actions from page
        try:
            page_actions = await self._page.evaluate("() => window.__recorded_actions || []")
            self._recorded_actions.extend(page_actions)
        except Exception as e:
            logger.warning(f"获取页面录制数据失败 / Failed to get page recording data: {e}")

        logger.info(f"录制已停止，共 {len(self._recorded_actions)} 个操作 / Recording stopped, {len(self._recorded_actions)} actions")
        return self._recorded_actions

    async def _start_polling(self) -> None:
        """@Function: 开始轮询页面操作 / Start polling page actions"""
        last_count = 0
        consecutive_errors = 0
        max_consecutive_errors = 3  # 连续错误次数阈值

        while self._is_recording:
            try:
                await asyncio.sleep(1)  # 每秒轮询一次

                # 检查浏览器是否还活着
                if not self.is_alive:
                    logger.info("浏览器已关闭，停止轮询")
                    self._is_recording = False
                    break

                if not self._page:
                    break

                # 从页面获取录制的操作数量
                current_count = await self._page.evaluate("() => (window.__recorded_actions || []).length")
                consecutive_errors = 0  # 重置错误计数

                if current_count > last_count:
                    # 获取新操作
                    new_actions = await self._page.evaluate(
                        f"() => (window.__recorded_actions || []).slice({last_count})"
                    )

                    for action in new_actions:
                        # 截图
                        screenshot_path = await self._take_screenshot(action.get("action_type", "unknown"))
                        action["screenshot"] = screenshot_path

                        # 添加到录制列表
                        self._recorded_actions.append(action)

                        # 回调通知
                        if self._on_action_callback:
                            try:
                                await self._on_action_callback(action)
                            except Exception as e:
                                logger.error(f"回调执行失败: {e}")

                    last_count = current_count
                    logger.info(f"轮询获取到 {len(new_actions)} 个新操作")

            except asyncio.CancelledError:
                break
            except Exception as e:
                consecutive_errors += 1
                logger.warning(f"轮询操作失败 ({consecutive_errors}/{max_consecutive_errors}): {e}")

                # 如果连续错误次数超过阈值，停止轮询
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("连续错误次数过多，停止轮询")
                    self._is_recording = False
                    break

    async def _inject_event_listeners(self) -> None:
        """@Function: 注入事件监听脚本 / Inject event listener script"""
        try:
            await self._page.evaluate(EVENT_LISTENER_SCRIPT)
            logger.info("事件监听脚本已注入 / Event listener script injected")
        except Exception as e:
            logger.error(f"注入事件监听脚本失败 / Failed to inject event listener: {e}")
            raise

    async def _setup_action_listener(self) -> None:
        """@Function: 设置操作监听器 / Setup action listener"""
        # 监听页面导航事件 / Listen to page navigation events
        self._page.on("framenavigated", self._on_navigation)

    async def _on_navigation(self, frame) -> None:
        """@Function: 处理页面导航事件 / Handle page navigation event"""
        if not self._is_recording:
            return

        # 只处理主框架 / Only handle main frame
        if frame != self._page.main_frame:
            return

        url = frame.url
        logger.info(f"页面导航 / Page navigation: {url}")

        # 记录导航操作 / Record navigation action
        action = {
            "action_type": "navigate",
            "element_locators": {},
            "element_name": "页面导航",
            "input_value": url,
            "page_url": url,
            "timestamp": int(time.time() * 1000),
        }
        self._recorded_actions.append(action)

        # 重新注入事件监听脚本 / Re-inject event listener script
        try:
            await asyncio.sleep(0.5)  # 等待页面加载 / Wait for page load
            await self._inject_event_listeners()
        except Exception as e:
            logger.warning(f"重新注入脚本失败 / Failed to re-inject script: {e}")

        # 截图 / Take screenshot
        await self._take_screenshot("navigate")

        # 回调通知 / Callback notification
        if self._on_action_callback:
            await self._on_action_callback(action)

    async def _take_screenshot(self, action_type: str) -> str:
        """@Function: 截图 / Take screenshot

        Args:
            action_type: 操作类型

        Returns:
            截图文件路径
        """
        try:
            timestamp = int(time.time() * 1000)
            filename = f"{action_type}_{timestamp}.png"
            filepath = os.path.join(self._screenshot_dir, filename)

            await self._page.screenshot(path=filepath, full_page=False)
            logger.info(f"截图已保存 / Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.warning(f"截图失败 / Screenshot failed: {e}")
            return ""

    def set_on_action_callback(self, callback: Callable) -> None:
        """@Function: 设置操作回调 / Set action callback

        Args:
            callback: 回调函数 / Callback function
        """
        self._on_action_callback = callback

    async def navigate(self, url: str) -> None:
        """@Function: 导航到URL / Navigate to URL

        Args:
            url: 目标URL
        """
        if not self._page:
            raise RuntimeError("浏览器未启动")

        await self._page.goto(url, wait_until="domcontentloaded")
        logger.info(f"已导航到 / Navigated to: {url}")

    async def close(self) -> None:
        """@Function: 关闭浏览器 / Close browser"""
        self._is_recording = False

        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("录制引擎浏览器已关闭 / Recording engine browser closed")
        except Exception as e:
            logger.warning(f"关闭浏览器时出样 / Error closing browser: {e}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

    @property
    def is_recording(self) -> bool:
        """是否正在录制 / Whether recording"""
        return self._is_recording

    @property
    def recorded_actions(self) -> List[Dict[str, Any]]:
        """获取录制的操作 / Get recorded actions"""
        return self._recorded_actions

    @property
    def page(self) -> Optional[Page]:
        """获取当前页面 / Get current page"""
        return self._page

    @property
    def is_alive(self) -> bool:
        """浏览器是否存活 / Whether browser is alive"""
        return self._browser is not None and self._browser.is_connected()
