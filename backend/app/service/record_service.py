# -*- coding: utf-8 -*-
"""
录制管理服务 / Record management service
@Function: 提供录制任务和步骤的业务逻辑处理 / Provide business logic for record tasks and steps
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.record_task import RecordTask
from app.models.record_step import RecordStep
from app.utils.logger import get_logger

logger = get_logger("record_service")


class RecordService:
    """录制管理服务类 / Record management service class"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 录制任务相关 / Record Task Related ====================

    def get_task_list(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """@Function: 获取录制任务列表 / Get record task list with filters and pagination

        Args:
            status: 状态筛选 / Status filter
            keyword: 关键词搜索 / Keyword search
            page: 页码 / Page number
            page_size: 每页数量 / Page size

        Returns:
            包含列表和分页信息的字典 / Dict with list and pagination info
        """
        query = self.db.query(RecordTask)

        # 应用筛选条件 / Apply filters
        if status:
            query = query.filter(RecordTask.status == status)
        if keyword:
            query = query.filter(
                or_(
                    RecordTask.task_name.contains(keyword),
                    RecordTask.description.contains(keyword),
                    RecordTask.target_url.contains(keyword),
                )
            )

        # 计算总数 / Count total
        total = query.count()

        # 分页查询 / Paginate query
        tasks = query.order_by(RecordTask.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "list": [task.to_dict() for task in tasks],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 根据 ID 获取录制任务 / Get record task by ID

        Args:
            task_id: 任务 ID / Task ID

        Returns:
            任务字典或 None / Task dict or None
        """
        task = self.db.query(RecordTask).filter(RecordTask.id == task_id).first()
        return task.to_dict() if task else None

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建录制任务 / Create record task

        Args:
            data: 任务数据 / Task data

        Returns:
            创建的任务字典 / Created task dict
        """
        task = RecordTask(
            task_name=data.get("task_name", "未命名录制任务"),
            target_url=data.get("target_url", ""),
            browser_type=data.get("browser_type", "chromium"),
            description=data.get("description", ""),
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"创建录制任务: {task.task_name} (ID: {task.id})")
        return task.to_dict()

    def update_task(self, task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新录制任务 / Update record task

        Args:
            task_id: 任务 ID / Task ID
            data: 更新数据 / Update data

        Returns:
            更新后的任务字典或 None / Updated task dict or None
        """
        task = self.db.query(RecordTask).filter(RecordTask.id == task_id).first()
        if not task:
            return None

        # 更新字段 / Update fields
        for key, value in data.items():
            if hasattr(task, key) and key not in ["id", "create_time"]:
                setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)
        logger.info(f"更新录制任务: {task.task_name} (ID: {task.id})")
        return task.to_dict()

    def delete_task(self, task_id: int) -> bool:
        """@Function: 删除录制任务 / Delete record task

        Args:
            task_id: 任务 ID / Task ID

        Returns:
            是否删除成功 / Whether deletion succeeded
        """
        task = self.db.query(RecordTask).filter(RecordTask.id == task_id).first()
        if not task:
            return False

        # 先删除关联的步骤 / Delete associated steps first
        self.db.query(RecordStep).filter(RecordStep.task_id == task_id).delete()

        # 删除任务 / Delete task
        self.db.delete(task)
        self.db.commit()
        logger.info(f"删除录制任务: {task.task_name} (ID: {task.id})")
        return True

    def update_task_status(self, task_id: int, status: str) -> Optional[Dict[str, Any]]:
        """@Function: 更新任务状态 / Update task status

        Args:
            task_id: 任务 ID / Task ID
            status: 新状态 / New status

        Returns:
            更新后的任务字典或 None / Updated task dict or None
        """
        task = self.db.query(RecordTask).filter(RecordTask.id == task_id).first()
        if not task:
            return None

        task.status = status
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"更新录制任务状态: {task.task_name} -> {status}")
        return task.to_dict()

    # ==================== 录制步骤相关 / Record Step Related ====================

    def get_steps_by_task_id(self, task_id: int) -> List[Dict[str, Any]]:
        """@Function: 获取任务的所有步骤 / Get all steps of a task

        Args:
            task_id: 任务 ID / Task ID

        Returns:
            步骤字典列表 / List of step dicts
        """
        steps = self.db.query(RecordStep).filter(RecordStep.task_id == task_id).order_by(RecordStep.step_order).all()
        return [step.to_dict() for step in steps]

    def get_step_by_id(self, step_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 根据 ID 获取步骤 / Get step by ID

        Args:
            step_id: 步骤 ID / Step ID

        Returns:
            步骤字典或 None / Step dict or None
        """
        step = self.db.query(RecordStep).filter(RecordStep.id == step_id).first()
        return step.to_dict() if step else None

    def create_step(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建录制步骤 / Create record step

        Args:
            data: 步骤数据 / Step data

        Returns:
            创建的步骤字典 / Created step dict
        """
        # 获取当前任务的最大步骤顺序 / Get max step order for the task
        max_order = self.db.query(RecordStep).filter(
            RecordStep.task_id == data.get("task_id")
        ).count()

        step = RecordStep(
            task_id=data.get("task_id"),
            step_order=data.get("step_order", max_order + 1),
            action_type=data.get("action_type"),
            element_locators=json.dumps(data.get("element_locators", {}), ensure_ascii=False),
            element_name=data.get("element_name", ""),
            input_value=data.get("input_value", ""),
            screenshot=data.get("screenshot", ""),
            page_url=data.get("page_url", ""),
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)

        # 更新任务的步骤数量 / Update task step count
        self._update_task_step_count(step.task_id)

        logger.info(f"创建录制步骤: 任务ID={step.task_id}, 顺序={step.step_order}, 类型={step.action_type}")
        return step.to_dict()

    def update_step(self, step_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新录制步骤 / Update record step

        Args:
            step_id: 步骤 ID / Step ID
            data: 更新数据 / Update data

        Returns:
            更新后的步骤字典或 None / Updated step dict or None
        """
        step = self.db.query(RecordStep).filter(RecordStep.id == step_id).first()
        if not step:
            return None

        # 更新字段 / Update fields
        for key, value in data.items():
            if hasattr(step, key) and key not in ["id", "task_id", "create_time"]:
                # 特殊处理 element_locators / Special handling for element_locators
                if key == "element_locators" and isinstance(value, dict):
                    setattr(step, key, json.dumps(value, ensure_ascii=False))
                else:
                    setattr(step, key, value)

        step.status = "edited"
        self.db.commit()
        self.db.refresh(step)
        logger.info(f"更新录制步骤: ID={step.id}")
        return step.to_dict()

    def delete_step(self, step_id: int) -> bool:
        """@Function: 删除录制步骤 / Delete record step

        Args:
            step_id: 步骤 ID / Step ID

        Returns:
            是否删除成功 / Whether deletion succeeded
        """
        step = self.db.query(RecordStep).filter(RecordStep.id == step_id).first()
        if not step:
            return False

        task_id = step.task_id
        self.db.delete(step)
        self.db.commit()

        # 重新排序步骤 / Reorder steps
        self._reorder_steps(task_id)
        # 更新任务的步骤数量 / Update task step count
        self._update_task_step_count(task_id)

        logger.info(f"删除录制步骤: ID={step_id}")
        return True

    def move_step(self, step_id: int, direction: str) -> Optional[List[Dict[str, Any]]]:
        """@Function: 移动步骤顺序 / Move step order

        Args:
            step_id: 步骤 ID / Step ID
            direction: 移动方向：up/down / Move direction

        Returns:
            更新后的步骤列表或 None / Updated step list or None
        """
        step = self.db.query(RecordStep).filter(RecordStep.id == step_id).first()
        if not step:
            return None

        # 获取任务的所有步骤 / Get all steps of the task
        steps = self.db.query(RecordStep).filter(
            RecordStep.task_id == step.task_id
        ).order_by(RecordStep.step_order).all()

        # 找到当前步骤的索引 / Find current step index
        current_index = next((i for i, s in enumerate(steps) if s.id == step_id), None)
        if current_index is None:
            return None

        # 计算目标索引 / Calculate target index
        if direction == "up" and current_index > 0:
            target_index = current_index - 1
        elif direction == "down" and current_index < len(steps) - 1:
            target_index = current_index + 1
        else:
            return None

        # 交换顺序 / Swap order
        steps[current_index].step_order, steps[target_index].step_order = (
            steps[target_index].step_order,
            steps[current_index].step_order,
        )
        self.db.commit()

        logger.info(f"移动录制步骤: ID={step_id}, 方向={direction}")
        return self.get_steps_by_task_id(step.task_id)

    def _reorder_steps(self, task_id: int) -> None:
        """@Function: 重新排序步骤 / Reorder steps

        Args:
            task_id: 任务 ID / Task ID
        """
        steps = self.db.query(RecordStep).filter(
            RecordStep.task_id == task_id
        ).order_by(RecordStep.step_order).all()

        for i, step in enumerate(steps, 1):
            step.step_order = i

        self.db.commit()

    def _update_task_step_count(self, task_id: int) -> None:
        """@Function: 更新任务的步骤数量 / Update task step count

        Args:
            task_id: 任务 ID / Task ID
        """
        task = self.db.query(RecordTask).filter(RecordTask.id == task_id).first()
        if task:
            count = self.db.query(RecordStep).filter(RecordStep.task_id == task_id).count()
            task.step_count = count
            self.db.commit()

    def batch_create_steps(self, task_id: int, steps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """@Function: 批量创建步骤 / Batch create steps

        Args:
            task_id: 任务 ID / Task ID
            steps_data: 步骤数据列表 / List of step data

        Returns:
            创建的步骤字典列表 / List of created step dicts
        """
        created_steps = []
        for i, data in enumerate(steps_data, 1):
            step = RecordStep(
                task_id=task_id,
                step_order=i,
                action_type=data.get("action_type"),
                element_locators=json.dumps(data.get("element_locators", {}), ensure_ascii=False),
                element_name=data.get("element_name", ""),
                input_value=data.get("input_value", ""),
                screenshot=data.get("screenshot", ""),
                page_url=data.get("page_url", ""),
            )
            self.db.add(step)
            created_steps.append(step)

        self.db.commit()

        # 刷新所有步骤 / Refresh all steps
        for step in created_steps:
            self.db.refresh(step)

        # 更新任务的步骤数量 / Update task step count
        self._update_task_step_count(task_id)

        logger.info(f"批量创建录制步骤: 任务ID={task_id}, 数量={len(created_steps)}")
        return [step.to_dict() for step in created_steps]
