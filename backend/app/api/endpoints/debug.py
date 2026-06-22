# -*- coding: utf-8 -*-
"""
调试运行 API / Debug run API
@Function: 提供用例调试运行接口 / Provide test case debug run endpoint
"""

import json
import asyncio
import threading
import time
import re
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.case_service import CaseService
from app.engine.execution_engine import ExecutionEngine
from app.utils.logger import get_logger

logger = get_logger("debug_api")

router = APIRouter()

# 动态类名模式 / Dynamic class patterns
DYNAMIC_CLASS_PATTERNS = [
    'focused', 'active', 'hover', 'disabled', 'selected', 'checked',
    'open', 'visible', 'hidden', 'loading', 'error', 'success', 'warning',
    'ant-motion', 'fade-', 'slide-', 'move-', 'ant-input-affix-wrapper-focused'
]


def clean_css_selector(css: str) -> str:
    """@Function: 清理CSS选择器，移除动态类名 / Clean CSS selector by removing dynamic classes"""
    if not css:
        return css
    for pattern in DYNAMIC_CLASS_PATTERNS:
        css = re.sub(r'\.' + re.escape(pattern) + r'[a-zA-Z0-9_-]*', '', css)
    css = re.sub(r'\s+', ' ', css).strip()
    css = re.sub(r'\s*>\s*', ' > ', css)
    return css


def _simplify_css_selector(css: str) -> str:
    """@Function: Simplify complex CSS selector, extract most stable parts"""
    if not css:
        return css

    css = clean_css_selector(css)

    # Try to extract input element selector
    input_match = re.search(r'(input\[.*?\]|input\.[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*)', css)
    if input_match:
        input_selector = input_match.group(0)

        # Try to extract more stable selector from parent
        placeholder_match = re.search(r"placeholder\s*=\s*['\"]([^'\"]+)['\"]", css)
        if placeholder_match:
            return f'input[placeholder="{placeholder_match.group(1)}"]'

        name_match = re.search(r"name\s*=\s*['\"]([^'\"]+)['\"]", css)
        if name_match:
            return f'input[name="{name_match.group(1)}"]'

        type_match = re.search(r"type\s*=\s*['\"]([^'\"]+)['\"]", css)
        if type_match:
            return f'input[type="{type_match.group(1)}"]'

        # Look for stable class names in parent (e.g. ant-input-password)
        password_match = re.search(r'(ant-input-password|has-border)', css)
        if password_match:
            return f'span.{password_match.group(1)} input'

        # If input selector is simple enough, return it directly
        if len(input_selector) < 50:
            return input_selector

    # For button elements
    button_match = re.search(r'(button\[.*?\]|button\.[a-zA-Z0-9_-]+)', css)
    if button_match:
        button_selector = button_match.group(0)
        text_match = re.search(r":has-text\(['\"]([^'\"]+)['\"]\)", css)
        if text_match:
            return f'button:has-text("{text_match.group(1)}")'
        if len(button_selector) < 50:
            return button_selector

    # If cannot simplify, truncate overly long paths - keep only last 3 levels
    parts = css.split(' > ')
    if len(parts) > 3:
        return ' > '.join(parts[-3:])

    return css


class DebugRunRequest(BaseModel):
    """调试运行请求"""
    case_id: int
    browser_type: str = "chromium"
    headless: bool = False
    timeout: int = 30
    variables: Dict[str, str] = {}


class DebugStepResult(BaseModel):
    """单步执行结果"""
    step_index: int
    keyword: str
    success: bool
    message: str
    duration: float = 0
    screenshot: str = ""


class ManualCaptchaInput(BaseModel):
    """人工验证码输入请求"""
    captcha_text: str


# 存储调试运行状态和执行引擎实例
_debug_tasks: Dict[int, Dict[str, Any]] = {}
_debug_engines: Dict[int, ExecutionEngine] = {}


