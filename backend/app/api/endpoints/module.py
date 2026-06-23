# -*- coding: utf-8 -*-
"""
模块管理 API / Module management API
@Function: 提供模块的增删改查接口 / Provide CRUD endpoints for modules
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.module_service import ModuleService

router = APIRouter()


class ModuleCreate(BaseModel):
    """模块创建请求"""
    name: str
    description: str = ""
    sort_order: int = 0
    status: int = 1


class ModuleUpdate(BaseModel):
    """模块更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


@router.get("/list", summary="获取模块列表")
async def get_module_list(
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取模块列表，支持筛选和分页"""
    service = ModuleService(db)
    result = service.get_module_list(
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
    )
    return {"code": 0, "data": result}


@router.get("/all", summary="获取所有模块")
async def get_all_modules(db: Session = Depends(get_db)):
    """@Function: 获取所有启用的模块（供下拉选择用）"""
    service = ModuleService(db)
    result = service.get_all_modules()
    return {"code": 0, "data": result}


@router.get("/stats", summary="获取模块统计")
async def get_module_stats(db: Session = Depends(get_db)):
    """@Function: 获取模块统计信息（包含用例数量）"""
    service = ModuleService(db)
    result = service.get_module_stats()
    return {"code": 0, "data": result}


@router.get("/{module_id}", summary="获取模块详情")
async def get_module(module_id: int, db: Session = Depends(get_db)):
    """@Function: 根据ID获取模块详情"""
    service = ModuleService(db)
    module = service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return {"code": 0, "data": module}


@router.post("/create", summary="创建模块")
async def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的模块"""
    service = ModuleService(db)
    try:
        result = service.create_module(module.dict())
        return {"code": 0, "data": result, "message": "创建成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.put("/{module_id}", summary="更新模块")
async def update_module(module_id: int, module: ModuleUpdate, db: Session = Depends(get_db)):
    """@Function: 更新模块信息"""
    service = ModuleService(db)
    try:
        result = service.update_module(module_id, module.dict(exclude_unset=True))
        return {"code": 0, "data": result, "message": "更新成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.delete("/{module_id}", summary="删除模块")
async def delete_module(module_id: int, db: Session = Depends(get_db)):
    """@Function: 删除模块"""
    service = ModuleService(db)
    try:
        service.delete_module(module_id)
        return {"code": 0, "message": "删除成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}
