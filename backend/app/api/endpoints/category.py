# -*- coding: utf-8 -*-
"""
分类管理 API / Category management API
@Function: 提供录制片段分类的增删改查接口 / Provide CRUD endpoints for recording categories
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.category_service import CategoryService

router = APIRouter()


class CategoryCreate(BaseModel):
    """分类创建请求"""
    name: str
    parent_id: Optional[int] = None
    description: str = ""
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """分类更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryMove(BaseModel):
    """分类移动请求"""
    parent_id: Optional[int] = None


@router.get("/tree", summary="获取分类树")
async def get_category_tree(db: Session = Depends(get_db)):
    """@Function: 获取分类树形结构"""
    service = CategoryService(db)
    result = service.get_category_tree()
    return {"code": 0, "data": result}


@router.get("/list", summary="获取分类列表")
async def get_category_list(
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """@Function: 获取子分类列表"""
    service = CategoryService(db)
    result = service.get_category_list(parent_id)
    return {"code": 0, "data": result}


@router.get("/stats", summary="获取分类统计")
async def get_category_stats(db: Session = Depends(get_db)):
    """@Function: 获取分类统计信息"""
    service = CategoryService(db)
    result = service.get_category_stats()
    return {"code": 0, "data": result}


@router.get("/{category_id}", summary="获取分类详情")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """@Function: 根据ID获取分类详情"""
    service = CategoryService(db)
    category = service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"code": 0, "data": category}


@router.post("/create", summary="创建分类")
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的分类"""
    service = CategoryService(db)
    try:
        result = service.create_category(category.dict())
        return {"code": 0, "data": result, "message": "创建成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.put("/{category_id}", summary="更新分类")
async def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    """@Function: 更新分类信息"""
    service = CategoryService(db)
    try:
        result = service.update_category(category_id, category.dict(exclude_unset=True))
        return {"code": 0, "data": result, "message": "更新成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.delete("/{category_id}", summary="删除分类")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """@Function: 删除分类"""
    service = CategoryService(db)
    try:
        service.delete_category(category_id)
        return {"code": 0, "message": "删除成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.post("/{category_id}/move", summary="移动分类")
async def move_category(category_id: int, move: CategoryMove, db: Session = Depends(get_db)):
    """@Function: 移动分类到新的父分类"""
    service = CategoryService(db)
    try:
        result = service.move_category(category_id, move.parent_id)
        return {"code": 0, "data": result, "message": "移动成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}
