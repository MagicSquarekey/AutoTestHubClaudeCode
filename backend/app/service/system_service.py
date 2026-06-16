# -*- coding: utf-8 -*-
"""
系统设置服务
@Function: 提供系统配置、数据备份恢复、全局变量管理功能
"""

import json
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.sys_config import SysConfig
from app.models.global_var import GlobalVar
from app.core.config import settings
from app.utils.crypto import encrypt, decrypt
from app.utils.logger import get_logger

logger = get_logger("system")


class SystemService:
    """系统设置服务类"""

    def __init__(self, db: Session):
        self.db = db

    # 系统配置管理
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """@Function: 获取所有配置

        Returns:
            配置列表
        """
        configs = self.db.query(SysConfig).all()
        return [config.to_dict() for config in configs]

    def get_config(self, config_key: str) -> Optional[Dict[str, Any]]:
        """@Function: 获取配置

        Args:
            config_key: 配置键

        Returns:
            配置信息
        """
        config = self.db.query(SysConfig).filter(SysConfig.config_key == config_key).first()
        return config.to_dict() if config else None

    def update_config(self, data: Dict[str, Any]):
        """@Function: 更新配置

        Args:
            data: 配置数据
        """
        config_key = data.get("config_key")
        config = self.db.query(SysConfig).filter(SysConfig.config_key == config_key).first()

        if config:
            # 加密敏感数据
            if data.get("config_type") == "encrypted":
                config.config_value = encrypt(data.get("config_value", ""))
            else:
                config.config_value = data.get("config_value", "")

            config.config_type = data.get("config_type", config.config_type)
            config.description = data.get("description", config.description)
            config.update_time = datetime.now()
        else:
            # 创建新配置
            config = SysConfig(
                config_key=config_key,
                config_value=encrypt(data.get("config_value", "")) if data.get("config_type") == "encrypted" else data.get("config_value", ""),
                config_type=data.get("config_type", "string"),
                description=data.get("description", ""),
            )
            self.db.add(config)

        self.db.commit()
        logger.info(f"更新配置: {config_key}")

    def batch_update_configs(self, configs: Dict[str, Any]):
        """@Function: 批量更新配置

        Args:
            configs: 配置字典
        """
        for key, value in configs.items():
            self.update_config({"config_key": key, "config_value": value})

    # 全局变量管理
    def get_all_variables(self) -> List[Dict[str, Any]]:
        """@Function: 获取所有变量

        Returns:
            变量列表
        """
        variables = self.db.query(GlobalVar).all()
        return [var.to_dict() for var in variables]

    def create_variable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建变量

        Args:
            data: 变量数据

        Returns:
            创建的变量
        """
        # 加密敏感变量
        if data.get("var_type") == "encrypted":
            data["var_value"] = encrypt(data.get("var_value", ""))

        variable = GlobalVar(**data)
        self.db.add(variable)
        self.db.commit()
        self.db.refresh(variable)

        logger.info(f"创建变量: {variable.var_name}")
        return variable.to_dict()

    def update_variable(self, var_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新变量

        Args:
            var_id: 变量ID
            data: 更新数据

        Returns:
            更新后的变量
        """
        variable = self.db.query(GlobalVar).filter(GlobalVar.id == var_id).first()
        if not variable:
            return None

        # 加密敏感变量
        if data.get("var_type") == "encrypted" or (variable.var_type == "encrypted" and "var_value" in data):
            data["var_value"] = encrypt(data.get("var_value", ""))

        for key, value in data.items():
            if hasattr(variable, key):
                setattr(variable, key, value)

        variable.update_time = datetime.now()
        self.db.commit()
        self.db.refresh(variable)

        logger.info(f"更新变量: {variable.var_name}")
        return variable.to_dict()

    def delete_variable(self, var_id: int) -> bool:
        """@Function: 删除变量

        Args:
            var_id: 变量ID

        Returns:
            是否删除成功
        """
        variable = self.db.query(GlobalVar).filter(GlobalVar.id == var_id).first()
        if not variable:
            return False

        self.db.delete(variable)
        self.db.commit()

        logger.info(f"删除变量: {variable.var_name}")
        return True

    # 数据备份恢复
    def backup_data(self) -> str:
        """@Function: 备份数据

        Returns:
            备份文件路径
        """
        backup_dir = Path(settings.DATA_DIR) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"autotest_backup_{timestamp}"
        backup_path = backup_dir / backup_name

        # 创建备份目录
        backup_path.mkdir(parents=True, exist_ok=True)

        # 复制数据库文件
        db_file = Path(settings.DATA_DIR) / "autotest.db"
        if db_file.exists():
            shutil.copy2(db_file, backup_path / "autotest.db")

        # 复制配置文件
        config_file = Path(settings.DATA_DIR) / ".secret_key"
        if config_file.exists():
            shutil.copy2(config_file, backup_path / ".secret_key")

        # 创建备份信息文件
        info = {
            "backup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": settings.APP_VERSION,
            "files": list(backup_path.glob("*")),
        }
        (backup_path / "backup_info.json").write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")

        # 压缩备份
        shutil.make_archive(str(backup_path), "zip", backup_path)
        shutil.rmtree(backup_path)

        backup_file = Path(f"{backup_path}.zip")
        logger.info(f"数据备份成功: {backup_file}")
        return str(backup_file)

    def restore_data(self, backup_path: str) -> bool:
        """@Function: 恢复数据

        Args:
            backup_path: 备份文件路径

        Returns:
            是否恢复成功
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False

            # 解压备份
            restore_dir = Path(settings.DATA_DIR) / "restore_temp"
            shutil.unpack_archive(str(backup_file), str(restore_dir), "zip")

            # 恢复数据库
            db_backup = restore_dir / "autotest.db"
            if db_backup.exists():
                db_file = Path(settings.DATA_DIR) / "autotest.db"
                shutil.copy2(db_backup, db_file)

            # 恢复密钥
            key_backup = restore_dir / ".secret_key"
            if key_backup.exists():
                key_file = Path(settings.DATA_DIR) / ".secret_key"
                shutil.copy2(key_backup, key_file)

            # 清理临时目录
            shutil.rmtree(restore_dir)

            logger.info("数据恢复成功")
            return True

        except Exception as e:
            logger.error(f"数据恢复失败: {e}")
            return False

    def clear_cache(self) -> Dict[str, Any]:
        """@Function: 清理缓存

        Returns:
            清理结果
        """
        cleaned_size = 0

        # 清理截图缓存
        screenshot_dir = Path(settings.SCREENSHOT_DIR)
        if screenshot_dir.exists():
            for file in screenshot_dir.glob("*"):
                if file.is_file():
                    cleaned_size += file.stat().st_size
                    file.unlink()

        # 清理临时文件
        temp_dir = Path(settings.DATA_DIR) / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        logger.info(f"清理缓存完成: {cleaned_size / 1024 / 1024:.2f} MB")
        return {
            "cleaned_size_mb": round(cleaned_size / 1024 / 1024, 2),
        }

    def get_system_info(self) -> Dict[str, Any]:
        """@Function: 获取系统信息

        Returns:
            系统信息
        """
        import platform
        import psutil

        return {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
            "memory_available_gb": round(psutil.virtual_memory().available / 1024 / 1024 / 1024, 2),
            "disk_total_gb": round(psutil.disk_usage("/").total / 1024 / 1024 / 1024, 2),
            "disk_free_gb": round(psutil.disk_usage("/").free / 1024 / 1024 / 1024, 2),
        }
