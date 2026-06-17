# -*- coding: utf-8 -*-
"""
元素管理 API / Element management API
@Function: 提供测试元素的 CRUD、定位符管理、健康巡检接口 / Provide CRUD, locator management, health check endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.element_service import ElementService

router = APIRouter()


class LocatorItem(BaseModel):
    """定位符项"""
    platform: str = "web"
    locate_type: str = "xpath"  # xpath/id/css/accessibility/ocr/image/coordinate
    locate_value: str = ""
    priority: int = 1


class ElementCreate(BaseModel):
    """元素创建请求"""
    elem_name: str
    page_name: str = ""
    module: str = ""
    locators: List[LocatorItem] = []


class ElementUpdate(BaseModel):
    """元素更新请求"""
    elem_name: Optional[str] = None
    page_name: Optional[str] = None
    module: Optional[str] = None
    locators: Optional[List[LocatorItem]] = None


@router.get("/list", summary="获取元素列表")
async def get_element_list(
    module: Optional[str] = None,
    page_name: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取元素列表，支持筛选和分页"""
    service = ElementService(db)
    result = service.get_element_list(
        module=module,
        page_name=page_name,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return {"code": 0, "data": result}


@router.get("/{elem_id}", summary="获取元素详情")
async def get_element(elem_id: int, db: Session = Depends(get_db)):
    """@Function: 根据ID获取元素详情"""
    service = ElementService(db)
    element = service.get_element_by_id(elem_id)
    if not element:
        raise HTTPException(status_code=404, detail="元素不存在")
    return {"code": 0, "data": element}


@router.post("/create", summary="创建元素")
async def create_element(element: ElementCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的测试元素"""
    service = ElementService(db)
    data = element.dict()
    data["locators"] = [loc.dict() for loc in element.locators]
    result = service.create_element(data)
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/{elem_id}", summary="更新元素")
async def update_element(elem_id: int, element: ElementUpdate, db: Session = Depends(get_db)):
    """@Function: 更新测试元素"""
    service = ElementService(db)
    data = element.dict(exclude_unset=True)
    if element.locators is not None:
        data["locators"] = [loc.dict() for loc in element.locators]
    result = service.update_element(elem_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="元素不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/{elem_id}", summary="删除元素")
async def delete_element(elem_id: int, db: Session = Depends(get_db)):
    """@Function: 删除测试元素"""
    service = ElementService(db)
    success = service.delete_element(elem_id)
    if not success:
        raise HTTPException(status_code=404, detail="元素不存在")
    return {"code": 0, "message": "删除成功"}


@router.post("/batch-delete", summary="批量删除元素")
async def batch_delete_elements(elem_ids: List[int], db: Session = Depends(get_db)):
    """@Function: 批量删除测试元素"""
    service = ElementService(db)
    count = service.batch_delete_elements(elem_ids)
    return {"code": 0, "data": {"deleted_count": count}, "message": f"成功删除{count}个元素"}


@router.post("/health-check", summary="元素健康巡检")
async def health_check(
    elem_ids: Optional[List[int]] = None,
    platform: str = "web",
    db: Session = Depends(get_db),
):
    """@Function: 执行元素健康巡检"""
    service = ElementService(db)
    result = service.health_check(elem_ids, platform)
    return {"code": 0, "data": result}


@router.get("/pages/list", summary="获取页面列表")
async def get_page_list(db: Session = Depends(get_db)):
    """@Function: 获取所有页面列表"""
    service = ElementService(db)
    pages = service.get_page_list()
    return {"code": 0, "data": pages}


@router.get("/modules/list", summary="获取元素模块列表")
async def get_element_module_list(db: Session = Depends(get_db)):
    """@Function: 获取元素模块列表"""
    service = ElementService(db)
    modules = service.get_module_list()
    return {"code": 0, "data": modules}


@router.post("/export", summary="导出元素")
async def export_elements(elem_ids: List[int], db: Session = Depends(get_db)):
    """@Function: 导出元素数据"""
    service = ElementService(db)
    data = service.export_elements(elem_ids)
    return {"code": 0, "data": data}


@router.post("/import", summary="导入元素")
async def import_elements(elements: List[Dict[str, Any]], db: Session = Depends(get_db)):
    """@Function: 批量导入元素"""
    service = ElementService(db)
    result = service.import_elements(elements)
    return {"code": 0, "data": result, "message": f"成功导入{result['imported_count']}个元素"}


@router.post("/batch-sync", summary="批量同步元素")
async def batch_sync(
    page_name: str,
    platform: str = "web",
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 从页面批量抓取并同步元素"""
    service = ElementService(db)
    result = service.batch_sync(page_name, platform, device_id)
    return {"code": 0, "data": result}
