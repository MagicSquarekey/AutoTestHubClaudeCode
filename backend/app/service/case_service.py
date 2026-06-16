# -*- coding: utf-8 -*-
"""
用例管理服务
@Function: 提供测试用例的业务逻辑处理
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
    """用例管理服务类"""

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
        """@Function: 获取用例列表

        Args:
            module: 模块筛选
            tag: 标签筛选
            priority: 优先级筛选
            platform: 平台筛选
            status: 状态筛选
            keyword: 关键词搜索
            page: 页码
            page_size: 每页数量

        Returns:
            包含列表和分页信息的字典
        """
        query = self.db.query(TestCase)

        # 应用筛选条件
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

        # 计算总数
        total = query.count()

        # 分页
        cases = query.order_by(TestCase.update_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "list": [case.to_dict() for case in cases],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_case_by_id(self, case_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 根据ID获取用例

        Args:
            case_id: 用例ID

        Returns:
            用例字典或None
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        return case.to_dict() if case else None

    def create_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建用例

        Args:
            data: 用例数据

        Returns:
            创建的用例字典
        """
        # 处理标签
        if isinstance(data.get("tags"), list):
            data["tags"] = ",".join(data["tags"])

        case = TestCase(**data)
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)

        logger.info(f"创建用例成功: {case.case_name}")
        return case.to_dict()

    def update_case(self, case_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新用例

        Args:
            case_id: 用例ID
            data: 更新数据

        Returns:
            更新后的用例字典或None
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return None

        # 处理标签
        if isinstance(data.get("tags"), list):
            data["tags"] = ",".join(data["tags"])

        # 更新字段
        for key, value in data.items():
            if hasattr(case, key):
                setattr(case, key, value)

        # 版本号+1
        case.version += 1
        case.update_time = datetime.now()

        self.db.commit()
        self.db.refresh(case)

        logger.info(f"更新用例成功: {case.case_name}")
        return case.to_dict()

    def delete_case(self, case_id: int) -> bool:
        """@Function: 删除用例

        Args:
            case_id: 用例ID

        Returns:
            是否删除成功
        """
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return False

        self.db.delete(case)
        self.db.commit()

        logger.info(f"删除用例成功: {case.case_name}")
        return True

    def batch_delete_cases(self, case_ids: List[int]) -> int:
        """@Function: 批量删除用例

        Args:
            case_ids: 用例ID列表

        Returns:
            删除的数量
        """
        count = self.db.query(TestCase).filter(TestCase.id.in_(case_ids)).delete()
        self.db.commit()

        logger.info(f"批量删除用例成功: {count}条")
        return count

    def copy_case(self, case_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 复制用例

        Args:
            case_id: 源用例ID

        Returns:
            复制的用例字典或None
        """
        source = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not source:
            return None

        new_case = TestCase(
            case_name=f"{source.case_name}_副本",
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

        logger.info(f"复制用例成功: {new_case.case_name}")
        return new_case.to_dict()

    def get_case_versions(self, case_id: int) -> List[Dict[str, Any]]:
        """@Function: 获取用例版本历史

        Args:
            case_id: 用例ID

        Returns:
            版本列表
        """
        # 简化实现：返回当前版本信息
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return []

        return [
            {
                "version": case.version,
                "update_time": case.update_time.strftime("%Y-%m-%d %H:%M:%S") if case.update_time else None,
                "description": "当前版本",
            }
        ]

    def rollback_case(self, case_id: int, version: int) -> Optional[Dict[str, Any]]:
        """@Function: 回滚到指定版本

        Args:
            case_id: 用例ID
            version: 目标版本号

        Returns:
            回滚后的用例字典或None
        """
        # 简化实现：实际应存储历史版本
        case = self.db.query(TestCase).filter(TestCase.id == case_id).first()
        if not case:
            return None

        logger.info(f"回滚用例: {case.case_name} 到版本 {version}")
        return case.to_dict()

    def export_cases(self, case_ids: List[int]) -> Dict[str, Any]:
        """@Function: 导出用例

        Args:
            case_ids: 用例ID列表

        Returns:
            导出的用例数据
        """
        cases = self.db.query(TestCase).filter(TestCase.id.in_(case_ids)).all()

        return {
            "version": "1.0",
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(cases),
            "cases": [case.to_dict() for case in cases],
        }

    def import_cases(self, content: bytes) -> Dict[str, Any]:
        """@Function: 导入用例

        Args:
            content: JSON文件内容

        Returns:
            导入结果
        """
        try:
            data = json.loads(content.decode("utf-8"))
            cases_data = data.get("cases", [])

            imported_count = 0
            for case_data in cases_data:
                # 处理标签
                if isinstance(case_data.get("tags"), list):
                    case_data["tags"] = ",".join(case_data["tags"])

                # 移除ID，创建新用例
                case_data.pop("id", None)
                case_data.pop("create_time", None)
                case_data.pop("update_time", None)

                case = TestCase(**case_data)
                self.db.add(case)
                imported_count += 1

            self.db.commit()

            logger.info(f"导入用例成功: {imported_count}条")
            return {"imported_count": imported_count}

        except Exception as e:
            logger.error(f"导入用例失败: {e}")
            raise

    def get_module_list(self) -> List[str]:
        """@Function: 获取所有模块列表

        Returns:
            模块名称列表
        """
        modules = self.db.query(TestCase.module).distinct().all()
        return [m[0] for m in modules if m[0]]

    def get_tag_list(self) -> List[str]:
        """@Function: 获取所有标签列表

        Returns:
            标签名称列表
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
