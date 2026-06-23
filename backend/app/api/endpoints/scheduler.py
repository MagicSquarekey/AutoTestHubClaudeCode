# -*- coding: utf-8 -*-
"""
任务调度 API / Task scheduler API
@Function: 提供定时任务、用例集管理接口 / Provide scheduled task and test suite management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.scheduler_service import SchedulerService

router = APIRouter()


class SuiteCreate(BaseModel):
    """用例集创建请求"""
    suite_name: str
    description: str = ""
    case_ids: List[int] = []
    suite_type: str = "regression"
    platform: str = "web"
    setup_steps: str = "[]"
    teardown_steps: str = "[]"


class SuiteUpdate(BaseModel):
    """用例集更新请求"""
    suite_name: Optional[str] = None
    description: Optional[str] = None
    case_ids: Optional[List[int]] = None
    suite_type: Optional[str] = None
    platform: Optional[str] = None
    setup_steps: Optional[str] = None
    teardown_steps: Optional[str] = None


class TaskCreate(BaseModel):
    """定时任务创建请求"""
    task_name: str
    suite_id: int
    cron_expression: str
    platform: str = "web"
    device_id: str = ""
    notify_type: str = "none"
    notify_config: dict = {}


class TaskUpdate(BaseModel):
    """定时任务更新请求"""
    task_name: Optional[str] = None
    suite_id: Optional[int] = None
    cron_expression: Optional[str] = None
    platform: Optional[str] = None
    device_id: Optional[str] = None
    notify_type: Optional[str] = None
    notify_config: Optional[dict] = None
    status: Optional[int] = None


# 用例集接口
@router.get("/suites", summary="获取用例集列表")
async def get_suite_list(db: Session = Depends(get_db)):
    """@Function: 获取所有用例集"""
    service = SchedulerService(db)
    suites = service.get_suite_list()
    return {"code": 0, "data": suites}


@router.get("/suites/{suite_id}", summary="获取用例集详情")
async def get_suite(suite_id: int, db: Session = Depends(get_db)):
    """@Function: 获取用例集详情"""
    service = SchedulerService(db)
    suite = service.get_suite_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="用例集不存在")
    return {"code": 0, "data": suite}


@router.post("/suites", summary="创建用例集")
async def create_suite(suite: SuiteCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的用例集"""
    service = SchedulerService(db)
    result = service.create_suite(suite.dict())
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/suites/{suite_id}", summary="更新用例集")
async def update_suite(suite_id: int, suite: SuiteUpdate, db: Session = Depends(get_db)):
    """@Function: 更新用例集"""
    service = SchedulerService(db)
    result = service.update_suite(suite_id, suite.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="用例集不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/suites/{suite_id}", summary="删除用例集")
async def delete_suite(suite_id: int, db: Session = Depends(get_db)):
    """@Function: 删除用例集"""
    service = SchedulerService(db)
    success = service.delete_suite(suite_id)
    if not success:
        raise HTTPException(status_code=404, detail="用例集不存在")
    return {"code": 0, "message": "删除成功"}


# 定时任务接口
@router.get("/tasks", summary="获取定时任务列表")
async def get_scheduler_task_list(db: Session = Depends(get_db)):
    """@Function: 获取所有定时任务"""
    service = SchedulerService(db)
    tasks = service.get_scheduler_task_list()
    return {"code": 0, "data": tasks}


@router.get("/tasks/{task_id}", summary="获取定时任务详情")
async def get_scheduler_task(task_id: int, db: Session = Depends(get_db)):
    """@Function: 获取定时任务详情"""
    service = SchedulerService(db)
    task = service.get_scheduler_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": task}


@router.post("/tasks", summary="创建定时任务")
async def create_scheduler_task(task: TaskCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的定时任务"""
    service = SchedulerService(db)
    result = service.create_scheduler_task(task.dict())
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/tasks/{task_id}", summary="更新定时任务")
async def update_scheduler_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """@Function: 更新定时任务"""
    service = SchedulerService(db)
    result = service.update_scheduler_task(task_id, task.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/tasks/{task_id}", summary="删除定时任务")
async def delete_scheduler_task(task_id: int, db: Session = Depends(get_db)):
    """@Function: 删除定时任务"""
    service = SchedulerService(db)
    success = service.delete_scheduler_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "message": "删除成功"}


@router.post("/tasks/{task_id}/toggle", summary="启用/禁用定时任务")
async def toggle_scheduler_task(task_id: int, db: Session = Depends(get_db)):
    """@Function: 切换定时任务的启用状态"""
    service = SchedulerService(db)
    result = service.toggle_scheduler_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": result}
