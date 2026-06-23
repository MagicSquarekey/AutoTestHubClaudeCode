# -*- coding: utf-8 -*-
"""
API 路由注册 / API route registration
@Function: 统一注册所有 API 路由到主路由器 / Register all API routes to main router
"""

from fastapi import APIRouter
from app.api.endpoints import test_case, test_element, execution, report, device, scheduler, system, ai, record, debug, module, tag, category

# 创建主路由器 / Create main router
api_router = APIRouter(prefix="/api")

# 注册各模块子路由 / Register module sub-routers
api_router.include_router(test_case.router, prefix="/case", tags=["用例管理 / Test Cases"])
api_router.include_router(test_element.router, prefix="/element", tags=["元素管理 / Elements"])
api_router.include_router(execution.router, prefix="/exec", tags=["执行引擎 / Execution"])
api_router.include_router(report.router, prefix="/report", tags=["测试报告 / Reports"])
api_router.include_router(device.router, prefix="/device", tags=["设备管理 / Devices"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["任务调度 / Scheduler"])
api_router.include_router(system.router, prefix="/system", tags=["系统设置 / System"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI辅助 / AI Assistant"])
api_router.include_router(record.router, prefix="/record", tags=["页面录制 / Page Recording"])
api_router.include_router(debug.router, prefix="/debug", tags=["调试运行 / Debug Run"])
api_router.include_router(module.router, prefix="/module", tags=["模块管理 / Module Management"])
api_router.include_router(tag.router, prefix="/tag", tags=["标签管理 / Tag Management"])
api_router.include_router(category.router, prefix="/record/categories", tags=["录制分类 / Recording Categories"])
