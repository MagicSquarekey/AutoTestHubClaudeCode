# -*- coding: utf-8 -*-
"""
系统设置 API / System settings API
@Function: 提供系统配置、数据备份恢复、全局变量管理接口 / Provide config, backup/restore, global variable endpoints
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.system_service import SystemService

router = APIRouter()


class ConfigUpdate(BaseModel):
    """配置更新请求"""
    config_key: str
    config_value: str
    config_type: str = "string"
    description: str = ""


class VariableCreate(BaseModel):
    """变量创建请求"""
    var_name: str
    var_value: str
    var_type: str = "string"
    description: str = ""
    scope: str = "global"


class VariableUpdate(BaseModel):
    """变量更新请求"""
    var_name: Optional[str] = None
    var_value: Optional[str] = None
    var_type: Optional[str] = None
    description: Optional[str] = None


# 系统配置接口
@router.get("/configs", summary="获取所有配置")
async def get_all_configs(db: Session = Depends(get_db)):
    """@Function: 获取所有系统配置"""
    service = SystemService(db)
    configs = service.get_all_configs()
    return {"code": 0, "data": configs}


@router.get("/configs/{config_key}", summary="获取配置")
async def get_config(config_key: str, db: Session = Depends(get_db)):
    """@Function: 获取指定配置项"""
    service = SystemService(db)
    config = service.get_config(config_key)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"code": 0, "data": config}


@router.put("/configs", summary="更新配置")
async def update_config(config: ConfigUpdate, db: Session = Depends(get_db)):
    """@Function: 更新系统配置"""
    service = SystemService(db)
    service.update_config(config.dict())
    return {"code": 0, "message": "配置已更新"}


@router.put("/configs/batch", summary="批量更新配置")
async def batch_update_configs(configs: Dict[str, Any], db: Session = Depends(get_db)):
    """@Function: 批量更新系统配置"""
    service = SystemService(db)
    service.batch_update_configs(configs)
    return {"code": 0, "message": "配置已更新"}


# 全局变量接口
@router.get("/variables", summary="获取所有变量")
async def get_all_variables(db: Session = Depends(get_db)):
    """@Function: 获取所有全局变量"""
    service = SystemService(db)
    variables = service.get_all_variables()
    return {"code": 0, "data": variables}


@router.post("/variables", summary="创建变量")
async def create_variable(variable: VariableCreate, db: Session = Depends(get_db)):
    """@Function: 创建全局变量"""
    service = SystemService(db)
    result = service.create_variable(variable.dict())
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/variables/{var_id}", summary="更新变量")
async def update_variable(var_id: int, variable: VariableUpdate, db: Session = Depends(get_db)):
    """@Function: 更新全局变量"""
    service = SystemService(db)
    result = service.update_variable(var_id, variable.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="变量不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/variables/{var_id}", summary="删除变量")
async def delete_variable(var_id: int, db: Session = Depends(get_db)):
    """@Function: 删除全局变量"""
    service = SystemService(db)
    success = service.delete_variable(var_id)
    if not success:
        raise HTTPException(status_code=404, detail="变量不存在")
    return {"code": 0, "message": "删除成功"}


# 数据备份恢复接口
@router.post("/backup", summary="数据备份")
async def backup_data(db: Session = Depends(get_db)):
    """@Function: 备份所有数据"""
    service = SystemService(db)
    backup_path = service.backup_data()
    return {"code": 0, "data": {"backup_path": backup_path}, "message": "备份成功"}


@router.post("/restore", summary="数据恢复")
async def restore_data(backup_path: str, db: Session = Depends(get_db)):
    """@Function: 从备份恢复数据"""
    service = SystemService(db)
    success = service.restore_data(backup_path)
    if not success:
        raise HTTPException(status_code=400, detail="恢复失败")
    return {"code": 0, "message": "恢复成功"}


@router.get("/backup/download/{filename}", summary="下载备份文件")
async def download_backup(filename: str):
    """@Function: 下载备份文件"""
    from pathlib import Path
    from app.core.config import settings
    file_path = Path(settings.DATA_DIR) / "backups" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")
    return FileResponse(file_path, filename=filename)


@router.post("/clear-cache", summary="清理缓存")
async def clear_cache(db: Session = Depends(get_db)):
    """@Function: 清理系统缓存"""
    service = SystemService(db)
    result = service.clear_cache()
    return {"code": 0, "data": result, "message": "缓存已清理"}


@router.get("/system-info", summary="获取系统信息")
async def get_system_info(db: Session = Depends(get_db)):
    """@Function: 获取系统运行信息"""
    service = SystemService(db)
    info = service.get_system_info()
    return {"code": 0, "data": info}


# 菜单配置接口
@router.get("/menu-config", summary="获取菜单配置")
async def get_menu_config(db: Session = Depends(get_db)):
    """@Function: 获取菜单显示配置"""
    service = SystemService(db)
    config = service.get_menu_config()
    return {"code": 0, "data": config}


@router.put("/menu-config", summary="更新菜单配置")
async def update_menu_config(config_data: dict, db: Session = Depends(get_db)):
    """@Function: 更新菜单显示配置"""
    service = SystemService(db)
    service.update_menu_config(config_data)
    return {"code": 0, "message": "菜单配置已更新"}
