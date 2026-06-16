# -*- coding: utf-8 -*-
"""
设备管理服务
@Function: 提供设备发现、连接、管理功能
"""

import subprocess
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("device")


class DeviceService:
    """设备管理服务类"""

    def __init__(self, db: Session):
        self.db = db
        self._devices: Dict[str, Dict[str, Any]] = {}

    def get_device_list(self, platform: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """@Function: 获取设备列表

        Args:
            platform: 平台筛选
            status: 状态筛选

        Returns:
            设备列表
        """
        devices = list(self._devices.values())

        if platform:
            devices = [d for d in devices if d.get("platform") == platform]
        if status:
            devices = [d for d in devices if d.get("status") == status]

        return devices

    def get_device_detail(self, device_id: str) -> Optional[Dict[str, Any]]:
        """@Function: 获取设备详情

        Args:
            device_id: 设备ID

        Returns:
            设备详情
        """
        return self._devices.get(device_id)

    def scan_devices(self, platform: str = "android") -> List[Dict[str, Any]]:
        """@Function: 扫描设备

        Args:
            platform: 平台类型

        Returns:
            发现的设备列表
        """
        devices = []

        if platform == "android":
            devices = self._scan_android_devices()
        elif platform == "ios":
            devices = self._scan_ios_devices()

        # 更新设备列表
        for device in devices:
            self._devices[device["device_id"]] = device

        logger.info(f"扫描到 {len(devices)} 个 {platform} 设备")
        return devices

    def connect_device(self, device_id: str) -> bool:
        """@Function: 连接设备

        Args:
            device_id: 设备ID

        Returns:
            是否连接成功
        """
        device = self._devices.get(device_id)
        if not device:
            return False

        # TODO: 实际连接设备
        device["status"] = "connected"
        logger.info(f"连接设备: {device_id}")
        return True

    def disconnect_device(self, device_id: str):
        """@Function: 断开设备

        Args:
            device_id: 设备ID
        """
        device = self._devices.get(device_id)
        if device:
            device["status"] = "disconnected"
            logger.info(f"断开设备: {device_id}")

    def take_screenshot(self, device_id: str) -> str:
        """@Function: 设备截图

        Args:
            device_id: 设备ID

        Returns:
            截图文件路径
        """
        # TODO: 实际截图
        logger.info(f"设备截图: {device_id}")
        return ""

    def install_app(self, device_id: str, app_path: str) -> bool:
        """@Function: 安装应用

        Args:
            device_id: 设备ID
            app_path: 应用路径

        Returns:
            是否安装成功
        """
        # TODO: 实际安装
        logger.info(f"安装应用: {device_id}, {app_path}")
        return True

    def uninstall_app(self, device_id: str, package_name: str) -> bool:
        """@Function: 卸载应用

        Args:
            device_id: 设备ID
            package_name: 包名

        Returns:
            是否卸载成功
        """
        # TODO: 实际卸载
        logger.info(f"卸载应用: {device_id}, {package_name}")
        return True

    def get_browser_list(self) -> List[Dict[str, Any]]:
        """@Function: 获取浏览器列表

        Returns:
            浏览器列表
        """
        browsers = []

        # 检测Chrome
        chrome_path = self._find_browser("chrome")
        if chrome_path:
            browsers.append({
                "name": "Chrome",
                "type": "chromium",
                "path": chrome_path,
                "version": self._get_browser_version(chrome_path),
            })

        # 检测Edge
        edge_path = self._find_browser("edge")
        if edge_path:
            browsers.append({
                "name": "Edge",
                "type": "chromium",
                "path": edge_path,
                "version": self._get_browser_version(edge_path),
            })

        return browsers

    def check_browser_driver(self, browser_type: str = "chromium") -> Dict[str, Any]:
        """@Function: 检查浏览器驱动

        Args:
            browser_type: 浏览器类型

        Returns:
            检查结果
        """
        # TODO: 实际检查和更新驱动
        return {
            "browser_type": browser_type,
            "driver_installed": True,
            "driver_version": "latest",
            "needs_update": False,
        }

    def _scan_android_devices(self) -> List[Dict[str, Any]]:
        """@Function: 扫描Android设备

        Returns:
            Android设备列表
        """
        devices = []

        try:
            # 使用adb devices获取设备列表
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # 跳过第一行
                for line in lines:
                    if "\tdevice" in line:
                        device_id = line.split("\t")[0]
                        devices.append({
                            "device_id": device_id,
                            "platform": "android",
                            "status": "connected",
                            "name": f"Android Device ({device_id})",
                        })
        except Exception as e:
            logger.error(f"扫描Android设备失败: {e}")

        return devices

    def _scan_ios_devices(self) -> List[Dict[str, Any]]:
        """@Function: 扫描iOS设备

        Returns:
            iOS设备列表
        """
        # TODO: 使用tidevice扫描iOS设备
        return []

    def _find_browser(self, browser_name: str) -> Optional[str]:
        """@Function: 查找浏览器路径

        Args:
            browser_name: 浏览器名称

        Returns:
            浏览器路径
        """
        import platform
        from pathlib import Path

        if platform.system() == "Windows":
            paths = {
                "chrome": [
                    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
                    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
                ],
                "edge": [
                    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
                    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
                ],
            }
        else:
            paths = {
                "chrome": [Path("/usr/bin/google-chrome")],
                "edge": [Path("/usr/bin/microsoft-edge")],
            }

        for path in paths.get(browser_name, []):
            if path.exists():
                return str(path)

        return None

    def _get_browser_version(self, browser_path: str) -> str:
        """@Function: 获取浏览器版本

        Args:
            browser_path: 浏览器路径

        Returns:
            版本号
        """
        try:
            result = subprocess.run(
                [browser_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # 解析版本号
                version_str = result.stdout.strip()
                # Chrome/Edge格式: "Google Chrome xx.x.xxxx.xx" 或 "Microsoft Edge xx.x.xxxx.xx"
                parts = version_str.split()
                if parts:
                    return parts[-1]
        except Exception:
            pass

        return "unknown"
