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


async def _auto_detect_login_button(driver: WebDriver) -> str:
    """@Function: 自动检测页面上的登录/提交按钮

    在用户未配置 login_button_selector 时，智能搜索页面上的登录按钮。
    优先匹配包含"登录"文字的按钮，其次匹配 submit 类型按钮。

    Args:
        driver: WebDriver 实例

    Returns:
        匹配到的选择器字符串，未找到返回空字符串
    """
    # 候选选择器列表（按优先级排列）
    candidates = [
        # 包含"登录"文字的按钮（最常见）
        "button:has-text('登录')",
        "button:has-text('登 录')",
        "button:has-text('Login')",
        "button:has-text('Sign in')",
        # submit 类型按钮
        "button[type='submit']",
        "input[type='submit']",
        # 常见登录按钮 class/id
        ".login-btn",
        ".btn-login",
        "#loginBtn",
        "#login-btn",
    ]

    for sel in candidates:
        try:
            locator = driver.page.locator(sel)
            count = await locator.count()
            if count == 1:
                return sel
            elif count > 1:
                # 多个匹配时，检查是否在登录表单内
                for i in range(count):
                    el = locator.nth(i)
                    visible = await el.is_visible()
                    if visible:
                        return sel
        except Exception:
            continue

    return ""


async def _detect_error_popup(driver: WebDriver, error_patterns: list) -> tuple:
    """@Function: 检测页面上是否出现错误提示弹窗

    Args:
        driver: WebDriver 实例
        error_patterns: 错误提示文本模式列表

    Returns:
        (error_detected: bool, detected_msg: str)
    """
    for pattern in error_patterns:
        try:
            # 方法1: 使用 text= 选择器
            error_locator = driver.page.locator(f"text={pattern}")
            error_count = await error_locator.count()
            if error_count > 0:
                return True, pattern

            # 方法2: 使用 contains 选择器（更宽松）
            error_locator2 = driver.page.locator(f"text*={pattern}")
            error_count2 = await error_locator2.count()
            if error_count2 > 0:
                return True, pattern
        except Exception:
            continue

    # 方法3: 检查常见的错误弹窗结构（如 el-message-box, ant-modal-confirm）
    try:
        # 检查 el-message-box 中的错误文本
        msg_box = driver.page.locator(".el-message-box")
        if await msg_box.count() > 0:
            msg_text = await msg_box.inner_text()
            for pattern in error_patterns:
                if pattern in msg_text:
                    return True, pattern

        # 检查 ant-modal-confirm 中的错误文本
        ant_modal = driver.page.locator(".ant-modal-confirm")
        if await ant_modal.count() > 0:
            modal_text = await ant_modal.inner_text()
            for pattern in error_patterns:
                if pattern in modal_text:
                    return True, pattern

        # 检查 el-notification 中的错误文本
        notification = driver.page.locator(".el-notification")
        if await notification.count() > 0:
            notif_text = await notification.inner_text()
            for pattern in error_patterns:
                if pattern in notif_text:
                    return True, pattern
    except Exception:
        pass

    return False, ""


async def _dismiss_error_popup(driver: WebDriver, dismiss_button_selector: str) -> None:
    """@Function: 关闭错误提示弹窗

    优先使用用户配置的 dismiss_button_selector，未配置时自动尝试常见弹窗关闭方式。

    Args:
        driver: WebDriver 实例
        dismiss_button_selector: 用户配置的关闭按钮选择器
    """
    dismissed = False

    # 1. 使用用户配置的选择器
    if dismiss_button_selector:
        try:
            dismiss_btn = driver.page.locator(dismiss_button_selector)
            if await dismiss_btn.count() > 0:
                await dismiss_btn.first.click()
                logger.info(f"[solve_captcha] 已点击关闭按钮: {dismiss_button_selector}")
                dismissed = True
        except Exception as e:
            logger.warning(f"[solve_captcha] 点击关闭按钮失败: {e}")

    # 2. 自动尝试常见弹窗关闭方式
    if not dismissed:
        auto_selectors = [
            "button:has-text('知道了')",
            "button:has-text('确定')",
            "button:has-text('确认')",
            "button:has-text('OK')",
            ".ant-modal-confirm-btns button",
            ".ant-notification-notice-close",
            ".el-message-box__btns button",
            ".el-notification__closeBtn",
        ]
        for sel in auto_selectors:
            try:
                btn = driver.page.locator(sel)
                if await btn.count() > 0:
                    await btn.first.click()
                    logger.info(f"[solve_captcha] 自动关闭弹窗: {sel}")
                    dismissed = True
                    break
            except Exception:
                continue

    # 3. 最后兜底：按 Escape
    if not dismissed:
        logger.info("[solve_captcha] 未找到关闭按钮，尝试 Escape 关闭弹窗")
        await driver.page.keyboard.press("Escape")

    await asyncio.sleep(0.5)