@router.post("/run", summary="调试运行用例")
async def debug_run(request: DebugRunRequest, db: Session = Depends(get_db)):
    """@Function: 调试运行单个用例，返回实时执行结果"""
    service = CaseService(db)
    case = service.get_case_by_id(request.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")

    # 解析步骤
    try:
        steps = json.loads(case.get("steps", "[]"))
    except json.JSONDecodeError:
        steps = []

    if not steps:
        return {"code": 1, "message": "用例没有测试步骤"}

    # 创建调试任务
    task_id = request.case_id
    _debug_tasks[task_id] = {
        "status": "running",
        "current_step": 0,
        "total_steps": len(steps),
        "results": [],
        "error": None,
        "waiting_captcha": False,
        "captcha_screenshot": None,
    }

    # 在后台线程执行
    def run_debug():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_execute_debug_steps(task_id, steps, request))
        except Exception as e:
            logger.error(f"调试运行异常: {e}")
            _debug_tasks[task_id]["status"] = "failed"
            _debug_tasks[task_id]["error"] = str(e)
        finally:
            loop.close()

    thread = threading.Thread(target=run_debug, daemon=True)
    thread.start()

    return {"code": 0, "data": {"task_id": task_id}, "message": "调试运行已启动"}


@router.get("/status/{task_id}", summary="获取调试运行状态")
async def get_debug_status(task_id: int):
    """@Function: 获取调试运行的实时状态"""
    if task_id not in _debug_tasks:
        raise HTTPException(status_code=404, detail="调试任务不存在")

    task = _debug_tasks[task_id]
    return {
        "code": 0,
        "data": {
            "task_id": task_id,
            "status": task["status"],
            "current_step": task["current_step"],
            "total_steps": task["total_steps"],
            "results": task["results"],
            "error": task.get("error"),
            "waiting_captcha": task.get("waiting_captcha", False),
            "captcha_screenshot": task.get("captcha_screenshot"),
        }
    }


@router.post("/stop/{task_id}", summary="停止调试运行")
async def stop_debug(task_id: int):
    """@Function: 停止调试运行"""
    if task_id in _debug_tasks:
        _debug_tasks[task_id]["status"] = "stopped"

    # 如果有执行引擎实例，也停止它
    if task_id in _debug_engines:
        engine = _debug_engines[task_id]
        try:
            # 如果引擎正在等待人工输入，提交空字符串以解除阻塞
            if engine.is_paused and engine.pending_manual_input:
                engine.submit_manual_input("")
            asyncio.run_coroutine_threadsafe(engine.stop(), asyncio.get_event_loop())
        except Exception as e:
            logger.warning(f"停止执行引擎失败: {e}")

    return {"code": 0, "message": "调试运行已停止"}


@router.post("/captcha/{task_id}", summary="提交人工验证码")
async def submit_captcha(task_id: int, request: ManualCaptchaInput):
    """@Function: 提交人工输入的验证码"""
    if task_id not in _debug_engines:
        raise HTTPException(status_code=404, detail="调试任务不存在或已结束")

    engine = _debug_engines[task_id]
    if not engine.is_paused or not engine.pending_manual_input:
        raise HTTPException(status_code=400, detail="当前不在等待验证码输入状态")

    success = engine.submit_manual_input(request.captcha_text)
    if not success:
        raise HTTPException(status_code=500, detail="提交验证码失败")

    # 更新任务状态
    if task_id in _debug_tasks:
        _debug_tasks[task_id]["waiting_captcha"] = False
        _debug_tasks[task_id]["captcha_screenshot"] = None

    return {"code": 0, "message": "验证码已提交"}


