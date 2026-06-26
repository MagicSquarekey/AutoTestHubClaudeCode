# -*- coding: utf-8 -*-
"""
用例管理服务 / Test case management service
@Function: 提供测试用例的业务逻辑处理 / Provide business logic for test cases
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.test_case import TestCase
from app.utils.logger import get_logger

logger = get_logger("case_service")


class CaseService:
    """用例管理服务类 / Test case management service class"""

    def __init__(self, db: Session):
        self.db = db

    def get_case_list(
        self,
        module: Optional[str] = None,
        tag: Optional[str] = None,
        priority: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """@Function: 获取用例列表 / Get case list with filters and pagination

        Args:
            module: 模块筛选 / Module filter
            tag: 标签筛选 / Tag filter
            priority: 优先级筛选 / Priority filter
            platform: 平台筛选 / Platform filter
            status: 状态筛选 / Status filter
            keyword: 关键词搜索 / Keyword search
            page: 页码 / Page number
            page_size: 每页数量 / Page size

        Returns:
            包含列表和分页信息的字典 / Dict with list and pagination info
        """
        query = self.db.query(TestCase)

        # 应用筛选条件 / Apply filters
        if module:
            query = query.filter(TestCase.module == module)
        if tag:
            query = query.filter(TestCase.tags.contains(tag))
        if priority:
            query = query.filter(TestCase.priority == priority)
        if platform:
            query = query.filter(TestCase.platform == platform)
        if status is not None:
            query = query.filter(TestCase.status == status)
        if keyword:
            query = query.filter(
                or_(
                    TestCase.case_name.contains(keyword),
                    TestCase.description.contains(keyword),
                )
            )

        # 计算总数 / Count total
        total = query.count()

        # 分页查询 / Paginate query
        cases = query.order_by(TestCase.update_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "list": [case.to_dict() for case in cases],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_case_by_id(self, case_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 根据 ID 获取用例 / Get case by ID

        Args:
            case_id: 用例 ID / Case ID

        Returns:
            用例字典或 None / Case dict or None
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        return case.to_dict() if case else None

    def _check_name_unique(self, case_name: str, exclude_id: Optional[int] = None) -> None:
        """@Function: 检查用例名称是否已存在 / Check if case name already exists

        Args:
            case_name: 用例名称 / Case name
            exclude_id: 排除的用例 ID（更新时使用）/ Case ID to exclude (for update)

        Raises:
            ValueError: 名称已存在时抛出 / Raised when name already exists
        """
        query = self.db.query(TestCase).filter(TestCase.case_name == case_name)
        if exclude_id is not None:
            query = query.filter(TestCase.id != exclude_id)
        if query.first():
            raise ValueError(f"用例名称已存在: {case_name}")

    def create_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建用例 / Create a new case

        Args:
            data: 用例数据 / Case data

        Returns:
            创建的用例字典 / Created case dict

        Raises:
            ValueError: 名称已存在 / Name already exists
        """
        # 检查名称唯一性 / Check name uniqueness
        self._check_name_unique(data.get("case_name", ""))

        # 处理标签 / Process tags
        if isinstance(data.get("tags"), list):
            data["tags"] = ",".join(data["tags"])

        case = TestCase(**data)
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)

        logger.info(f"创建用例成功 / Case created: {case.case_name}")
        return case.to_dict()

    def update_case(self, case_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新用例 / Update an existing case

        Args:
            case_id: 用例 ID / Case ID
            data: 更新数据 / Update data

        Returns:
            更新后的用例字典或 None / Updated case dict or None

        Raises:
            ValueError: 名称已存在 / Name already exists
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return None

        # 如果修改了名称，检查唯一性 / Check uniqueness if name is changed
        if "case_name" in data and data["case_name"] != case.case_name:
            self._check_name_unique(data["case_name"], exclude_id=case_id)

        # 处理标签 / Process tags
        if isinstance(data.get("tags"), list):
            data["tags"] = ",".join(data["tags"])

        # 更新字段 / Update fields
        for key, value in data.items():
            if hasattr(case, key):
                setattr(case, key, value)

        # 版本号 +1 / Increment version
        case.version += 1
        case.update_time = datetime.now()

        self.db.commit()
        self.db.refresh(case)

        logger.info(f"更新用例成功 / Case updated: {case.case_name}")
        return case.to_dict()

    def delete_case(self, case_id: int) -> bool:
        """@Function: 删除用例 / Delete a case

        Args:
            case_id: 用例 ID / Case ID

        Returns:
            是否删除成功 / Whether deletion succeeded
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return False

        self.db.delete(case)
        self.db.commit()

        logger.info(f"删除用例成功 / Case deleted: {case.case_name}")
        return True

    def batch_delete_cases(self, case_ids: List[int]) -> int:
        """@Function: 批量删除用例 / Batch delete cases

        Args:
            case_ids: 用例 ID 列表 / Case ID list

        Returns:
            删除的数量 / Number of deleted cases
        """
        count = self.db.query(TestCase).filter(TestCase.id.in_(case_ids)).delete()
        self.db.commit()

        logger.info(f"批量删除用例成功 / Batch deleted: {count} cases")
        return count

    def copy_case(self, case_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 复制用例 / Copy a case

        Args:
            case_id: 源用例 ID / Source case ID

        Returns:
            复制的用例字典或 None / Copied case dict or None
        """
        source = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not source:
            return None

        # 生成唯一副本名称 / Generate unique copy name
        base_name = f"{source.case_name}_副本"
        copy_name = base_name
        counter = 2
        while self.db.query(TestCase).filter(TestCase.case_name == copy_name).first():
            copy_name = f"{base_name}{counter}"
            counter += 1

        new_case = TestCase(
            case_name=copy_name,
            module=source.module,
            tags=source.tags,
            priority=source.priority,
            description=source.description,
            steps=source.steps,
            platform=source.platform,
            status=1,
        )

        self.db.add(new_case)
        self.db.commit()
        self.db.refresh(new_case)

        logger.info(f"复制用例成功 / Case copied: {new_case.case_name}")
        return new_case.to_dict()

    def get_case_versions(self, case_id: int) -> List[Dict[str, Any]]:
        """@Function: 获取用例版本历史 / Get case version history

        Args:
            case_id: 用例 ID / Case ID

        Returns:
            版本列表 / Version list
        """
        # 简化实现：返回当前版本信息 / Simplified: return current version info
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return []

        return [
            {
                "version": case.version,
                "update_time": case.update_time.strftime("%Y-%m-%d %H:%M:%S") if case.update_time else None,
                "description": "当前版本 / Current version",
            }
        ]

    def rollback_case(self, case_id: int, version: int) -> Optional[Dict[str, Any]]:
        """@Function: 回滚到指定版本 / Rollback to specified version

        Args:
            case_id: 用例 ID / Case ID
            version: 目标版本号 / Target version number

        Returns:
            回滚后的用例字典或 None / Rolled back case dict or None
        """
        # 简化实现：实际应存储历史版本 / Simplified: should store history in production
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return None

        logger.info(f"回滚用例 / Rollback case: {case.case_name} to version {version}")
        return case.to_dict()

    def export_cases(self, case_ids: List[int]) -> Dict[str, Any]:
        """@Function: 导出用例 / Export cases

        Args:
            case_ids: 用例 ID 列表 / Case ID list

        Returns:
            导出的用例数据 / Exported case data
        """
        cases = self.db.query(TestCase).filter(TestCase.id.in_(case_ids)).all()

        return {
            "version": "1.0",
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(cases),
            "cases": [case.to_dict() for case in cases],
        }

    def import_cases(self, content: bytes) -> Dict[str, Any]:
        """@Function: 导入用例 / Import cases

        Args:
            content: JSON 文件内容 / JSON file content

        Returns:
            导入结果 / Import result
        """
        try:
            data = json.loads(content.decode("utf-8"))
            cases_data = data.get("cases", [])

            imported_count = 0
            for case_data in cases_data:
                # 处理标签 / Process tags
                if isinstance(case_data.get("tags"), list):
                    case_data["tags"] = ",".join(case_data["tags"])

                # 移除 ID，创建新用例 / Remove ID, create new case
                case_data.pop("id", None)
                case_data.pop("create_time", None)
                case_data.pop("update_time", None)

                case = TestCase(**case_data)
                self.db.add(case)
                imported_count += 1

            self.db.commit()

            logger.info(f"导入用例成功 / Cases imported: {imported_count}")
            return {"imported_count": imported_count}

        except Exception as e:
            logger.error(f"导入用例失败 / Import failed: {e}")
            raise

    def get_module_list(self) -> List[str]:
        """@Function: 获取所有模块列表 / Get all module names

        Returns:
            模块名称列表 / Module name list
        """
        modules = self.db.query(TestCase.module).distinct().all()
        return [m[0] for m in modules if m[0]]

    def get_tag_list(self) -> List[str]:
        """@Function: 获取所有标签列表 / Get all tag names

        Returns:
            标签名称列表 / Tag name list
        """
        cases = self.db.query(TestCase.tags).all()
        tags = set()
        for case in cases:
            if case[0]:
                for tag in case[0].split(","):
                    tag = tag.strip()
                    if tag:
                        tags.add(tag)
        return sorted(list(tags))

    def update_case_sort_order(self, sort_items: List[Dict[str, int]]) -> int:
        """@Function: 批量更新用例排序顺序 / Batch update case sort order

        Args:
            sort_items: 排序项列表 [{"id": 1, "sort_order": 0}, ...]

        Returns:
            更新的数量 / Number of updated cases
        """
        updated_count = 0
        for item in sort_items:
            case_id = item.get("id") if isinstance(item, dict) else item.id
            sort_order = item.get("sort_order") if isinstance(item, dict) else item.sort_order

            case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
            if case:
                case.sort_order = sort_order
                case.update_time = datetime.now()
                updated_count += 1

        self.db.commit()
        logger.info(f"更新用例排序成功 / Case sort order updated: {updated_count} cases")
        return updated_count

    def get_sorted_case_list(
        self,
        module: Optional[str] = None,
        tag: Optional[str] = None,
        priority: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """@Function: 获取按 sort_order 排序的用例列表 / Get case list sorted by sort_order

        Args:
            module: 模块筛选 / Module filter
            tag: 标签筛选 / Tag filter
            priority: 优先级筛选 / Priority filter
            platform: 平台筛选 / Platform filter
            status: 状态筛选 / Status filter
            keyword: 关键词搜索 / Keyword search

        Returns:
            用例列表 / Case list
        """
        query = self.db.query(TestCase)

        # 应用筛选条件 / Apply filters
        if module:
            query = query.filter(TestCase.module == module)
        if tag:
            query = query.filter(TestCase.tags.contains(tag))
        if priority:
            query = query.filter(TestCase.priority == priority)
        if platform:
            query = query.filter(TestCase.platform == platform)
        if status is not None:
            query = query.filter(TestCase.status == status)
        if keyword:
            query = query.filter(
                or_(
                    TestCase.case_name.contains(keyword),
                    TestCase.description.contains(keyword),
                )
            )

        # 按 sort_order 升序排序，然后按 id 升序排序
        cases = query.order_by(TestCase.sort_order.asc(), TestCase.id.asc()).all()

        return [case.to_dict() for case in cases]
