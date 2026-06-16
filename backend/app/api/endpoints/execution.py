# -*- coding: utf-8 -*-
"""
执行引擎API
@Function: 提供用例执行、任务管理、执行控制接口
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.exec_service import ExecService

router = APIRouter()


class ExecRequest(BaseModel):
    """执行请求"""
    case_ids: List[int]
    platform: str = "web"
    device_id: Optional[str] = None
    browser_type: str = "chromium"
    headless: bool = False
    timeout: int = 30
    retry_count: int = 3
    enable_screenshot: bool = True
    enable_video: bool = False
    variables: Dict[str, str] = {}


class TaskControl(BaseModel):
    """任务控制"""
    action: str  # pause/resume/stop


@router.post("/run", summary="执行用例")
async def run_cases(request: ExecRequest, db: Session = Depends(get_db)):
    """@Function: 执行指定的测试用例"""
    service = ExecService(db)
    task_id = service.create_task(request.dict())
    return {"code": 0, "data": {"task_id": task_id}, "message": "任务已创建"}


@router.post("/run-suite/{suite_id}", summary="执行用例集")
async def run_suite(
    suite_id: int,
    platform: str = "web",
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 执行指定的测试套件"""
    service = ExecService(db)
    task_id = service.run_suite(suite_id, platform, device_id)
    return {"code": 0, "data": {"task_id": task_id}, "message": "任务已创建"}


@router.get("/status/{task_id}", summary="查询任务状态")
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """@Function: 查询执行任务的状态"""
    service = ExecService(db)
    status = service.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": status}


@router.post("/control/{task_id}", summary="控制任务执行")
async def control_task(task_id: str, control: TaskControl, db: Session = Depends(get_db)):
    """@Function: 控制任务执行（暂停/继续/停止）"""
    service = ExecService(db)
    success = service.control_task(task_id, control.action)
    if not success:
        raise HTTPException(status_code=400, detail="控制失败")
    return {"code": 0, "message": f"已{control.action}任务"}


@router.get("/log/{task_id}", summary="获取执行日志")
async def get_exec_log(
    task_id: str,
    case_id: Optional[int] = None,
    step_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 获取执行过程的日志"""
    service = ExecService(db)
    logs = service.get_exec_log(task_id, case_id, step_id)
    return {"code": 0, "data": logs}


@router.get("/screenshot/{task_id}", summary="获取执行截图")
async def get_exec_screenshot(
    task_id: str,
    case_id: Optional[int] = None,
    step_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 获取执行过程的截图"""
    service = ExecService(db)
    screenshots = service.get_exec_screenshot(task_id, case_id, step_id)
    return {"code": 0, "data": screenshots}


@router.get("/tasks", summary="获取任务列表")
async def get_task_list(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取执行任务列表"""
    service = ExecService(db)
    result = service.get_task_list(status, page, page_size)
    return {"code": 0, "data": result}


@router.post("/debug/step", summary="单步调试")
async def debug_step(
    case_id: int,
    step_id: str,
    platform: str = "web",
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 单步调试执行指定步骤"""
    service = ExecService(db)
    result = service.debug_step(case_id, step_id, platform, device_id)
    return {"code": 0, "data": result}


@router.post("/debug/breakpoint", summary="断点调试")
async def debug_with_breakpoint(
    case_id: int,
    breakpoint_step_id: str,
    platform: str = "web",
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 执行到断点位置暂停"""
    service = ExecService(db)
    task_id = service.debug_with_breakpoint(case_id, breakpoint_step_id, platform, device_id)
    return {"code": 0, "data": {"task_id": task_id}}
