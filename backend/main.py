# -*- coding: utf-8 -*-
"""
FastAPI 应用入口 / FastAPI application entry point
@Function: 启动后端服务，配置中间件和路由 / Start backend service, configure middleware and routes
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.models.database import init_db
from app.api.router import api_router
from app.engine.recording_manager import recording_manager
from app.utils.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """@Function: 应用生命周期管理 / Application lifespan management"""
    # 启动时执行 / Run on startup
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("数据库初始化完成 / Database initialized")
    yield
    # 关闭时执行 / Run on shutdown
    logger.info("应用关闭，清理录制引擎...")
    recording_manager.cleanup()
    logger.info("应用关闭 / Application shutdown")


# 创建 FastAPI 应用 / Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AutoTest Hub 单人落地版 - 自动化测试工具 / Standalone automation testing tool",
    lifespan=lifespan,
)

# 配置跨域资源共享 / Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由 / Register API routes
app.include_router(api_router)


@app.get("/", tags=["健康检查"])
async def root():
    """@Function: 根路径健康检查 / Root path health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """@Function: 健康检查接口 / Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # 禁用热重载，避免与执行引擎的线程冲突
        log_level="info",
    )
