# -*- coding: utf-8 -*-
"""
标签管理服务 / Tag management service
@Function: 提供标签的增删改查、统计功能 / Provide CRUD and statistics for tags
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.test_tag import TestTag
from app.models.test_case import TestCase
from app.utils.logger import get_logger


class TagService:
    """标签管理服务类 / Tag management service class"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger("tag_service")

    def get_tag_list(
        self,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """@Function: 获取标签列表（分页）/ Get tag list with pagination"""
        query = self.db.query(TestTag)

        # 关键词搜索 / Keyword search
        if keyword:
            query = query.filter(TestTag.name.contains(keyword))

        # 状态筛选 / Status filter
        if status is not None:
            query = query.filter(TestTag.status == status)

        # 统计总数 / Count total
        total = query.count()

        # 分页查询 / Paginated query
        tags = query.order_by(TestTag.id.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        # 获取每个标签的使用次数 / Get usage count for each tag
        result = []
        for tag in tags:
            usage_count = self._count_tag_usage(tag.name)
            tag_dict = tag.to_dict()
            tag_dict["usage_count"] = usage_count
            result.append(tag_dict)

        return {
            "list": result,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_all_tags(self) -> List[dict]:
        """@Function: 获取所有启用的标签 / Get all active tags"""
        tags = self.db.query(TestTag).filter(
            TestTag.status == 1
        ).order_by(TestTag.name).all()
        return [t.to_dict() for t in tags]

    def get_tag_by_id(self, tag_id: int) -> Optional[dict]:
        """@Function: 根据ID获取标签详情 / Get tag by ID"""
        tag = self.db.query(TestTag).filter(TestTag.id == tag_id).first()
        if not tag:
            return None
        tag_dict = tag.to_dict()
        tag_dict["usage_count"] = self._count_tag_usage(tag.name)
        return tag_dict

    def create_tag(self, data: dict) -> dict:
        """@Function: 创建标签 / Create tag"""
        # 检查名称唯一性 / Check name uniqueness
        existing = self.db.query(TestTag).filter(TestTag.name == data["name"]).first()
        if existing:
            raise ValueError(f"标签名称 '{data['name']}' 已存在")

        tag = TestTag(
            name=data["name"],
            color=data.get("color", "#409EFF"),
            description=data.get("description", ""),
            status=data.get("status", 1),
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        self.logger.info(f"创建标签成功 / Tag created: {tag.name}")
        return tag.to_dict()

    def update_tag(self, tag_id: int, data: dict) -> dict:
        """@Function: 更新标签 / Update tag"""
        tag = self.db.query(TestTag).filter(TestTag.id == tag_id).first()
        if not tag:
            raise ValueError("标签不存在")

        # 检查名称唯一性（排除自身）/ Check name uniqueness (exclude self)
        if "name" in data and data["name"] != tag.name:
            existing = self.db.query(TestTag).filter(
                TestTag.name == data["name"],
                TestTag.id != tag_id,
            ).first()
            if existing:
                raise ValueError(f"标签名称 '{data['name']}' 已存在")

            # 同步更新用例表中的标签名 / Sync update tag name in test_case
            old_name = tag.name
            new_name = data["name"]
            self._update_tag_in_cases(old_name, new_name)

        # 更新字段 / Update fields
        for key, value in data.items():
            if hasattr(tag, key):
                setattr(tag, key, value)

        self.db.commit()
        self.logger.info(f"更新标签成功 / Tag updated: {tag.name}")
        return tag.to_dict()

    def delete_tag(self, tag_id: int) -> bool:
        """@Function: 删除标签 / Delete tag"""
        tag = self.db.query(TestTag).filter(TestTag.id == tag_id).first()
        if not tag:
            raise ValueError("标签不存在")

        # 检查是否有关联用例 / Check associated cases
        usage_count = self._count_tag_usage(tag.name)
        if usage_count > 0:
            raise ValueError(f"该标签被 {usage_count} 个用例使用，请先移除用例中的该标签")

        self.db.delete(tag)
        self.db.commit()
        self.logger.info(f"删除标签成功 / Tag deleted: {tag.name}")
        return True

    def get_tag_stats(self) -> List[dict]:
        """@Function: 获取标签统计信息 / Get tag statistics"""
        tags = self.db.query(TestTag).filter(TestTag.status == 1).all()
        result = []
        for tag in tags:
            usage_count = self._count_tag_usage(tag.name)
            result.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "usage_count": usage_count,
            })
        return result

    def _count_tag_usage(self, tag_name: str) -> int:
        """@Function: 统计标签使用次数 / Count tag usage"""
        cases = self.db.query(TestCase.tags).all()
        count = 0
        for (tags_str,) in cases:
            if tags_str:
                tag_list = [t.strip() for t in tags_str.split(",")]
                if tag_name in tag_list:
                    count += 1
        return count

    def _update_tag_in_cases(self, old_name: str, new_name: str):
        """@Function: 更新用例表中的标签名 / Update tag name in test_case"""
        cases = self.db.query(TestCase).filter(TestCase.tags.contains(old_name)).all()
        for case in cases:
            if case.tags:
                tag_list = [t.strip() for t in case.tags.split(",")]
                tag_list = [new_name if t == old_name else t for t in tag_list]
                case.tags = ",".join(tag_list)
        self.db.commit()
