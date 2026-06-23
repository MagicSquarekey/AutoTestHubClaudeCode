# -*- coding: utf-8 -*-
"""
标签管理 API / Tag management API
@Function: 提供标签的增删改查接口 / Provide CRUD endpoints for tags
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.tag_service import TagService

router = APIRouter()


class TagCreate(BaseModel):
    """标签创建请求"""
    name: str
    color: str = "#409EFF"
    description: str = ""
    status: int = 1


class TagUpdate(BaseModel):
    """标签更新请求"""
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


@router.get("/list", summary="获取标签列表")
async def get_tag_list(
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取标签列表，支持筛选和分页"""
    service = TagService(db)
    result = service.get_tag_list(
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
    )
    return {"code": 0, "data": result}


@router.get("/all", summary="获取所有标签")
async def get_all_tags(db: Session = Depends(get_db)):
    """@Function: 获取所有启用的标签（供下拉选择用）"""
    service = TagService(db)
    result = service.get_all_tags()
    return {"code": 0, "data": result}


@router.get("/stats", summary="获取标签统计")
async def get_tag_stats(db: Session = Depends(get_db)):
    """@Function: 获取标签统计信息（包含使用次数）"""
    service = TagService(db)
    result = service.get_tag_stats()
    return {"code": 0, "data": result}


@router.get("/{tag_id}", summary="获取标签详情")
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """@Function: 根据ID获取标签详情"""
    service = TagService(db)
    tag = service.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {"code": 0, "data": tag}


@router.post("/create", summary="创建标签")
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的标签"""
    service = TagService(db)
    try:
        result = service.create_tag(tag.dict())
        return {"code": 0, "data": result, "message": "创建成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.put("/{tag_id}", summary="更新标签")
async def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """@Function: 更新标签信息"""
    service = TagService(db)
    try:
        result = service.update_tag(tag_id, tag.dict(exclude_unset=True))
        return {"code": 0, "data": result, "message": "更新成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}


@router.delete("/{tag_id}", summary="删除标签")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """@Function: 删除标签"""
    service = TagService(db)
    try:
        service.delete_tag(tag_id)
        return {"code": 0, "message": "删除成功"}
    except ValueError as e:
        return {"code": 1, "message": str(e)}
