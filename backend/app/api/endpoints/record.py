# -*- coding: utf-8 -*-
"""
录制管理 API / Record management API
@Function: 提供录制任务和步骤的 CRUD、录制控制、转换接口 / Provide CRUD, recording control, conversion endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.record_service import RecordService
from app.service.case_service import CaseService
from app.engine.recording_manager import recording_manager
from app.utils.logger import get_logger

logger = get_logger("record_api")

router = APIRouter()


# ==================== 请求模型 / Request Models ====================

class TaskCreate(BaseModel):
    """录制任务创建请求"""
    task_name: str = "未命名录制任务"
    target_url: str = ""
    browser_type: str = "chromium"
    description: str = ""


class TaskUpdate(BaseModel):
    """录制任务更新请求"""
    task_name: Optional[str] = None
    target_url: Optional[str] = None
    browser_type: Optional[str] = None
    description: Optional[str] = None


class StepCreate(BaseModel):
    """录制步骤创建请求"""
    task_id: int
    step_order: Optional[int] = None
    action_type: str
    element_locators: Dict[str, Any] = {}
    element_name: str = ""
    input_value: str = ""
    screenshot: str = ""
    page_url: str = ""


class StepUpdate(BaseModel):
    """录制步骤更新请求"""
    step_order: Optional[int] = None
    action_type: Optional[str] = None
    element_locators: Optional[Dict[str, Any]] = None
    element_name: Optional[str] = None
    input_value: Optional[str] = None
    screenshot: Optional[str] = None
    page_url: Optional[str] = None


class StepMove(BaseModel):
    """步骤移动请求"""
    direction: str  # up/down


class ConvertRequest(BaseModel):
    """转换为测试用例请求"""
    case_name: str
    module: str = ""
    tags: List[str] = []
    priority: str = "P0"
    description: str = ""
    platform: str = "web"


class BatchStepCreate(BaseModel):
    """批量创建步骤请求"""
    steps: List[Dict[str, Any]]


# ==================== 录制任务接口 / Record Task Endpoints ====================

@router.get("/tasks/list", summary="获取录制任务列表")
async def get_task_list(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取录制任务列表，支持筛选和分页"""
    service = RecordService(db)
    result = service.get_task_list(
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return {"code": 0, "data": result}


@router.get("/tasks/{task_id}", summary="获取录制任务详情")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """@Function: 根据ID获取录制任务详情"""
    service = RecordService(db)
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")
    return {"code": 0, "data": task}


@router.post("/tasks/create", summary="创建录制任务")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的录制任务"""
    service = RecordService(db)
    result = service.create_task(task.dict())
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/tasks/{task_id}", summary="更新录制任务")
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """@Function: 更新录制任务信息"""
    service = RecordService(db)
    result = service.update_task(task_id, task.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="录制任务不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/tasks/{task_id}", summary="删除录制任务")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """@Function: 删除录制任务及其所有步骤"""
    service = RecordService(db)
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="录制任务不存在")
    return {"code": 0, "message": "删除成功"}


@router.post("/tasks/{task_id}/start", summary="开始录制")
async def start_recording(task_id: int, db: Session = Depends(get_db)):
    """@Function: 开始录制任务"""
    logger.info(f"收到开始录制请求，任务ID: {task_id}")
    service = RecordService(db)
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    if task["status"] == "recording":
        # 检查录制引擎是否真的在运行
        if recording_manager.is_recording(task_id):
            return {"code": 1, "message": "任务正在录制中"}
        else:
            # 状态异常，重置为 pending
            logger.warning(f"任务 {task_id} 状态异常，重置为 pending")
            service.update_task_status(task_id, "pending")
            task["status"] = "pending"

    target_url = task.get("target_url", "")
    browser_type = task.get("browser_type", "chromium")

    logger.info(f"准备启动录制引擎，任务ID: {task_id}，目标URL: {target_url}，浏览器: {browser_type}")

    # 启动录制引擎
    success = recording_manager.start_recording(task_id, target_url, browser_type)
    if not success:
        return {"code": 1, "message": "启动录制失败，请重试"}

    # 更新任务状态
    result = service.update_task_status(task_id, "recording")
    logger.info(f"录制任务 {task_id} 已启动，目标URL: {target_url}")
    return {"code": 0, "data": result, "message": "录制已开始，浏览器即将打开"}


@router.post("/tasks/{task_id}/stop", summary="停止录制")
async def stop_recording(task_id: int, db: Session = Depends(get_db)):
    """@Function: 停止录制任务"""
    service = RecordService(db)
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    if task["status"] != "recording":
        return {"code": 1, "message": "任务未在录制中"}

    # 停止录制引擎并获取录制的操作
    actions = recording_manager.stop_recording(task_id)
    logger.info(f"录制任务 {task_id} 已停止，获取到 {len(actions)} 个操作")

    # 更新任务状态
    result = service.update_task_status(task_id, "completed")

    # 刷新步骤列表
    steps = service.get_steps_by_task_id(task_id)

    return {"code": 0, "data": {"task": result, "steps": steps, "actions_count": len(actions)}, "message": f"录制已停止，共录制 {len(steps)} 个步骤"}


@router.get("/tasks/{task_id}/status", summary="获取录制状态")
async def get_recording_status(task_id: int, db: Session = Depends(get_db)):
    """@Function: 获取录制任务的实时状态"""
    service = RecordService(db)
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    is_recording = recording_manager.is_recording(task_id)

    # 如果任务状态是 recording 但实际没有在录制，自动修复状态
    if task.get("status") == "recording" and not is_recording:
        logger.info(f"检测到任务 {task_id} 状态异常，自动修复为 completed")
        service.update_task_status(task_id, "completed")
        task["status"] = "completed"

    # 获取最新的步骤列表
    steps = service.get_steps_by_task_id(task_id)

    return {
        "code": 0,
        "data": {
            "task_id": task_id,
            "status": task.get("status"),
            "is_recording": is_recording,
            "step_count": len(steps),
            "steps": steps,
        }
    }


@router.post("/tasks/{task_id}/reset", summary="重置任务状态")
async def reset_task_status(task_id: int, db: Session = Depends(get_db)):
    """@Function: 重置任务状态为 pending（用于修复卡住的任务）"""
    service = RecordService(db)
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    # 停止可能存在的录制引擎
    if recording_manager.is_recording(task_id):
        recording_manager.stop_recording(task_id)

    result = service.update_task_status(task_id, "pending")
    return {"code": 0, "data": result, "message": "任务状态已重置"}


# ==================== 录制步骤接口 / Record Step Endpoints ====================

@router.get("/tasks/{task_id}/steps", summary="获取任务步骤列表")
async def get_steps(task_id: int, db: Session = Depends(get_db)):
    """@Function: 获取录制任务的所有步骤"""
    service = RecordService(db)
    # 验证任务存在 / Verify task exists
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    steps = service.get_steps_by_task_id(task_id)
    return {"code": 0, "data": steps}


@router.post("/steps/create", summary="创建录制步骤")
async def create_step(step: StepCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的录制步骤"""
    service = RecordService(db)
    # 验证任务存在 / Verify task exists
    task = service.get_task_by_id(step.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    result = service.create_step(step.dict())
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/steps/{step_id}", summary="更新录制步骤")
async def update_step(step_id: int, step: StepUpdate, db: Session = Depends(get_db)):
    """@Function: 更新录制步骤信息"""
    service = RecordService(db)
    result = service.update_step(step_id, step.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="录制步骤不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/steps/{step_id}", summary="删除录制步骤")
async def delete_step(step_id: int, db: Session = Depends(get_db)):
    """@Function: 删除录制步骤"""
    service = RecordService(db)
    success = service.delete_step(step_id)
    if not success:
        raise HTTPException(status_code=404, detail="录制步骤不存在")
    return {"code": 0, "message": "删除成功"}


@router.post("/steps/{step_id}/move", summary="移动步骤顺序")
async def move_step(step_id: int, move: StepMove, db: Session = Depends(get_db)):
    """@Function: 移动步骤顺序（上移/下移）"""
    service = RecordService(db)
    result = service.move_step(step_id, move.direction)
    if result is None:
        return {"code": 1, "message": "无法移动"}
    return {"code": 0, "data": result, "message": "移动成功"}


@router.post("/steps/batch-create", summary="批量创建步骤")
async def batch_create_steps(data: BatchStepCreate, task_id: int = None, db: Session = Depends(get_db)):
    """@Function: 批量创建录制步骤"""
    if not task_id:
        return {"code": 1, "message": "缺少 task_id 参数"}

    service = RecordService(db)
    # 验证任务存在 / Verify task exists
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    result = service.batch_create_steps(task_id, data.steps)
    return {"code": 0, "data": result, "message": f"批量创建成功，共 {len(result)} 个步骤"}


# ==================== 转换接口 / Conversion Endpoints ====================

@router.post("/tasks/{task_id}/convert", summary="转换为测试用例")
async def convert_to_case(task_id: int, convert: ConvertRequest, db: Session = Depends(get_db)):
    """@Function: 将录制任务转换为测试用例"""
    record_service = RecordService(db)
    case_service = CaseService(db)

    # 验证任务存在 / Verify task exists
    task = record_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="录制任务不存在")

    # 获取录制步骤 / Get recorded steps
    steps = record_service.get_steps_by_task_id(task_id)
    if not steps:
        return {"code": 1, "message": "录制任务没有步骤，无法转换"}

    # 转换步骤格式 / Convert step format
    case_steps = []
    for step in steps:
        action_type = step.get("action_type", "")
        element_locators = step.get("element_locators", "{}")
        input_value = step.get("input_value", "")

        # 映射操作类型到关键字 / Map action type to keyword
        keyword_map = {
            "navigate": "open_url",
            "click": "click",
            "input": "input_text",
            "select": "select",
            "hover": "hover",
            "wait": "wait",
            "keyboard": "execute_js",
        }
        keyword = keyword_map.get(action_type, action_type)

        # 构建步骤参数 / Build step params
        params = {}
        if keyword == "open_url":
            params = {"url": input_value}
        elif keyword in ["click", "hover", "select", "input_text"]:
            params = {"element": element_locators}
            if keyword == "input_text":
                params["value"] = input_value
            elif keyword == "select":
                params["value"] = input_value
        elif keyword == "wait":
            params = {"timeout": int(input_value) if input_value.isdigit() else 3000}

        case_step = {
            "keyword": keyword,
            "params": params,
            "order": step.get("step_order", 0),
        }
        case_steps.append(case_step)

    # 创建测试用例 / Create test case
    case_data = {
        "case_name": convert.case_name,
        "module": convert.module,
        "tags": convert.tags,
        "priority": convert.priority,
        "description": convert.description or f"从录制任务转换: {task.get('task_name', '')}",
        "steps": str(case_steps),
        "platform": convert.platform,
    }

    try:
        result = case_service.create_case(case_data)
        return {"code": 0, "data": result, "message": "转换成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}
    except Exception as e:
        return {"code": 1, "message": f"转换失败: {str(e)}"}
