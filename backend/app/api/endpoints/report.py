# -*- coding: utf-8 -*-
"""
测试报告 API / Test report API
@Function: 提供报告查询、统计、导出接口 / Provide report query, statistics, export endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.service.report_service import ReportService

router = APIRouter()


# ===== 固定路由（必须在 /{task_id} 之前注册，否则会被通配捕获）=====
# Fixed routes (must be registered before /{task_id} to avoid wildcard capture)


@router.get("/list", summary="获取报告列表")
async def get_report_list(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取执行报告列表"""
    service = ReportService(db)
    result = service.get_report_list(page, page_size)
    return {"code": 0, "data": result}


@router.get("/statistics/overview", summary="获取统计概览")
async def get_statistics_overview(db: Session = Depends(get_db)):
    """@Function: 获取测试统计概览数据"""
    service = ReportService(db)
    stats = service.get_statistics_overview()
    return {"code": 0, "data": stats}


@router.get("/statistics/trend", summary="获取趋势数据")
async def get_statistics_trend(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """@Function: 获取测试通过率趋势数据"""
    service = ReportService(db)
    trend = service.get_statistics_trend(days)
    return {"code": 0, "data": trend}


@router.get("/statistics/distribution", summary="获取用例分布")
async def get_case_distribution(db: Session = Depends(get_db)):
    """@Function: 获取用例平台分布数据"""
    service = ReportService(db)
    distribution = service.get_case_distribution()
    return {"code": 0, "data": distribution}


# ===== 动态路由（通配符，放最后）=====
# Dynamic routes (wildcards, register last)


@router.get("/{task_id}", summary="获取报告详情")
async def get_report_detail(task_id: str, db: Session = Depends(get_db)):
    """@Function: 获取指定任务的报告详情"""
    service = ReportService(db)
    report = service.get_report_detail(task_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return {"code": 0, "data": report}


@router.get("/{task_id}/html", summary="获取HTML报告")
async def get_html_report(task_id: str, db: Session = Depends(get_db)):
    """@Function: 获取HTML格式的测试报告"""
    service = ReportService(db)
    file_path = service.generate_html_report(task_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="报告不存在")
    return FileResponse(file_path, media_type="text/html", filename=f"report_{task_id}.html")


@router.get("/{task_id}/steps", summary="获取步骤详情")
async def get_step_details(
    task_id: str,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """@Function: 获取用例执行的步骤详情"""
    service = ReportService(db)
    steps = service.get_step_details(task_id, case_id)
    return {"code": 0, "data": steps}


@router.get("/{task_id}/failure-analysis", summary="获取失败分析")
async def get_failure_analysis(task_id: str, db: Session = Depends(get_db)):
    """@Function: 获取失败用例的分类分析"""
    service = ReportService(db)
    analysis = service.get_failure_analysis(task_id)
    return {"code": 0, "data": analysis}


@router.post("/{task_id}/export-defect", summary="导出缺陷详情")
async def export_defect(
    task_id: str,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """@Function: 导出失败用例的缺陷详情"""
    service = ReportService(db)
    defect = service.export_defect(task_id, case_id)
    return {"code": 0, "data": defect}


@router.post("/{task_id}/replay", summary="一键复现")
async def replay_failed_case(
    task_id: str,
    case_id: int,
    db: Session = Depends(get_db),
):
    """@Function: 复现失败的用例执行"""
    service = ReportService(db)
    new_task_id = service.replay_failed_case(task_id, case_id)
    return {"code": 0, "data": {"task_id": new_task_id}, "message": "复现任务已创建"}