async def _solve_captcha(driver: WebDriver, params: Dict[str, Any], timeout: int) -> str:
    """@Function: 识别并输入验证码 / Recognize and input captcha

    完整流程：
    1. 按优先级候选列表定位验证码图片（精确匹配1个元素才采用）
    2. 按优先级候选列表定位验证码输入框（精确匹配1个元素才采用）
    3. 截图验证码图片 → OCR 识别（多种预处理策略重试） → 输入到验证码输入框
    4. OCR 识别失败时根据 on_fail 策略处理：
       - stop: 抛出异常停止执行
       - skip: 跳过验证码步骤继续
       - manual: 暂停等待人工输入
    5. 自动检测登录按钮（用户未配置 login_button_selector 时，智能搜索页面上的登录按钮）
    6. 点击登录按钮 → 检测错误弹窗 → 自动关闭弹窗 → 重新识别验证码 → 重试
    7. 最多重试 max_login_retries 次，每次使用不同的 OCR 预处理策略
       - "stop"（默认）：抛出异常终止用例
       - "skip"：跳过验证码步骤，继续执行
       - "manual"：暂停执行，等待人工输入验证码（仅非 headless 模式）
    5. 如果配置了 login_button_selector，输入验证码后自动点击登录并检测错误：
       - 检测到错误提示 → 关闭提示 → 重新识别验证码 → 重试
       - 未检测到错误 → 登录成功
       - 达到最大重试次数 → 抛出异常

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
            - login_button_selector: 登录按钮选择器（为空则不自动点击登录，保持原有行为）
            - error_text: 登录失败提示文本（默认: "验证码不匹配"）
            - dismiss_button_selector: 关闭错误提示的按钮选择器（如"知道了"按钮）
            - max_login_retries: 登录重试次数（默认: 3）
            - login_wait_ms: 点击登录后等待时间毫秒（默认: 2000）
            - engine: 执行引擎实例（人工介入时需要，由执行引擎自动注入）
            - task_id: 调试任务ID（人工介入时用于前端推送）
        timeout: 超时时间

    Returns:
        识别出的验证码文本，如果跳过则返回 "[SKIPPED]"

    Raises:
        RuntimeError: 无法定位验证码图片或输入框时，或 OCR 识别失败且策略为 stop 时，
                      或登录重试次数耗尽时
    """
    from app.service.ocr_service import ocr_service

    # 获取参数
    on_fail = params.get("on_fail", "stop")  # stop / skip / manual
    engine = params.get("engine")  # 执行引擎实例（人工介入时需要）
    task_id = params.get("task_id")

    # 登录重试相关参数
    login_button_selector = params.get("login_button_selector", "")
    error_text = params.get("error_text", "")
    dismiss_button_selector = params.get("dismiss_button_selector", "")
    max_login_retries = params.get("max_login_retries", 3)
    login_wait_ms = params.get("login_wait_ms", 3000)

    # 自动检测登录按钮（用户未配置时，智能搜索页面上的登录/提交按钮）
    if not login_button_selector:
        login_button_selector = await _auto_detect_login_button(driver)
        if login_button_selector:
            logger.info(f"[solve_captcha] 自动检测到登录按钮: {login_button_selector}")

    has_login_retry = bool(login_button_selector)

    # 默认错误文本候选列表（中英文常见验证码错误提示）
    DEFAULT_ERROR_TEXTS = [
        "验证码不匹配", "验证码错误", "验证码不正确", "验证码已过期",
        "验证码过期", "请输入正确的验证码", "验证失败", "captcha error",
        "incorrect captcha", "invalid captcha", "captcha mismatch",
        "验证码输入错误", "验证码无效", "请重新输入验证码", "图形验证码错误",
    ]
    # 将用户指定的 error_text + 默认列表合并，去重
    error_patterns = list(dict.fromkeys(
        [error_text] + DEFAULT_ERROR_TEXTS if error_text else DEFAULT_ERROR_TEXTS
    ))


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

    # 截图验证码（支持登录重试循环）
    login_attempt = 0
    max_login_attempts = max_login_retries if has_login_retry else 1

    while login_attempt < max_login_attempts:
        if login_attempt > 0:
            logger.info(f"[solve_captcha] 登录重试第 {login_attempt} 次...")

        # 等待验证码图片加载
        await driver.wait_for_selector(resolved_captcha_selector, timeout=5000)

        # 截图验证码
        save_dir = settings.SCREENSHOT_DIR
        filename = f"captcha_{int(time.time() * 1000)}.png"
        screenshot_path = os.path.join(save_dir, filename)

        captcha_element = driver.page.locator(resolved_captcha_selector)
        await captcha_element.screenshot(path=screenshot_path)
        logger.info(f"验证码截图已保存: {screenshot_path}")

        # OCR 识别验证码（外层重试：每次刷新截图 + 不同预处理策略）
        captcha_text = None
        last_error = None
        # 预处理策略列表：每次重试尝试不同策略
        preprocess_strategies = [
            {"preprocess": False},                      # 原始图片
            {"preprocess": True},                       # 自适应二值化
            {"alt": True},                              # 固定阈值 + 形态学 + 反色
            {"preprocess": True, "invert": True},       # 自适应二值化 + 反色
        ]

        for attempt in range(max_retries):
            try:
                # 选择预处理策略（循环使用）
                strategy = preprocess_strategies[attempt % len(preprocess_strategies)]

                if strategy.get("alt"):
                    text = ocr_service.recognize_with_alt_method(screenshot_path)
                else:
                    text = ocr_service.recognize(
                        screenshot_path,
                        preprocess=strategy.get("preprocess", False),
                    )
                    # 可选反色处理
                    if strategy.get("invert"):
                        import cv2
                        img = cv2.imread(screenshot_path)
                        if img is not None:
                            inverted = cv2.bitwise_not(img)
                            inv_path = screenshot_path.replace('.png', '_inv.png')
                            cv2.imwrite(inv_path, inverted)
                            try:
                                text = ocr_service.recognize(inv_path, preprocess=False)
                            finally:
                                if os.path.exists(inv_path):
                                    os.remove(inv_path)

                captcha_text = text

                if not captcha_text:
                    raise ValueError("OCR 返回空结果")

                # 长度校验
                if len(captcha_text) != expected_length:
                    logger.warning(f"[solve_captcha] OCR 识别结果长度不符: {captcha_text} (期望 {expected_length} 位，实际 {len(captcha_text)} 位，策略 {attempt + 1})")
                    if attempt < max_retries - 1:
                        logger.info(f"[solve_captcha] OCR 重试 {attempt + 2}/{max_retries}...")
                        await asyncio.sleep(1.0)
                        await captcha_element.screenshot(path=screenshot_path)
                        continue
                    else:
                        raise ValueError(f"验证码长度不符: 期望{expected_length}位, 实际{len(captcha_text)}位")

                logger.info(f"[solve_captcha] OCR 识别成功 (策略 {attempt + 1}): {captcha_text}")
                break  # 识别成功

            except Exception as e:
                last_error = e
                logger.warning(f"[solve_captcha] OCR 识别失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                captcha_text = None  # 重置，避免空字符串穿透
                if attempt < max_retries - 1:
                    logger.info(f"[solve_captcha] OCR 重试 {attempt + 2}/{max_retries}...")
                    try:
                        await asyncio.sleep(0.5)
                        await captcha_element.screenshot(path=screenshot_path)
                    except Exception:
                        pass

        # 检查 OCR 是否最终成功
        if not captcha_text:
            if has_login_retry:
                # 登录重试模式下，OCR 失败也尝试重试
                logger.warning(f"[solve_captcha] OCR 识别失败，将在登录重试中重新尝试")
                # 清理临时文件
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                login_attempt += 1
                continue
            elif on_fail == "skip":
                logger.warning(f"[solve_captcha] OCR 识别失败，跳过验证码步骤: {last_error}")
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                return "[SKIPPED]"
            elif on_fail == "manual":
                # 人工介入模式
                if engine is None:
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)
                    raise RuntimeError("OCR 识别失败，且未提供执行引擎实例用于人工介入")

                if not hasattr(engine, 'pause_for_manual_input'):
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)
                    raise RuntimeError("OCR 识别失败，执行引擎不支持暂停功能")

                logger.info("[solve_captcha] 策略为 manual，暂停执行等待人工输入...")
                captcha_text = await engine.pause_for_manual_input(
                    screenshot_path=screenshot_path,
                    captcha_selector=resolved_captcha_selector,
                    input_selector=resolved_input_selector,
                    task_id=task_id,
                )

                if not captcha_text:
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)
                    raise RuntimeError("人工介入失败：未收到用户输入的验证码")

                logger.info(f"[solve_captcha] 收到人工输入的验证码: {captcha_text}")
            else:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                raise RuntimeError("OCR 识别失败")
        else:
            logger.info(f"[solve_captcha] 验证码识别成功: {captcha_text}")

        # 输入验证码（已验证选择器精确匹配 1 个元素）
        input_locator = driver.page.locator(resolved_input_selector)
        input_count = await input_locator.count()
        if input_count == 0:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            raise RuntimeError(f"验证码输入框未找到: {resolved_input_selector}")

        await input_locator.clear()
        await input_locator.type(captcha_text, delay=50)
        await input_locator.dispatch_event('blur')
        await asyncio.sleep(0.3)

        actual_value = await input_locator.input_value()
        if actual_value != captcha_text:
            logger.warning(f"[solve_captcha] 验证码输入验证不匹配: 期望={captcha_text}, 实际={actual_value}")

        logger.info(f"[solve_captcha] 验证码已输入到 {resolved_input_selector}, 值: {captcha_text}")

        # 清理临时文件
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        # 如果没有登录重试配置，直接返回（保持向后兼容）
        if not has_login_retry:
            return captcha_text

        # === 登录重试模式 ===
        # 点击登录按钮
        login_btn = driver.page.locator(login_button_selector)
        login_btn_count = await login_btn.count()
        if login_btn_count == 0:
            raise RuntimeError(f"登录按钮未找到: {login_button_selector}")
        if login_btn_count > 1:
            logger.warning(f"[solve_captcha] 登录按钮选择器匹配到 {login_btn_count} 个元素，使用第一个")

        # 记录点击登录前的 URL，用于检测登录跳转
        url_before_login = driver.page.url

        await login_btn.first.click()
        logger.info(f"[solve_captcha] 已点击登录按钮: {login_button_selector}")

        # 等待页面响应（使用 networkidle 提升稳定性）
        try:
            await driver.page.wait_for_load_state("networkidle", timeout=login_wait_ms)
        except Exception:
            # 超时不影响主流程，仅等待固定时间兜底
            await asyncio.sleep(login_wait_ms / 1000)

        # 检测是否出现错误提示（多模式匹配）
        error_detected, detected_error_msg = await _detect_error_popup(driver, error_patterns)

        # 首次未检测到错误时，再等一下检查延迟出现的弹窗
        if not error_detected:
            await asyncio.sleep(1.0)
            error_detected, detected_error_msg = await _detect_error_popup(driver, error_patterns)

        if error_detected:
            logger.warning(f"[solve_captcha] 检测到登录错误提示: {detected_error_msg}")
        else:
            # 无文本错误提示，再通过 URL 变化判断是否登录成功
            url_after_login = driver.page.url
            if url_after_login != url_before_login:
                logger.info(f"[solve_captcha] 登录成功（页面已跳转）: {url_before_login} -> {url_after_login}")
                return captcha_text
            # URL 未变且无错误文本 → 可能成功，也可能错误提示非文本型
            logger.info("[solve_captcha] 未检测到错误提示且页面未跳转，视为登录成功")
            return captcha_text

        # 检测到错误，尝试关闭提示弹窗
        await _dismiss_error_popup(driver, dismiss_button_selector)

        # 清空验证码输入框，准备重新输入
        try:
            input_el = driver.page.locator(resolved_input_selector)
            if await input_el.count() > 0:
                await input_el.first.clear()
                logger.info("[solve_captcha] 已清空验证码输入框")
        except Exception as e:
            logger.warning(f"[solve_captcha] 清空输入框失败: {e}")

        # 等待验证码图片刷新
        try:
            captcha_el = driver.page.locator(resolved_captcha_selector)
            await captcha_el.first.wait_for(timeout=5000)
        except Exception:
            pass
        await asyncio.sleep(1.0)  # 额外等待验证码图片刷新

        login_attempt += 1


    # 循环结束，所有重试都失败了
    raise RuntimeError(f"验证码识别失败，已达最大登录重试次数 ({max_login_retries})")


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
