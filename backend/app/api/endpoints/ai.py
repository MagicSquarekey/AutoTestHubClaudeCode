# -*- coding: utf-8 -*-
"""
AI 辅助 API / AI assistant API
@Function: 提供自然语言生成用例、元素智能修复、失败分析接口 / Provide NL case generation, element repair, failure analysis endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.ai_service import AIService

router = APIRouter()


class GenerateCaseRequest(BaseModel):
    """自然语言生成用例请求"""
    description: str
    platform: str = "web"
    module: str = ""


class RepairElementRequest(BaseModel):
    """元素修复请求"""
    element_id: int
    page_source: Optional[str] = None
    screenshot_path: Optional[str] = None


class AnalyzeFailureRequest(BaseModel):
    """失败分析请求"""
    task_id: str
    case_id: Optional[int] = None


@router.post("/generate-case", summary="自然语言生成用例")
async def generate_case(request: GenerateCaseRequest, db: Session = Depends(get_db)):
    """@Function: 根据自然语言描述生成测试用例"""
    service = AIService(db)
    try:
        result = service.generate_case(
            description=request.description,
            platform=request.platform,
            module=request.module,
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/repair-element", summary="智能修复元素")
async def repair_element(request: RepairElementRequest, db: Session = Depends(get_db)):
    """@Function: 使用AI智能修复失效的元素定位符"""
    service = AIService(db)
    try:
        result = service.repair_element(
            element_id=request.element_id,
            page_source=request.page_source,
            screenshot_path=request.screenshot_path,
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修复失败: {str(e)}")


@router.post("/analyze-failure", summary="分析失败原因")
async def analyze_failure(request: AnalyzeFailureRequest, db: Session = Depends(get_db)):
    """@Function: 使用AI分析用例执行失败的原因"""
    service = AIService(db)
    try:
        result = service.analyze_failure(
            task_id=request.task_id,
            case_id=request.case_id,
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/failure-statistics", summary="获取失败统计")
async def get_failure_statistics(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """@Function: 获取高频失败原因统计"""
    service = AIService(db)
    stats = service.get_failure_statistics(days)
    return {"code": 0, "data": stats}


@router.get("/config", summary="获取AI配置")
async def get_ai_config(db: Session = Depends(get_db)):
    """@Function: 获取AI服务配置"""
    service = AIService(db)
    config = service.get_ai_config()
    return {"code": 0, "data": config}


@router.put("/config", summary="更新AI配置")
async def update_ai_config(config: dict, db: Session = Depends(get_db)):
    """@Function: 更新AI服务配置"""
    service = AIService(db)
    service.update_ai_config(config)
    return {"code": 0, "message": "配置已更新"}
