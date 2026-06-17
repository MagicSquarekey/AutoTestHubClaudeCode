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
                "cases": [{"id": c.id, "name": c.case_name, "steps": json.loads(c.steps) if c.steps else []} for c in cases],
                "current_case_index": 0,
                "current_step_index": 0,
                "results": [],
                "logs": [],
                "screenshots": [],
                "start_time": None,
                "end_time": None,
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

        return self.create_task({
            "case_ids": case_ids,
            "platform": platform,
            "device_id": device_id,
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
            params = task["params"]
            engine = ExecutionEngine(
                platform=params.get("platform", "web"),
                browser_type=params.get("browser_type", "chromium"),
                headless=params.get("headless", settings.HEADLESS),
                timeout=params.get("timeout", settings.BROWSER_TIMEOUT),
            )

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
            # 确保引擎关闭
            if engine:
                try:
                    if sys.platform == "win32":
                        cleanup_loop = asyncio.ProactorEventLoop()
                    else:
                        cleanup_loop = asyncio.new_event_loop()
                    cleanup_loop.run_until_complete(engine.stop())
                    cleanup_loop.close()
                except Exception:
                    pass

            # 关闭独立数据库会话
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

        logger.info(f"开始执行用例: {case_name}")

        step_results = []
        status = "passed"

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