@router.get("/captcha/sse/{task_id}", summary="验证码等待 SSE 推送")
async def captcha_sse(task_id: int):
    """@Function: SSE 推送验证码等待事件（用于前端实时显示验证码图片）"""

    async def event_generator():
        # 等待任务进入等待验证码状态
        max_wait = 120  # 最多等待 120 秒
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if task_id not in _debug_tasks:
                yield f"event: error\ndata: {json.dumps({'message': '任务不存在'})}\n\n"
                return

            task = _debug_tasks[task_id]
            if task.get("waiting_captcha") and task.get("captcha_screenshot"):
                yield f"event: captcha\ndata: {json.dumps({'screenshot': task['captcha_screenshot']})}\n\n"
                return

            if task["status"] in ("completed", "failed", "stopped"):
                yield f"event: done\ndata: {json.dumps({'status': task['status']})}\n\n"
                return

            await asyncio.sleep(0.5)

        yield f"event: timeout\ndata: {json.dumps({'message': '等待超时'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _notify_captcha_needed(task_id: int, screenshot_base64: str, **kwargs):
    """@Function: 通知前端需要人工输入验证码"""
    if task_id in _debug_tasks:
        _debug_tasks[task_id]["waiting_captcha"] = True
        _debug_tasks[task_id]["captcha_screenshot"] = screenshot_base64


async def _execute_debug_steps(task_id: int, steps: List[Dict[str, Any]], request: DebugRunRequest):
    """@Function: 执行调试步骤"""
    from app.driver.web_driver import WebDriver
    from plugins.keywords.web_keywords import execute_keyword

    driver = None
    engine = None
    try:
        # 初始化浏览器
        driver = WebDriver(
            browser_type=request.browser_type,
            headless=request.headless,
            timeout=request.timeout * 1000
        )
        await driver.launch()

        # 创建执行引擎（用于暂停/恢复支持）
        engine = ExecutionEngine(
            browser_type=request.browser_type,
            headless=request.headless,
            timeout=request.timeout * 1000,
        )
        engine._driver = driver  # 复用已启动的 driver
        engine.set_manual_input_callback(
            lambda **kw: _notify_captcha_needed(task_id, **kw)
        )
        _debug_engines[task_id] = engine

        # 逐步执行
        for i, step in enumerate(steps):
            if _debug_tasks.get(task_id, {}).get("status") == "stopped":
                break

            _debug_tasks[task_id]["current_step"] = i + 1

            keyword = step.get("keyword", "")
            params = step.get("params", {})

            # 清理 CSS 选择器中的动态类名 / Clean dynamic classes from CSS selectors
            if "element" in params and params["element"]:
                params = params.copy()
                params["element"] = _simplify_css_selector(params["element"])

            # 为 solve_captcha 注入 engine 和 task_id（支持人工介入）
            if keyword == "solve_captcha":
                params = params.copy()
                params["engine"] = engine
                params["task_id"] = task_id

            start_time = time.time()
            try:
                result = await execute_keyword(driver, keyword, params, request.timeout * 1000)
                duration = time.time() - start_time
                success = result.get("success", False)
                message = result.get("message", "")
                _debug_tasks[task_id]["results"].append({
                    "step_index": i,
                    "keyword": keyword,
                    "success": success,
                    "message": message,
                    "duration": round(duration, 2)
                })
                # 步骤失败，停止执行
                if not success:
                    _debug_tasks[task_id]["status"] = "failed"
                    _debug_tasks[task_id]["error"] = f"步骤 {i+1} 执行失败: {message}"
                    break
            except Exception as e:
                duration = time.time() - start_time
                _debug_tasks[task_id]["results"].append({
                    "step_index": i,
                    "keyword": keyword,
                    "success": False,
                    "message": str(e),
                    "duration": round(duration, 2)
                })
                # 步骤失败，停止执行
                _debug_tasks[task_id]["status"] = "failed"
                _debug_tasks[task_id]["error"] = f"步骤 {i+1} 执行失败: {str(e)}"
                break

        if _debug_tasks[task_id]["status"] == "running":
            _debug_tasks[task_id]["status"] = "completed"

    except Exception as e:
        logger.error(f"调试运行引擎错误: {e}")
        _debug_tasks[task_id]["status"] = "failed"
        _debug_tasks[task_id]["error"] = str(e)
    finally:
        # 清理引擎引用
        if task_id in _debug_engines:
            del _debug_engines[task_id]
        if driver:
            await driver.close()
            logger.info("浏览器已关闭")
