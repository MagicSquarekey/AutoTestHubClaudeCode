# -*- coding: utf-8 -*-
"""
执行引擎服务 / Execution engine service
@Function: 提供用例执行的核心业务逻辑 / Provide core business logic for test execution
"""

import uuid
import json
import time
import asyncio
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from app.models.test_case import TestCase
from app.models.exec_record import ExecRecord
from app.models.test_suite import TestSuite
from app.engine.execution_engine import ExecutionEngine
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("exec")


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class ExecService:
    """执行引擎服务类"""

    # 任务状态存储（内存中）
    _tasks: Dict[str, Dict[str, Any]] = {}
    _task_lock = threading.Lock()

    def __init__(self, db: Session):
        self.db = db
        self._executor = ThreadPoolExecutor(max_workers=settings.MAX_PARALLEL_TASKS)

    def create_task(self, params: Dict[str, Any]) -> str:
        """@Function: 创建执行任务

        Args:
            params: 执行参数

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        # 获取用例信息
        case_ids = params.get("case_ids", [])
        cases = self.db.query(TestCase).filter(TestCase.id.in_(case_ids)).all()

        # 创建执行记录
        record = ExecRecord(
            task_id=task_id,
            task_name=f"执行任务-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            case_count=len(cases),
            platform=params.get("platform", "web"),
            status=TaskStatus.PENDING,
            device_info=json.dumps({
                "device_id": params.get("device_id"),
                "browser_type": params.get("browser_type", "chromium"),
            }),
        )
        self.db.add(record)
        self.db.commit()

        # 初始化任务状态
        with self._task_lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "status": TaskStatus.PENDING,
                "params": params,
                "cases": [
                    {
                        "id": c.id,
                        "name": c.case_name,
                        "steps": json.loads(c.steps) if c.steps else [],
                        "setup_steps": json.loads(c.setup_steps) if c.setup_steps else [],
                        "teardown_steps": json.loads(c.teardown_steps) if c.teardown_steps else [],
                    }
                    for c in cases
                ],
                "suite_setup_steps": params.get("suite_setup_steps", []),
                "suite_teardown_steps": params.get("suite_teardown_steps", []),
                "current_case_index": 0,
                "current_step_index": 0,
                "results": [],
                "logs": [],
                "screenshots": [],
                "start_time": None,
                "end_time": None,
                "engine": None,  # 执行引擎引用，用于检查验证码等待状态
            }

        # 异步执行任务
        self._executor.submit(self._execute_task, task_id)

        logger.info(f"创建执行任务: {task_id}")
        return task_id

    def run_suite(self, suite_id: int, platform: str = "web", device_id: Optional[str] = None) -> str:
        """@Function: 执行测试套件

        Args:
            suite_id: 套件ID
            platform: 平台类型
            device_id: 设备ID

        Returns:
            任务ID
        """
        suite = self.db.query(TestSuite).filter(TestSuite.id == suite_id).first()
        if not suite:
            raise ValueError("用例集不存在")

        case_ids = json.loads(suite.case_ids) if suite.case_ids else []
        suite_setup_steps = json.loads(suite.setup_steps) if suite.setup_steps else []
        suite_teardown_steps = json.loads(suite.teardown_steps) if suite.teardown_steps else []

        return self.create_task({
            "case_ids": case_ids,
            "platform": platform,
            "device_id": device_id,
            "suite_setup_steps": suite_setup_steps,
            "suite_teardown_steps": suite_teardown_steps,
        })

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """@Function: 获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        with self._task_lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

            # 检查是否正在等待验证码输入
            waiting_captcha = False
            captcha_screenshot = None
            engine = task.get("engine")
            if engine:
                has_pending = hasattr(engine, '_pending_manual_input')
                pending_value = engine._pending_manual_input if has_pending else None
                if has_pending and pending_value:
                    waiting_captcha = True
                    captcha_screenshot = pending_value.get("screenshot_base64")
                    logger.debug(f"检测到验证码等待状态: waiting_captcha={waiting_captcha}, has_screenshot={captcha_screenshot is not None}")

            return {
                "task_id": task["task_id"],
                "status": task["status"],
                "case_count": len(task["cases"]),
                "current_case_index": task["current_case_index"],
                "current_step_index": task["current_step_index"],
                "results": task["results"],
                "start_time": task["start_time"],
                "end_time": task["end_time"],
                "duration": (task["end_time"] - task["start_time"]) if task["start_time"] and task["end_time"] else None,
                "waiting_captcha": waiting_captcha,
                "captcha_screenshot": captcha_screenshot,
            }

    def control_task(self, task_id: str, action: str) -> bool:
        """@Function: 控制任务执行

        Args:
            task_id: 任务ID
            action: 控制动作（pause/resume/stop）

        Returns:
            是否成功
        """
        with self._task_lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            if action == "pause" and task["status"] == TaskStatus.RUNNING:
                task["status"] = TaskStatus.PAUSED
            elif action == "resume" and task["status"] == TaskStatus.PAUSED:
                task["status"] = TaskStatus.RUNNING
            elif action == "stop":
                task["status"] = TaskStatus.STOPPED
            else:
                return False

            logger.info(f"任务 {task_id} 执行 {action}")
            return True

    def submit_captcha(self, task_id: str, captcha_text: str) -> bool:
        """@Function: 提交人工验证码

        Args:
            task_id: 任务ID
            captcha_text: 验证码文本

        Returns:
            是否成功
        """
        with self._task_lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            engine = task.get("engine")
            if not engine:
                return False

            # 调用引擎的 submit_manual_input 方法
            return engine.submit_manual_input(captcha_text)

    def get_exec_log(self, task_id: str, case_id: Optional[int] = None, step_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """@Function: 获取执行日志

        Args:
            task_id: 任务ID
            case_id: 用例ID筛选
            step_id: 步骤ID筛选

        Returns:
            日志列表
        """
        with self._task_lock:
            task = self._tasks.get(task_id)
            if not task:
                return []

            logs = task["logs"]
            if case_id is not None:
                logs = [l for l in logs if l.get("case_id") == case_id]
            if step_id is not None:
                logs = [l for l in logs if l.get("step_id") == step_id]

            return logs

    def get_exec_screenshot(self, task_id: str, case_id: Optional[int] = None, step_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """@Function: 获取执行截图

        Args:
            task_id: 任务ID
            case_id: 用例ID筛选
            step_id: 步骤ID筛选

        Returns:
            截图列表
        """
        with self._task_lock:
            task = self._tasks.get(task_id)
            if not task:
                return []

            screenshots = task["screenshots"]
            if case_id is not None:
                screenshots = [s for s in screenshots if s.get("case_id") == case_id]
            if step_id is not None:
                screenshots = [s for s in screenshots if s.get("step_id") == step_id]

            return screenshots

    def get_task_list(self, status: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """@Function: 获取任务列表

        Args:
            status: 状态筛选
            page: 页码
            page_size: 每页数量

        Returns:
            任务列表
        """
        query = self.db.query(ExecRecord)

        if status:
            query = query.filter(ExecRecord.status == status)

        total = query.count()
        records = query.order_by(ExecRecord.exec_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "list": [record.to_dict() for record in records],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def debug_step(self, case_id: int, step_id: str, platform: str = "web", device_id: Optional[str] = None) -> Dict[str, Any]:
        """@Function: 单步调试执行

        Args:
            case_id: 用例ID
            step_id: 步骤ID
            platform: 平台类型
            device_id: 设备ID

        Returns:
            执行结果
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            raise ValueError("用例不存在")

        steps = json.loads(case.steps) if case.steps else []
        target_step = None

        for step in steps:
            if step.get("id") == step_id:
                target_step = step
                break

        if not target_step:
            raise ValueError("步骤不存在")

        # TODO: 实际执行步骤
        logger.info(f"单步调试: 用例 {case_id}, 步骤 {step_id}")

        return {
            "case_id": case_id,
            "step_id": step_id,
            "step": target_step,
            "status": "success",
            "duration": 0,
            "message": "执行成功",
        }

    def debug_with_breakpoint(self, case_id: int, breakpoint_step_id: str, platform: str = "web", device_id: Optional[str] = None) -> str:
        """@Function: 断点调试执行

        Args:
            case_id: 用例ID
            breakpoint_step_id: 断点步骤ID
            platform: 平台类型
            device_id: 设备ID

        Returns:
            任务ID
        """
        return self.create_task({
            "case_ids": [case_id],
            "platform": platform,
            "device_id": device_id,
            "breakpoint_step_id": breakpoint_step_id,
        })

    def _execute_task(self, task_id: str):
        """@Function: 执行任务（内部方法，在独立线程中运行）

        Args:
            task_id: 任务ID
        """
        import sys
        from app.models.database import SessionLocal

        with self._task_lock:
            task = self._tasks.get(task_id)
            if not task:
                return

            task["status"] = TaskStatus.RUNNING
            task["start_time"] = time.time()

        # 创建独立的数据库会话（不依赖 FastAPI 的请求会话）
        db = SessionLocal()
        record = None
        engine = None

        logger.info(f"任务 {task_id} 开始执行（新代码版本）")

        try:
            # 更新数据库状态
            record = db.query(ExecRecord).filter(ExecRecord.task_id == task_id).first()
            if record:
                try:
                    record.status = TaskStatus.RUNNING
                    db.commit()
                except Exception as e:
                    logger.warning(f"更新运行状态失败，继续执行: {e}")
                    db.rollback()

            # 创建执行引擎
            # 注意：前端传来的 timeout 是秒，ExecutionEngine 需要毫秒
            params = task["params"]
            engine_timeout = params.get("timeout", 30)
            if engine_timeout < 1000:
                engine_timeout = engine_timeout * 1000  # 秒转毫秒
            engine = ExecutionEngine(
                platform=params.get("platform", "web"),
                browser_type=params.get("browser_type", "chromium"),
                headless=params.get("headless", settings.HEADLESS),
                timeout=engine_timeout,
            )

            # 存储引擎引用到任务状态，用于检查验证码等待状态
            with self._task_lock:
                task["engine"] = engine

            # 在线程中创建新的事件循环运行异步引擎
            # Windows 需要 ProactorEventLoop 才支持子进程
            if sys.platform == "win32":
                loop = asyncio.ProactorEventLoop()
            else:
                loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._run_task_with_engine(task_id, task, engine, db))
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {e}")

            with self._task_lock:
                task["status"] = TaskStatus.FAILED
                task["end_time"] = time.time()

            if record:
                try:
                    db.rollback()  # 先回滚，再更新
                    record.status = TaskStatus.FAILED
                    record.error_message = str(e)[:500]
                    db.commit()
                except Exception as commit_err:
                    logger.error(f"更新失败状态也失败: {commit_err}")
                    db.rollback()

        finally:
            # 引擎已在 _run_task_with_engine 的 finally 块中关闭
            # 这里只需要确保数据库会话关闭
            try:
                db.close()
            except Exception:
                pass

    async def _run_task_with_engine(self, task_id: str, task: Dict[str, Any], engine: ExecutionEngine, db: Session):
        """@Function: 使用引擎执行任务（异步方法）

        Args:
            task_id: 任务ID
            task: 任务信息
            engine: 执行引擎
            db: 独立的数据库会话
        """
        try:
            # 启动引擎
            await engine.start()

            # 获取套件级别的 setup/teardown
            suite_setup_steps = task.get("suite_setup_steps", [])
            suite_teardown_steps = task.get("suite_teardown_steps", [])

            # 执行套件前置步骤
            if suite_setup_steps:
                logger.info(f"执行套件前置步骤: {len(suite_setup_steps)} 个")
                for step in suite_setup_steps:
                    # 检查任务状态
                    with self._task_lock:
                        if task["status"] == TaskStatus.STOPPED:
                            break
                    try:
                        await engine.execute_step(step)
                    except Exception as e:
                        logger.warning(f"套件前置步骤执行失败: {e}")
                        # 套件前置步骤失败，继续执行用例

            # 执行用例
            cases = task["cases"]
            results = []

            for i, case in enumerate(cases):
                # 检查任务状态
                with self._task_lock:
                    if task["status"] == TaskStatus.STOPPED:
                        break
                    while task["status"] == TaskStatus.PAUSED:
                        await asyncio.sleep(0.5)

                    task["current_case_index"] = i

                # 执行用例
                case_result = await self._execute_case_async(task_id, case, engine)
                results.append(case_result)

                with self._task_lock:
                    task["results"] = results

            # 执行套件后置步骤
            if suite_teardown_steps:
                logger.info(f"执行套件后置步骤: {len(suite_teardown_steps)} 个")
                for step in suite_teardown_steps:
                    # 检查任务状态
                    with self._task_lock:
                        if task["status"] == TaskStatus.STOPPED:
                            break
                    try:
                        await engine.execute_step(step)
                    except Exception as e:
                        logger.warning(f"套件后置步骤执行失败: {e}")
                        # 套件后置步骤失败不影响任务结果

            # 更新任务状态
            with self._task_lock:
                task["status"] = TaskStatus.COMPLETED
                task["end_time"] = time.time()

            # 更新数据库记录
            record = db.query(ExecRecord).filter(ExecRecord.task_id == task_id).first()
            if record:
                pass_count = sum(1 for r in results if r.get("status") == "passed")
                fail_count = sum(1 for r in results if r.get("status") == "failed")
                record.pass_count = pass_count
                record.fail_count = fail_count
                record.pass_rate = round(pass_count / len(results) * 100, 2) if results else 0
                record.exec_duration = int(task["end_time"] - task["start_time"])
                record.status = TaskStatus.COMPLETED
                db.commit()

            logger.info(f"任务 {task_id} 执行完成")

        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {e}")
            raise
        finally:
            # 在同一个事件循环中关闭引擎，确保浏览器正确关闭
            try:
                await engine.stop()
            except Exception as e:
                logger.debug(f"关闭引擎时出错（可忽略）: {e}")

    async def _execute_case_async(self, task_id: str, case: Dict[str, Any], engine: ExecutionEngine) -> Dict[str, Any]:
        """@Function: 执行单个用例（异步方法）

        Args:
            task_id: 任务ID
            case: 用例信息
            engine: 执行引擎

        Returns:
            用例执行结果
        """
        case_id = case["id"]
        case_name = case["name"]
        steps = case["steps"]
        setup_steps = case.get("setup_steps", [])
        teardown_steps = case.get("teardown_steps", [])

        logger.info(f"开始执行用例: {case_name}")

        step_results = []
        status = "passed"

        # 执行前置步骤
        if setup_steps:
            logger.info(f"执行用例前置步骤: {len(setup_steps)} 个")
            for j, step in enumerate(setup_steps):
                step_result = await self._execute_step_async(task_id, case_id, step, engine)
                step_results.append(step_result)
                if step_result["status"] == "failed":
                    logger.warning(f"前置步骤失败: {step.get('name', '')}")
                    # 前置步骤失败，用例标记为失败
                    status = "failed"
                    break

        # 执行主步骤（前置步骤成功时才执行）
        if status == "passed":
            for j, step in enumerate(steps):
                # 检查任务状态
                with self._task_lock:
                    task = self._tasks.get(task_id)
                    if task and task["status"] == TaskStatus.STOPPED:
                        break

                    task["current_step_index"] = j

                # 执行步骤
                step_result = await self._execute_step_async(task_id, case_id, step, engine)
                step_results.append(step_result)

                # 记录日志
                with self._task_lock:
                    task["logs"].append({
                        "case_id": case_id,
                        "step_id": step.get("id"),
                        "step_name": step.get("name"),
                        "status": step_result["status"],
                        "message": step_result.get("message", ""),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })

                if step_result["status"] == "failed":
                    status = "failed"

                    # 检查重试配置
                    retry_count = step.get("retry_count", 0)
                    for _ in range(retry_count):
                        step_result = await self._execute_step_async(task_id, case_id, step, engine)
                        if step_result["status"] == "passed":
                            status = "passed"
                            break

                    if step_result["status"] == "failed":
                        # 检查异常处理策略
                        on_error = step.get("on_error", "stop")
                        if on_error == "continue":
                            continue
                        elif on_error == "stop":
                            break

        # 执行后置步骤（无论用例成功或失败都执行）
        if teardown_steps:
            logger.info(f"执行用例后置步骤: {len(teardown_steps)} 个")
            for j, step in enumerate(teardown_steps):
                try:
                    step_result = await self._execute_step_async(task_id, case_id, step, engine)
                    step_results.append(step_result)
                except Exception as e:
                    logger.warning(f"后置步骤执行失败: {e}")
                    # 后置步骤失败不影响用例结果

        return {
            "case_id": case_id,
            "case_name": case_name,
            "status": status,
            "step_results": step_results,
        }

    async def _execute_step_async(self, task_id: str, case_id: int, step: Dict[str, Any], engine: ExecutionEngine) -> Dict[str, Any]:
        """@Function: 执行单个步骤（异步方法）

        Args:
            task_id: 任务ID
            case_id: 用例ID
            step: 步骤信息
            engine: 执行引擎

        Returns:
            步骤执行结果
        """
        step_id = step.get("id", "")
        keyword = step.get("keyword", "")
        params = step.get("params", {})

        logger.debug(f"执行步骤: {keyword}")

        start_time = time.time()

        try:
            result = await engine.execute_step(step)
            duration = round(time.time() - start_time, 2)

            return {
                "step_id": step_id,
                "keyword": keyword,
                "status": result.get("status", "failed"),
                "duration": duration,
                "message": result.get("message", ""),
            }
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            logger.error(f"步骤执行异常: {e}")
            return {
                "step_id": step_id,
                "keyword": keyword,
                "status": "failed",
                "duration": duration,
                "message": str(e),
            }
