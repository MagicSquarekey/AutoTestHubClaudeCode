# -*- coding: utf-8 -*-
"""
FastAPI 应用入口 / FastAPI application entry point
@Function: 启动后端服务，配置中间件和路由 / Start backend service, configure middleware and routes
"""

import os
import re
import sys
import socket
import subprocess
import signal
import time
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.models.database import init_db, engine
from app.api.router import api_router
from app.engine.recording_manager import recording_manager
from app.utils.logger import get_logger

logger = get_logger("main")


def reset_stale_recordings():
    """@Function: 重置残留的录制状态 / Reset stale recording states on startup

    When the app crashes or is force-closed during recording, the DB status
    remains "recording" but RecordingManager has no memory of the task.
    This function resets such stale tasks back to "pending" so they can be
    re-recorded cleanly.
    """
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(
            text('UPDATE record_task SET status = "pending" WHERE status = "recording"')
        )
        if result.rowcount > 0:
            logger.info(f"启动时重置了 {result.rowcount} 个残留录制任务状态为 pending")
        conn.commit()


def ensure_port_available(host: str, port: int) -> None:
    """@Function: 检测端口是否可用，被占用时自动释放 / Ensure port is available, auto-free if occupied

    Uses socket probe first; if occupied, finds the PID via `netstat` on Windows
    or `lsof` on Unix and terminates the process so uvicorn can bind cleanly.

    Args:
        host: Bind address.
        port: Port number to check.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        sock.close()
        logger.info(f"端口 {port} 可用")
        return
    except OSError:
        sock.close()
        logger.warning(f"端口 {port} 被占用，尝试自动释放...")

    pid = _find_pid_by_port(port)
    if pid is None:
        msg = f"端口 {port} 被占用，但无法定位占用进程，请手动关闭占用进程或修改配置端口（HOST={host}, PORT={port}）"
        logger.error(msg)
        sys.exit(f"❌ {msg}")

    if pid == os.getpid():
        logger.warning(f"端口 {port} 被自身占用（PID={pid}），跳过终止")
        return

    logger.info(f"占用端口 {port} 的进程 PID={pid}，正在终止...")
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                check=True,
                capture_output=True,
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except (subprocess.CalledProcessError, OSError) as exc:
        msg = f"端口 {port} 被进程 PID={pid} 占用，但终止失败: {exc}。请手动关闭该进程或修改配置端口"
        logger.error(msg)
        sys.exit(f"❌ {msg}")

    # 等待端口释放（最多 3 秒）
    for _ in range(30):
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock2.bind((host, port))
            sock2.close()
            logger.info(f"端口 {port} 已释放")
            return
        except OSError:
            sock2.close()
        time.sleep(0.1)

    msg = f"端口 {port} 被进程 PID={pid} 占用，释放超时（3秒）。请手动关闭该进程或修改配置端口（HOST={host}, PORT={port}）"
    logger.error(msg)
    sys.exit(f"❌ {msg}")


def _find_pid_by_port(port: int) -> int | None:
    """@Function: 根据端口号查找占用进程的 PID / Find PID that occupies the given port

    Args:
        port: Port number to look up.

    Returns:
        PID as int, or None if not found.
    """
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            pattern = re.compile(
                rf":{port}\s+.*LISTENING\s+(\d+)"
            )
            match = pattern.search(result.stdout)
            if match:
                return int(match.group(1))
        else:
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-t"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            pids = result.stdout.strip().split("\n")
            if pids and pids[0]:
                return int(pids[0])
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as exc:
        logger.warning(f"查找端口 {port} 占用进程失败: {exc}")
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """@Function: 应用生命周期管理 / Application lifespan management"""
    # 启动时执行 / Run on startup
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("数据库初始化完成 / Database initialized")
    reset_stale_recordings()
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
    ensure_port_available(settings.HOST, settings.PORT)
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # 禁用热重载，避免与执行引擎的线程冲突
        log_level="info",
    )
