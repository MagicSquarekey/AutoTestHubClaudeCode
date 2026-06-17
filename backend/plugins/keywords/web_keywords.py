# -*- coding: utf-8 -*-
"""
Web 关键字实现 / Web keyword implementations
@Function: 将测试关键字映射到 WebDriver 操作 / Map test keywords to WebDriver operations
"""

import os
from typing import Dict, Any, Optional
from app.driver.web_driver import WebDriver
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("web_keywords")


async def execute_keyword(driver: WebDriver, keyword: str, params: Dict[str, Any], timeout: int = 30000) -> Dict[str, Any]:
    """@Function: 执行单个关键字 / Execute a single keyword

    Args:
        driver: WebDriver 实例
        keyword: 关键字名称
        params: 关键字参数
        timeout: 超时时间（毫秒）

    Returns:
        执行结果 {"success": bool, "message": str, "data": any}
    """
    handler = KEYWORD_MAP.get(keyword)
    if not handler:
        return {"success": False, "message": f"未实现的关键字 / Unsupported keyword: {keyword}"}

    try:
        result = await handler(driver, params, timeout)
        return {"success": True, "message": "执行成功", "data": result}
    except Exception as e:
        logger.error(f"关键字 {keyword} 执行失败: {e}")
        return {"success": False, "message": str(e)}


# ========== 关键字处理函数 / Keyword handlers ==========

async def _open_url(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """打开 URL"""
    url = params.get("url", "")
    if not url:
        raise ValueError("URL 不能为空")
    await driver.goto(url, timeout=timeout)


async def _click(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """点击元素"""
    element = params.get("element", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.click(element, timeout=timeout)


async def _input_text(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """输入文本"""
    element = params.get("element", "")
    value = params.get("value", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.fill(element, value, timeout=timeout)


async def _clear_input(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """清空输入"""
    element = params.get("element", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.clear_input(element, timeout=timeout)


async def _hover(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """鼠标悬停"""
    element = params.get("element", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.hover(element, timeout=timeout)


async def _select(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """下拉选择"""
    element = params.get("element", "")
    value = params.get("value", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.select(element, value, timeout=timeout)


async def _upload_file(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """上传文件"""
    element = params.get("element", "")
    file_path = params.get("file_path", "")
    if not element or not file_path:
        raise ValueError("元素选择器和文件路径不能为空")
    await driver.upload_file(element, file_path, timeout=timeout)


async def _switch_iframe(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """切换 iframe"""
    iframe = params.get("iframe", "")
    if not iframe:
        raise ValueError("iframe 选择器不能为空")
    await driver.switch_iframe(iframe)


async def _switch_window(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """切换窗口"""
    window_index = params.get("window_index", 0)
    await driver.switch_window(int(window_index))


async def _wait(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """等待"""
    seconds = float(params.get("timeout", 5))
    await driver.wait(seconds)


async def _screenshot(driver: WebDriver, params: Dict[str, Any], timeout: int) -> str:
    """截图"""
    save_dir = settings.SCREENSHOT_DIR
    import time
    filename = f"screenshot_{int(time.time() * 1000)}.png"
    save_path = os.path.join(save_dir, filename)
    return await driver.screenshot(save_path)


async def _execute_js(driver: WebDriver, params: Dict[str, Any], timeout: int) -> Any:
    """执行 JavaScript"""
    script = params.get("script", "")
    if not script:
        raise ValueError("JS 脚本不能为空")
    return await driver.execute_js(script)


async def _assert_text(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """断言文本"""
    expected = params.get("expected", "")
    element = params.get("element", "")
    if element:
        actual = await driver.get_text(element, timeout=timeout)
    else:
        actual = await driver.get_text("body")

    if expected not in actual:
        raise AssertionError(f"断言失败: 期望包含 '{expected}', 实际 '{actual[:100]}'")


async def _assert_element_exists(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """断言元素存在"""
    element = params.get("element", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.wait_for_selector(element, timeout=timeout)


async def _assert_url(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """断言 URL"""
    expected = params.get("expected", "")
    actual = await driver.get_url()
    if expected not in actual:
        raise AssertionError(f"URL 断言失败: 期望包含 '{expected}', 实际 '{actual}'")


async def _assert_title(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """断言标题"""
    expected = params.get("expected", "")
    actual = await driver.get_title()
    if expected not in actual:
        raise AssertionError(f"标题断言失败: 期望包含 '{expected}', 实际 '{actual}'")


async def _wait_for_element(driver: WebDriver, params: Dict[str, Any], timeout: int) -> None:
    """等待元素出现"""
    element = params.get("element", "")
    if not element:
        raise ValueError("元素选择器不能为空")
    await driver.wait_for_selector(element, timeout=timeout)


# ========== 关键字映射表 / Keyword mapping ==========

KEYWORD_MAP = {
    "open_url": _open_url,
    "click": _click,
    "input_text": _input_text,
    "clear_input": _clear_input,
    "hover": _hover,
    "select": _select,
    "upload_file": _upload_file,
    "switch_iframe": _switch_iframe,
    "switch_window": _switch_window,
    "wait": _wait,
    "screenshot": _screenshot,
    "execute_js": _execute_js,
    "assert_text": _assert_text,
    "assert_element_exists": _assert_element_exists,
    "assert_url": _assert_url,
    "assert_title": _assert_title,
    "wait_for_element": _wait_for_element,
}
