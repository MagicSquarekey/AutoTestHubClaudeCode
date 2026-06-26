# -*- coding: utf-8 -*-
"""
用例管理 API / Test case management API
@Function: 提供测试用例的 CRUD、导入导出、版本管理接口 / Provide CRUD, import/export, version management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.service.case_service import CaseService

router = APIRouter()


class CaseCreate(BaseModel):
    """用例创建请求"""
    case_name: str
    module: str = ""
    tags: List[str] = []
    priority: str = "P0"
    description: str = ""
    steps: str = "[]"
    setup_steps: str = "[]"
    teardown_steps: str = "[]"
    platform: str = "web"


class CaseUpdate(BaseModel):
    """用例更新请求"""
    case_name: Optional[str] = None
    module: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[str] = None
    setup_steps: Optional[str] = None
    teardown_steps: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[int] = None
    sort_order: Optional[int] = None


class CaseSortItem(BaseModel):
    """用例排序项"""
    id: int
    sort_order: int


class CaseSortRequest(BaseModel):
    """用例排序请求"""
    cases: List[CaseSortItem]


class CaseResponse(BaseModel):
    """用例响应"""
    id: int
    case_name: str
    module: str
    tags: List[str]
    priority: str
    description: str
    steps: str
    setup_steps: str
    teardown_steps: str
    version: int
    status: int
    platform: str
    create_time: str
    update_time: str


@router.get("/list", summary="获取用例列表")
async def get_case_list(
    module: Optional[str] = None,
    tag: Optional[str] = None,
    priority: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """@Function: 获取用例列表，支持筛选和分页"""
    service = CaseService(db)
    result = service.get_case_list(
        module=module,
        tag=tag,
        priority=priority,
        platform=platform,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return {"code": 0, "data": result}


@router.get("/{case_id}", summary="获取用例详情")
async def get_case(case_id: int, db: Session = Depends(get_db)):
    """@Function: 根据ID获取用例详情"""
    service = CaseService(db)
    case = service.get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"code": 0, "data": case}


@router.post("/create", summary="创建用例")
async def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    """@Function: 创建新的测试用例"""
    service = CaseService(db)
    try:
        result = service.create_case(case.dict())
    except ValueError as e:
        return {"code": 1, "message": str(e)}
    return {"code": 0, "data": result, "message": "创建成功"}


@router.put("/{case_id}", summary="更新用例")
async def update_case(case_id: int, case: CaseUpdate, db: Session = Depends(get_db)):
    """@Function: 更新测试用例"""
    service = CaseService(db)
    try:
        result = service.update_case(case_id, case.dict(exclude_unset=True))
    except ValueError as e:
        return {"code": 1, "message": str(e)}
    if not result:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/{case_id}", summary="删除用例")
async def delete_case(case_id: int, db: Session = Depends(get_db)):
    """@Function: 删除测试用例"""
    service = CaseService(db)
    success = service.delete_case(case_id)
    if not success:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"code": 0, "message": "删除成功"}


@router.post("/batch-delete", summary="批量删除用例")
async def batch_delete_cases(case_ids: List[int], db: Session = Depends(get_db)):
    """@Function: 批量删除测试用例"""
    service = CaseService(db)
    count = service.batch_delete_cases(case_ids)
    return {"code": 0, "data": {"deleted_count": count}, "message": f"成功删除{count}条用例"}


@router.post("/copy/{case_id}", summary="复制用例")
async def copy_case(case_id: int, db: Session = Depends(get_db)):
    """@Function: 复制测试用例"""
    service = CaseService(db)
    result = service.copy_case(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"code": 0, "data": result, "message": "复制成功"}


@router.get("/{case_id}/versions", summary="获取用例版本历史")
async def get_case_versions(case_id: int, db: Session = Depends(get_db)):
    """@Function: 获取用例的版本历史"""
    service = CaseService(db)
    versions = service.get_case_versions(case_id)
    return {"code": 0, "data": versions}


@router.post("/{case_id}/rollback/{version}", summary="回滚到指定版本")
async def rollback_case(case_id: int, version: int, db: Session = Depends(get_db)):
    """@Function: 将用例回滚到指定版本"""
    service = CaseService(db)
    result = service.rollback_case(case_id, version)
    if not result:
        raise HTTPException(status_code=404, detail="版本不存在")
    return {"code": 0, "data": result, "message": "回滚成功"}


@router.post("/export", summary="导出用例")
async def export_cases(case_ids: List[int], db: Session = Depends(get_db)):
    """@Function: 导出用例为JSON格式"""
    service = CaseService(db)
    data = service.export_cases(case_ids)
    return {"code": 0, "data": data}


@router.post("/import", summary="导入用例")
async def import_cases(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """@Function: 从JSON文件导入用例"""
    service = CaseService(db)
    content = await file.read()
    result = service.import_cases(content)
    return {"code": 0, "data": result, "message": f"成功导入{result['imported_count']}条用例"}


@router.get("/modules/list", summary="获取模块列表")
async def get_module_list(db: Session = Depends(get_db)):
    """@Function: 获取所有模块列表"""
    service = CaseService(db)
    modules = service.get_module_list()
    return {"code": 0, "data": modules}


@router.get("/tags/list", summary="获取标签列表")
async def get_tag_list(db: Session = Depends(get_db)):
    """@Function: 获取所有标签列表"""
    service = CaseService(db)
    tags = service.get_tag_list()
    return {"code": 0, "data": tags}


@router.post("/sort", summary="批量更新用例排序")
async def sort_cases(sort_data: CaseSortRequest, db: Session = Depends(get_db)):
    """@Function: 批量更新用例的排序顺序"""
    service = CaseService(db)
    try:
        count = service.update_case_sort_order(sort_data.cases)
        return {"code": 0, "data": {"updated_count": count}, "message": f"成功更新{count}条用例的排序"}
    except Exception as e:
        return {"code": 1, "message": f"排序更新失败: {str(e)}"}


@router.get("/sorted/list", summary="获取排序后的用例列表")
async def get_sorted_case_list(
    module: Optional[str] = None,
    tag: Optional[str] = None,
    priority: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[int] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """@Function: 获取按 sort_order 排序的用例列表（不分页）"""
    service = CaseService(db)
    cases = service.get_sorted_case_list(
        module=module,
        tag=tag,
        priority=priority,
        platform=platform,
        status=status,
        keyword=keyword,
    )
    return {"code": 0, "data": cases}
