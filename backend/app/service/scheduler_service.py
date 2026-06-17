# -*- coding: utf-8 -*-
"""
任务调度服务 / Task scheduler service
@Function: 提供定时任务、用例集管理功能 / Provide scheduled tasks and test suite management
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.test_suite import TestSuite
from app.models.scheduler_task import SchedulerTask
from app.utils.logger import get_logger

logger = get_logger("scheduler")


class SchedulerService:
    """任务调度服务类"""

    def __init__(self, db: Session):
        self.db = db

    # 用例集管理
    def get_suite_list(self) -> List[Dict[str, Any]]:
        """@Function: 获取用例集列表

        Returns:
            用例集列表
        """
        suites = self.db.query(TestSuite).order_by(TestSuite.update_time.desc()).all()
        return [suite.to_dict() for suite in suites]

    def get_suite_by_id(self, suite_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 获取用例集详情

        Args:
            suite_id: 用例集ID

        Returns:
            用例集详情
        """
        suite = self.db.query(TestSuite).filter(TestSuite.id == suite_id).first()
        return suite.to_dict() if suite else None

    def create_suite(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建用例集

        Args:
            data: 用例集数据

        Returns:
            创建的用例集
        """
        if isinstance(data.get("case_ids"), list):
            data["case_ids"] = json.dumps(data["case_ids"])

        suite = TestSuite(**data)
        self.db.add(suite)
        self.db.commit()
        self.db.refresh(suite)

        logger.info(f"创建用例集: {suite.suite_name}")
        return suite.to_dict()

    def update_suite(self, suite_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新用例集

        Args:
            suite_id: 用例集ID
            data: 更新数据

        Returns:
            更新后的用例集
        """
        suite = self.db.query(TestSuite).filter(TestSuite.id == suite_id).first()
        if not suite:
            return None

        if isinstance(data.get("case_ids"), list):
            data["case_ids"] = json.dumps(data["case_ids"])

        for key, value in data.items():
            if hasattr(suite, key):
                setattr(suite, key, value)

        suite.update_time = datetime.now()
        self.db.commit()
        self.db.refresh(suite)

        logger.info(f"更新用例集: {suite.suite_name}")
        return suite.to_dict()

    def delete_suite(self, suite_id: int) -> bool:
        """@Function: 删除用例集

        Args:
            suite_id: 用例集ID

        Returns:
            是否删除成功
        """
        suite = self.db.query(TestSuite).filter(TestSuite.id == suite_id).first()
        if not suite:
            return False

        self.db.delete(suite)
        self.db.commit()

        logger.info(f"删除用例集: {suite.suite_name}")
        return True

    # 定时任务管理
    def get_scheduler_task_list(self) -> List[Dict[str, Any]]:
        """@Function: 获取定时任务列表

        Returns:
            定时任务列表
        """
        tasks = self.db.query(SchedulerTask).order_by(SchedulerTask.update_time.desc()).all()
        return [task.to_dict() for task in tasks]

    def get_scheduler_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 获取定时任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务详情
        """
        task = self.db.query(SchedulerTask).filter(SchedulerTask.id == task_id).first()
        return task.to_dict() if task else None

    def create_scheduler_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建定时任务

        Args:
            data: 任务数据

        Returns:
            创建的任务
        """
        if isinstance(data.get("notify_config"), dict):
            data["notify_config"] = json.dumps(data["notify_config"])

        task = SchedulerTask(**data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        logger.info(f"创建定时任务: {task.task_name}")
        return task.to_dict()

    def update_scheduler_task(self, task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新定时任务

        Args:
            task_id: 任务ID
            data: 更新数据

        Returns:
            更新后的任务
        """
        task = self.db.query(SchedulerTask).filter(SchedulerTask.id == task_id).first()
        if not task:
            return None

        if isinstance(data.get("notify_config"), dict):
            data["notify_config"] = json.dumps(data["notify_config"])

        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.update_time = datetime.now()
        self.db.commit()
        self.db.refresh(task)

        logger.info(f"更新定时任务: {task.task_name}")
        return task.to_dict()

    def delete_scheduler_task(self, task_id: int) -> bool:
        """@Function: 删除定时任务

        Args:
            task_id: 任务ID

        Returns:
            是否删除成功
        """
        task = self.db.query(SchedulerTask).filter(SchedulerTask.id == task_id).first()
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()

        logger.info(f"删除定时任务: {task.task_name}")
        return True

    def toggle_scheduler_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 切换定时任务状态

        Args:
            task_id: 任务ID

        Returns:
            更新后的任务
        """
        task = self.db.query(SchedulerTask).filter(SchedulerTask.id == task_id).first()
        if not task:
            return None

        task.status = 1 if task.status == 0 else 0
        task.update_time = datetime.now()
        self.db.commit()
        self.db.refresh(task)

        logger.info(f"切换定时任务状态: {task.task_name} -> {'启用' if task.status else '禁用'}")
        return task.to_dict()
