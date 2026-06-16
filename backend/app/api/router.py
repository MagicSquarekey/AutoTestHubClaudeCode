# -*- coding: utf-8 -*-
"""
API路由注册
@Function: 统一注册所有API路由
"""

from fastapi import APIRouter
from app.api.endpoints import test_case, test_element, execution, report, device, scheduler, system, ai

# 创建主路由器
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(test_case.router, prefix="/case", tags=["用例管理"])
api_router.include_router(test_element.router, prefix="/element", tags=["元素管理"])
api_router.include_router(execution.router, prefix="/exec", tags=["执行引擎"])
api_router.include_router(report.router, prefix="/report", tags=["测试报告"])
api_router.include_router(device.router, prefix="/device", tags=["设备管理"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["任务调度"])
api_router.include_router(system.router, prefix="/system", tags=["系统设置"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI辅助"])
