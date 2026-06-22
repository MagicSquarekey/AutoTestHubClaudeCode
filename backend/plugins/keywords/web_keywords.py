# -*- coding: utf-8 -*-
"""
Web 关键字实现 / Web keyword implementations
@Function: 将测试关键字映射到 WebDriver 操作 / Map test keywords to WebDriver operations
"""

import asyncio
import os
import time
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


async def _solve_captcha(driver: WebDriver, params: Dict[str, Any], timeout: int) -> str:
    """@Function: 识别并输入验证码 / Recognize and input captcha

    流程：
    1. 按优先级候选列表定位验证码图片（精确匹配1个元素才采用）
    2. 按优先级候选列表定位验证码输入框（精确匹配1个元素才采用）
    3. 截图验证码图片 → OCR 识别 → 输入到验证码输入框
    4. OCR 识别失败时根据 on_fail 策略处理：
       - "stop"（默认）：抛出异常终止用例
       - "skip"：跳过验证码步骤，继续执行
       - "manual"：暂停执行，等待人工输入验证码（仅非 headless 模式）

    选择器解析规则：
    - 用户通过 params 传入的选择器优先使用
    - 未传入时使用内置候选列表，按优先级逐个尝试：
      验证码图片: img.captcha > span.ant-input-suffix img > .verify-code img > img[src*='captcha/verify/code']
      输入框:     input[placeholder*='验证码'] > input[name='captcha'] > input[name='verify'] > input[name*='code'] > input[autocomplete='one-time-code']
    - 每个候选选择器会先验证匹配元素数量，必须恰好匹配1个才采用
    - 匹配到多个元素时跳过（避免验证码填入错误位置）
    - 所有候选均失败则抛出 RuntimeError，附带已尝试的选择器列表

    Args:
        driver: WebDriver 实例
        params: 参数字典
            - captcha_selector: 验证码图片选择器（传入精确选择器可跳过候选匹配）
            - input_selector: 验证码输入框选择器（传入精确选择器可跳过候选匹配）
            - expected_length: 期望验证码长度 (默认: 4)
            - max_retries: 最大重试次数 (默认: 3)
            - on_fail: 失败策略 "stop"|"skip"|"manual" (默认: "stop")
            - engine: 执行引擎实例（人工介入时需要，由执行引擎自动注入）
            - task_id: 调试任务ID（人工介入时用于前端推送）
        timeout: 超时时间

    Returns:
        识别出的验证码文本，如果跳过则返回 "[SKIPPED]"

    Raises:
        RuntimeError: 无法定位验证码图片或输入框时，或 OCR 识别失败且策略为 stop 时
    """
    from app.service.ocr_service import ocr_service

    # 获取参数
    on_fail = params.get("on_fail", "stop")  # stop / skip / manual
    engine = params.get("engine")  # 执行引擎实例（人工介入时需要）
    task_id = params.get("task_id")

    # 验证码图片选择器：按优先级排列，从最精确到最宽泛
    # @Note: 用户应优先通过 params 传入精确的 captcha_selector
    captcha_selector_candidates = [
        params.get("captcha_selector", ""),
    ]
    if not captcha_selector_candidates[0]:
        captcha_selector_candidates = [
            # 常见验证码图片 class/id
            "img.captcha",
            "img#captcha",
            "img#captchaImg",
            "img#verifyCodeImg",
            "img.verify-img",
            # Ant Design / Element Plus 等 UI 框架
            "span.ant-input-suffix img",
            ".el-input-suffix img",
            ".verify-code img",
            "#login-code img",
            ".login-code img",
            # src 属性匹配（最通用）
            "img[src*='captcha']",
            "img[src*='verify']",
            "img[src*='code']",
            "img[src*='yzm']",
            "img[src*='yzmImage']",
            "img[src*='getCode']",
            "img[src*='checkcode']",
            # base64 格式的验证码（很多网站用）
            "img[src^='data:image']",
        ]

    # 验证码输入框选择器：按优先级排列
    input_selector_candidates = [
        params.get("input_selector", ""),
    ]
    if not input_selector_candidates[0]:
        input_selector_candidates = [
            "input[placeholder*='验证码']",
            "input[name='captcha']",
            "input[name='verify']",
            "input[name*='code']",
            "input[autocomplete='one-time-code']",
        ]

    expected_length = int(params.get("expected_length", 4))
    max_retries = int(params.get("max_retries", 3))

    # --- 选择器匹配验证 / Selector matching verification ---
    # 验证验证码图片选择器：确保精确匹配到1个元素
    resolved_captcha_selector = None
    for sel in captcha_selector_candidates:
        if not sel:
            continue
        count = await driver.page.locator(sel).count()
        if count == 1:
            resolved_captcha_selector = sel
            break
        elif count > 1:
            logger.warning(f"[solve_captcha] 选择器 '{sel}' 匹配到 {count} 个元素，跳过以避免歧义")
            continue

    # 智能兜底：如果所有选择器都失败，用 JS 搜索页面上可能是验证码的 img 元素
    # 优先找靠近验证码输入框的 img，或 src 为 base64 的小尺寸 img
    if not resolved_captcha_selector:
        logger.info("[solve_captcha] 所有预设选择器失败，尝试 JS 智能搜索验证码图片...")
        try:
            js_find_captcha = """
            (() => {
                // 1. 找到验证码输入框
                let inputEl = null;
                const inputSelectors = INPUT_SELECTORS_PLACEHOLDER;
                for (const sel of inputSelectors) {
                    try {
                        const el = document.querySelector(sel);
                        if (el) { inputEl = el; break; }
                    } catch(e) {}
                }

                // 2. 收集页面上所有 img 元素
                const allImgs = Array.from(document.querySelectorAll('img'));
                if (allImgs.length === 0) return null;

                // 3. 评分排序：找出最像验证码的 img
                const scored = allImgs.map(img => {
                    let score = 0;
                    const src = img.src || '';
                    const w = img.offsetWidth || img.width;
                    const h = img.offsetHeight || img.height;

                    // base64 格式加分（很多验证码用 base64）
                    if (src.startsWith('data:image')) score += 30;

                    // 尺寸在合理范围内加分（验证码通常 60-200px 宽，30-100px 高）
                    if (w >= 50 && w <= 250 && h >= 20 && h <= 120) score += 20;

                    // 宽高比合理（通常 1.5:1 到 4:1）
                    const ratio = w / (h || 1);
                    if (ratio >= 1.2 && ratio <= 5) score += 10;

                    // 靠近验证码输入框加分
                    if (inputEl) {
                        const inputRect = inputEl.getBoundingClientRect();
                        const imgRect = img.getBoundingClientRect();
                        const dist = Math.abs(imgRect.right - inputRect.left);
                        if (dist < 200) score += 25;
                        if (dist < 100) score += 15;
                    }

                    // class/id 包含验证码相关词加分
                    const cls = (img.className || '').toLowerCase();
                    const id = (img.id || '').toLowerCase();
                    if (/captcha|verify|code|yzm|check/.test(cls + id)) score += 40;

                    return { img, score };
                });

                scored.sort((a, b) => b.score - a.score);

                // 返回得分最高的（分数需要大于 30 才认为是验证码）
                if (scored.length > 0 && scored[0].score > 30) {
                    // 动态创建一个选择器来定位这个元素
                    const best = scored[0].img;
                    if (best.id) return ' #' + best.id;
                    // 给元素临时加个 data 属性用于定位
                    best.setAttribute('data-captcha-auto', 'true');
                    return "[data-captcha-auto='true']";
                }
                return null;
            })()
            """.replace("INPUT_SELECTORS_PLACEHOLDER", str(input_selector_candidates))
            auto_selector = await driver.page.evaluate(js_find_captcha)
            if auto_selector:
                resolved_captcha_selector = auto_selector
                logger.info(f"[solve_captcha] JS 智能搜索找到验证码图片选择器: {auto_selector}")
        except Exception as e:
            logger.warning(f"[solve_captcha] JS 智能搜索失败: {e}")

    if not resolved_captcha_selector:
        tried = [s for s in captcha_selector_candidates if s]
        raise RuntimeError(
            f"[solve_captcha] 无法定位验证码图片元素。"
            f"已尝试的选择器: {tried}。"
            f"请通过 captcha_selector 参数传入精确的CSS选择器。"
        )
    logger.info(f"[solve_captcha] 使用验证码图片选择器: {resolved_captcha_selector}")

    # 验证验证码输入框选择器：确保精确匹配到1个元素
    resolved_input_selector = None
    for sel in input_selector_candidates:
        if not sel:
            continue
        count = await driver.page.locator(sel).count()
        if count == 1:
            resolved_input_selector = sel
            break
        elif count > 1:
            logger.warning(f"[solve_captcha] 选择器 '{sel}' 匹配到 {count} 个输入框，跳过以避免验证码填入错误位置")
            continue

    if not resolved_input_selector:
        tried = [s for s in input_selector_candidates if s]
        raise RuntimeError(
            f"[solve_captcha] 无法定位验证码输入框。"
            f"已尝试的选择器: {tried}。"
            f"请通过 input_selector 参数传入精确的CSS选择器。"
        )
    logger.info(f"[solve_captcha] 使用验证码输入框选择器: {resolved_input_selector}")

    # 截图验证码
    save_dir = settings.SCREENSHOT_DIR
    filename = f"captcha_{int(time.time() * 1000)}.png"
    screenshot_path = os.path.join(save_dir, filename)

    # 等待验证码图片加载
    await driver.wait_for_selector(resolved_captcha_selector, timeout=5000)

    # 截图
    captcha_element = driver.page.locator(resolved_captcha_selector)
    await captcha_element.screenshot(path=screenshot_path)

    logger.info(f"验证码截图已保存: {screenshot_path}")

    try:
        # OCR 识别
        captcha_text = ocr_service.recognize_with_retry(
            screenshot_path,
            max_retries=max_retries,
            expected_length=expected_length
        )

        if not captcha_text:
            # OCR 识别失败，根据策略处理
            logger.warning("[solve_captcha] OCR 识别失败")

            if on_fail == "skip":
                logger.info("[solve_captcha] 策略为 skip，跳过验证码步骤")
                return "[SKIPPED]"

            elif on_fail == "manual":
                # 人工介入模式
                if engine is None:
                    logger.warning("[solve_captcha] 未提供执行引擎实例，无法启用人工介入，回退到 stop 策略")
                    raise RuntimeError("验证码识别失败，且未提供执行引擎实例用于人工介入")

                if not hasattr(engine, 'pause_for_manual_input'):
                    logger.warning("[solve_captcha] 执行引擎不支持暂停功能，回退到 stop 策略")
                    raise RuntimeError("验证码识别失败，执行引擎不支持暂停功能")

                # 暂停执行，等待人工输入
                logger.info("[solve_captcha] 策略为 manual，暂停执行等待人工输入...")
                captcha_text = await engine.pause_for_manual_input(
                    screenshot_path=screenshot_path,
                    captcha_selector=resolved_captcha_selector,
                    input_selector=resolved_input_selector,
                    task_id=task_id,
                )

                if not captcha_text:
                    raise RuntimeError("人工介入失败：未收到用户输入的验证码")

                logger.info(f"[solve_captcha] 收到人工输入的验证码: {captcha_text}")

            else:
                # 默认 stop 策略
                raise RuntimeError("验证码识别失败")

        else:
            logger.info(f"[solve_captcha] 验证码识别成功: {captcha_text}")

        # 输入验证码（已验证选择器精确匹配1个元素）
        # 先清空输入框
        await driver.page.locator(resolved_input_selector).clear()
        # 使用 type 而不是 fill，模拟真实键盘输入
        await driver.page.locator(resolved_input_selector).type(captcha_text, delay=50)

        # 触发 blur 事件，确保输入值被框架识别
        await driver.page.locator(resolved_input_selector).dispatch_event('blur')

        # 短暂等待，让框架处理输入
        await asyncio.sleep(0.2)

        return captcha_text

    finally:
        # 清理临时文件
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)


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
    "solve_captcha": _solve_captcha,
}
