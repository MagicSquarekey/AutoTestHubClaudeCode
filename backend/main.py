# -*- coding: utf-8 -*-
"""
FastAPI应用入口
@Function: 启动后端服务
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.models.database import init_db
from app.api.router import api_router
from app.utils.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """@Function: 应用生命周期管理"""
    # 启动时执行
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("数据库初始化完成")
    yield
    # 关闭时执行
    logger.info("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AutoTest Hub 单人落地版 - 自动化测试工具",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


@app.get("/", tags=["健康检查"])
async def root():
    """@Function: 健康检查接口"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """@Function: 健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
