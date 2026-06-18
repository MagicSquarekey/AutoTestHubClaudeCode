# -*- coding: utf-8 -*-
"""
录制引擎管理器 / Recording engine manager
@Function: 管理录制引擎实例的生命周期 / Manage recording engine instance lifecycle
"""

import asyncio
import threading
from typing import Optional, Dict, Any, List
from app.engine.recording_engine import RecordingEngine
from app.service.record_service import RecordService
from app.models.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger("recording_manager")


class RecordingManager:
    """录制引擎管理器类 / Recording engine manager class"""

    def __init__(self):
        """@Function: 初始化管理器 / Initialize manager"""
        self._engines: Dict[int, RecordingEngine] = {}
        self._threads: Dict[int, threading.Thread] = {}
        self._loops: Dict[int, asyncio.AbstractEventLoop] = {}
        self._new_actions: Dict[int, List[Dict[str, Any]]] = {}
        # 标记正在启动中的任务，解决竞态条件 / Mark tasks being started to fix race condition
        self._starting_tasks: set = set()

    def start_recording(self, task_id: int, target_url: str, browser_type: str = "chromium") -> bool:
        """@Function: 启动录制 / Start recording

        Args:
            task_id: 任务 ID
            target_url: 目标 URL
            browser_type: 浏览器类型

        Returns:
            是否启动成功
        """
        if task_id in self._engines or task_id in self._starting_tasks:
            logger.warning(f"任务 {task_id} 已在录制中或正在启动")
            return False

        # 初始化新操作列表
        self._new_actions[task_id] = []
        # 标记为正在启动 / Mark as starting
        self._starting_tasks.add(task_id)

        logger.info(f"正在启动录制任务 {task_id}，目标URL: {target_url}，浏览器: {browser_type}")

        # 在新线程中启动录制引擎
        thread = threading.Thread(
            target=self._run_recording_thread,
            args=(task_id, target_url, browser_type),
            daemon=True,
        )
        self._threads[task_id] = thread
        thread.start()

        logger.info(f"录制任务 {task_id} 线程已启动")
        return True

    def _run_recording_thread(self, task_id: int, target_url: str, browser_type: str):
        """@Function: 在线程中运行录制引擎 / Run recording engine in thread"""
        logger.info(f"录制任务 {task_id} 线程开始运行")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loops[task_id] = loop

        try:
            loop.run_until_complete(self._recording_task(task_id, target_url, browser_type))
        except Exception as e:
            logger.error(f"录制任务 {task_id} 线程异常: {e}")
            # 清除启动标记 / Clear starting flag on unexpected error
            self._starting_tasks.discard(task_id)
        finally:
            loop.close()
            if task_id in self._loops:
                del self._loops[task_id]
            # 确保清除启动标记 / Ensure starting flag is cleared
            self._starting_tasks.discard(task_id)
            logger.info(f"录制任务 {task_id} 线程已结束")

    async def _recording_task(self, task_id: int, target_url: str, browser_type: str):
        """@Function: 录制任务协程 / Recording task coroutine"""
        logger.info(f"录制任务 {task_id} 协程开始，准备启动浏览器")
        engine = RecordingEngine(browser_type=browser_type, headless=False)

        try:
            # 启动浏览器
            logger.info(f"录制任务 {task_id} 正在启动浏览器...")
            await engine.launch()
            logger.info(f"录制任务 {task_id} 浏览器启动成功")

            # 浏览器启动成功后，将引擎加入字典并清除启动标记
            # Add engine to dict and clear starting flag after browser launched
            self._engines[task_id] = engine
            self._starting_tasks.discard(task_id)

            # 设置操作回调
            async def on_action(action):
                """处理新录制的操作"""
                logger.info(f"录制任务 {task_id} 收到新操作: {action.get('action_type')}")
                # 保存到数据库
                db = SessionLocal()
                try:
                    service = RecordService(db)
                    service.create_step({
                        "task_id": task_id,
                        "action_type": action.get("action_type", ""),
                        "element_locators": action.get("element_locators", {}),
                        "element_name": action.get("element_name", ""),
                        "input_value": action.get("input_value", ""),
                        "screenshot": action.get("screenshot", ""),
                        "page_url": action.get("page_url", ""),
                    })
                    # 添加到新操作列表
                    self._new_actions[task_id].append(action)
                    logger.info(f"录制步骤已保存到数据库: {action.get('action_type')}")
                except Exception as e:
                    logger.error(f"保存录制步骤失败: {e}")
                finally:
                    db.close()

            engine.set_on_action_callback(on_action)

            # 开始录制
            logger.info(f"录制任务 {task_id} 开始录制，目标URL: {target_url}")
            await engine.start_recording(target_url)
            logger.info(f"录制任务 {task_id} 录制已启动")

            # 保持浏览器打开，直到录制停止
            while engine.is_recording and engine.is_alive:
                await asyncio.sleep(1)

            # 录制结束后更新任务状态（无论哪种原因结束）
            # Update task status after recording ends (regardless of reason)
            browser_alive = engine.is_alive
            engine._is_recording = False

            db = SessionLocal()
            try:
                service = RecordService(db)
                if not browser_alive:
                    logger.info(f"浏览器已关闭，停止录制任务 {task_id}")
                    service.update_task_status(task_id, "completed")
                    logger.info(f"任务 {task_id} 状态已更新为 completed")
                else:
                    # 正常停止（由 stop_recording 触发）
                    service.update_task_status(task_id, "completed")
                    logger.info(f"任务 {task_id} 状态已更新为 completed")
            except Exception as e:
                logger.error(f"更新任务状态失败: {e}")
            finally:
                db.close()

        except Exception as e:
            logger.error(f"录制引擎错误: {e}")
            # 清除启动标记 / Clear starting flag
            self._starting_tasks.discard(task_id)
            # 发生错误时更新任务状态
            db = SessionLocal()
            try:
                service = RecordService(db)
                service.update_task_status(task_id, "failed")
            except Exception as ex:
                logger.error(f"更新任务状态失败: {ex}")
            finally:
                db.close()
        finally:
            # 确保浏览器关闭
            await engine.close()
            if task_id in self._engines:
                del self._engines[task_id]
            # 确保清除启动标记 / Ensure starting flag is cleared
            self._starting_tasks.discard(task_id)

    def stop_recording(self, task_id: int) -> List[Dict[str, Any]]:
        """@Function: 停止录制 / Stop recording

        Args:
            task_id: 任务 ID

        Returns:
            录制的操作列表
        """
        # 如果任务正在启动中但引擎还未就绪，直接清除启动标记
        # If task is starting but engine not ready, clear starting flag
        if task_id in self._starting_tasks:
            self._starting_tasks.discard(task_id)
            logger.info(f"录制任务 {task_id} 尚未启动完成，已取消启动")
            return []

        if task_id not in self._engines:
            logger.warning(f"任务 {task_id} 未在录制中")
            return []

        engine = self._engines[task_id]

        # 在事件循环中停止录制
        if task_id in self._loops:
            loop = self._loops[task_id]
            asyncio.run_coroutine_threadsafe(engine.stop_recording(), loop)

        # 等待线程结束
        if task_id in self._threads:
            thread = self._threads[task_id]
            thread.join(timeout=5)
            del self._threads[task_id]

        # 获取新录制的操作
        new_actions = self._new_actions.get(task_id, [])

        # 清理
        if task_id in self._new_actions:
            del self._new_actions[task_id]

        logger.info(f"录制任务 {task_id} 已停止，共 {len(new_actions)} 个操作")
        return new_actions

    def is_recording(self, task_id: int) -> bool:
        """@Function: 检查是否正在录制 / Check if recording

        Args:
            task_id: 任务 ID

        Returns:
            是否正在录制
        """
        # 正在启动中也视为录制中 / Starting tasks are also considered recording
        if task_id in self._starting_tasks:
            return True
        return task_id in self._engines and self._engines[task_id].is_recording

    def get_new_actions(self, task_id: int) -> List[Dict[str, Any]]:
        """@Function: 获取新录制的操作 / Get new recorded actions

        Args:
            task_id: 任务 ID

        Returns:
            新操作列表
        """
        actions = self._new_actions.get(task_id, [])
        self._new_actions[task_id] = []  # 清空已读取的操作
        return actions

    def cleanup(self):
        """@Function: 清理所有录制引擎 / Cleanup all recording engines"""
        for task_id in list(self._engines.keys()):
            try:
                self.stop_recording(task_id)
            except Exception as e:
                logger.error(f"清理录制引擎 {task_id} 失败: {e}")


# 全局录制管理器实例
recording_manager = RecordingManager()
