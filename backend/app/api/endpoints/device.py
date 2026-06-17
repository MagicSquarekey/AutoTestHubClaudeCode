# -*- coding: utf-8 -*-
"""
设备管理 API / Device management API
@Function: 提供设备发现、连接、管理接口 / Provide device discovery, connection, management endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.service.device_service import DeviceService

router = APIRouter()


@router.get("/list", summary="获取设备列表")
async def get_device_list(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 获取已连接的设备列表"""
    service = DeviceService(db)
    devices = service.get_device_list(platform, status)
    return {"code": 0, "data": devices}


@router.get("/{device_id}", summary="获取设备详情")
async def get_device_detail(device_id: str, db: Session = Depends(get_db)):
    """@Function: 获取设备详细信息"""
    service = DeviceService(db)
    device = service.get_device_detail(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return {"code": 0, "data": device}


@router.post("/scan", summary="扫描设备")
async def scan_devices(
    platform: str = "android",
    db: Session = Depends(get_db),
):
    """@Function: 扫描并发现新设备"""
    service = DeviceService(db)
    devices = service.scan_devices(platform)
    return {"code": 0, "data": devices}


@router.post("/{device_id}/connect", summary="连接设备")
async def connect_device(device_id: str, db: Session = Depends(get_db)):
    """@Function: 连接指定设备"""
    service = DeviceService(db)
    success = service.connect_device(device_id)
    if not success:
        raise HTTPException(status_code=400, detail="连接失败")
    return {"code": 0, "message": "连接成功"}


@router.post("/{device_id}/disconnect", summary="断开设备")
async def disconnect_device(device_id: str, db: Session = Depends(get_db)):
    """@Function: 断开设备连接"""
    service = DeviceService(db)
    service.disconnect_device(device_id)
    return {"code": 0, "message": "已断开连接"}


@router.get("/{device_id}/screenshot", summary="设备截图")
async def take_screenshot(device_id: str, db: Session = Depends(get_db)):
    """@Function: 获取设备当前截图"""
    service = DeviceService(db)
    screenshot_path = service.take_screenshot(device_id)
    return {"code": 0, "data": {"screenshot_path": screenshot_path}}


@router.post("/{device_id}/install-app", summary="安装应用")
async def install_app(
    device_id: str,
    app_path: str,
    db: Session = Depends(get_db),
):
    """@Function: 向设备安装应用"""
    service = DeviceService(db)
    success = service.install_app(device_id, app_path)
    if not success:
        raise HTTPException(status_code=400, detail="安装失败")
    return {"code": 0, "message": "安装成功"}


@router.post("/{device_id}/uninstall-app", summary="卸载应用")
async def uninstall_app(
    device_id: str,
    package_name: str,
    db: Session = Depends(get_db),
):
    """@Function: 从设备卸载应用"""
    service = DeviceService(db)
    success = service.uninstall_app(device_id, package_name)
    if not success:
        raise HTTPException(status_code=400, detail="卸载失败")
    return {"code": 0, "message": "卸载成功"}


@router.get("/browsers", summary="获取浏览器列表")
async def get_browser_list(db: Session = Depends(get_db)):
    """@Function: 获取可用的浏览器列表"""
    service = DeviceService(db)
    browsers = service.get_browser_list()
    return {"code": 0, "data": browsers}


@router.post("/browsers/driver-check", summary="检查浏览器驱动")
async def check_browser_driver(
    browser_type: str = "chromium",
    db: Session = Depends(get_db),
):
    """@Function: 检查并更新浏览器驱动"""
    service = DeviceService(db)
    result = service.check_browser_driver(browser_type)
    return {"code": 0, "data": result}
