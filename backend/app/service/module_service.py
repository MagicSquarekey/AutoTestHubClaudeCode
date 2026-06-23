# -*- coding: utf-8 -*-
"""
模块管理服务 / Module management service
@Function: 提供模块的增删改查、统计功能 / Provide CRUD and statistics for modules
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.test_module import TestModule
from app.models.test_case import TestCase
from app.utils.logger import get_logger


class ModuleService:
    """模块管理服务类 / Module management service class"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger("module_service")

    def get_module_list(
        self,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """@Function: 获取模块列表（分页）/ Get module list with pagination"""
        query = self.db.query(TestModule)

        # 关键词搜索 / Keyword search
        if keyword:
            query = query.filter(TestModule.name.contains(keyword))

        # 状态筛选 / Status filter
        if status is not None:
            query = query.filter(TestModule.status == status)

        # 统计总数 / Count total
        total = query.count()

        # 分页查询 / Paginated query
        modules = query.order_by(TestModule.sort_order, TestModule.id).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        # 获取每个模块的用例数 / Get case count for each module
        result = []
        for module in modules:
            case_count = self.db.query(TestCase).filter(TestCase.module == module.name).count()
            module_dict = module.to_dict()
            module_dict["case_count"] = case_count
            result.append(module_dict)

        return {
            "list": result,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_all_modules(self) -> List[dict]:
        """@Function: 获取所有启用的模块 / Get all active modules"""
        modules = self.db.query(TestModule).filter(
            TestModule.status == 1
        ).order_by(TestModule.sort_order).all()
        return [m.to_dict() for m in modules]

    def get_module_by_id(self, module_id: int) -> Optional[dict]:
        """@Function: 根据ID获取模块详情 / Get module by ID"""
        module = self.db.query(TestModule).filter(TestModule.id == module_id).first()
        if not module:
            return None
        module_dict = module.to_dict()
        module_dict["case_count"] = self.db.query(TestCase).filter(TestCase.module == module.name).count()
        return module_dict

    def create_module(self, data: dict) -> dict:
        """@Function: 创建模块 / Create module"""
        # 检查名称唯一性 / Check name uniqueness
        existing = self.db.query(TestModule).filter(TestModule.name == data["name"]).first()
        if existing:
            raise ValueError(f"模块名称 '{data['name']}' 已存在")

        module = TestModule(
            name=data["name"],
            description=data.get("description", ""),
            sort_order=data.get("sort_order", 0),
            status=data.get("status", 1),
        )
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        self.logger.info(f"创建模块成功 / Module created: {module.name}")
        return module.to_dict()

    def update_module(self, module_id: int, data: dict) -> dict:
        """@Function: 更新模块 / Update module"""
        module = self.db.query(TestModule).filter(TestModule.id == module_id).first()
        if not module:
            raise ValueError("模块不存在")

        # 检查名称唯一性（排除自身）/ Check name uniqueness (exclude self)
        if "name" in data and data["name"] != module.name:
            existing = self.db.query(TestModule).filter(
                TestModule.name == data["name"],
                TestModule.id != module_id,
            ).first()
            if existing:
                raise ValueError(f"模块名称 '{data['name']}' 已存在")

            # 同步更新用例表中的模块名 / Sync update module name in test_case
            old_name = module.name
            new_name = data["name"]
            self.db.query(TestCase).filter(TestCase.module == old_name).update({"module": new_name})

        # 更新字段 / Update fields
        for key, value in data.items():
            if hasattr(module, key):
                setattr(module, key, value)

        self.db.commit()
        self.logger.info(f"更新模块成功 / Module updated: {module.name}")
        return module.to_dict()

    def delete_module(self, module_id: int) -> bool:
        """@Function: 删除模块 / Delete module"""
        module = self.db.query(TestModule).filter(TestModule.id == module_id).first()
        if not module:
            raise ValueError("模块不存在")

        # 检查是否有关联用例 / Check associated cases
        case_count = self.db.query(TestCase).filter(TestCase.module == module.name).count()
        if case_count > 0:
            raise ValueError(f"该模块下有 {case_count} 个用例，请先移除用例的模块归属")

        self.db.delete(module)
        self.db.commit()
        self.logger.info(f"删除模块成功 / Module deleted: {module.name}")
        return True

    def get_module_stats(self) -> List[dict]:
        """@Function: 获取模块统计信息 / Get module statistics"""
        modules = self.db.query(TestModule).filter(TestModule.status == 1).all()
        result = []
        for module in modules:
            case_count = self.db.query(TestCase).filter(TestCase.module == module.name).count()
            result.append({
                "id": module.id,
                "name": module.name,
                "case_count": case_count,
            })
        return result
