# -*- coding: utf-8 -*-
"""
分类管理服务 / Category management service
@Function: 提供录制片段分类的增删改查、树形结构管理 / Provide CRUD and tree management for recording categories
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.record_category import RecordCategory
from app.models.record_task import RecordTask
from app.utils.logger import get_logger

logger = get_logger("category_service")


class CategoryService:
    """分类管理服务类 / Category management service class"""

    def __init__(self, db: Session):
        self.db = db

    def get_category_tree(self) -> List[Dict[str, Any]]:
        """@Function: 获取分类树 / Get category tree

        Returns:
            树形结构的分类列表
        """
        # 获取所有根分类（parent_id 为 None）
        root_categories = self.db.query(RecordCategory).filter(
            RecordCategory.parent_id.is_(None)
        ).order_by(RecordCategory.sort_order).all()

        return [category.to_tree_dict() for category in root_categories]

    def get_category_list(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """@Function: 获取子分类列表 / Get child category list

        Args:
            parent_id: 父分类ID，None 表示获取根分类

        Returns:
            分类列表
        """
        query = self.db.query(RecordCategory)
        if parent_id is not None:
            query = query.filter(RecordCategory.parent_id == parent_id)
        else:
            query = query.filter(RecordCategory.parent_id.is_(None))

        categories = query.order_by(RecordCategory.sort_order).all()
        return [category.to_dict() for category in categories]

    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 根据ID获取分类 / Get category by ID

        Args:
            category_id: 分类ID

        Returns:
            分类字典或 None
        """
        category = self.db.query(RecordCategory).filter(RecordCategory.id == category_id).first()
        return category.to_dict() if category else None

    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建分类 / Create category

        Args:
            data: 分类数据（name, parent_id, description, sort_order）

        Returns:
            创建的分类字典

        Raises:
            ValueError: 层级超限或父分类不存在
        """
        parent_id = data.get("parent_id")
        level = 1

        # 检查父分类和层级
        if parent_id:
            parent = self.db.query(RecordCategory).filter(RecordCategory.id == parent_id).first()
            if not parent:
                raise ValueError("父分类不存在")
            level = parent.level + 1
            if level > 3:
                raise ValueError("最多支持3级分类")

        category = RecordCategory(
            name=data["name"],
            parent_id=parent_id,
            level=level,
            sort_order=data.get("sort_order", 0),
            description=data.get("description", ""),
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        logger.info(f"创建分类成功: {category.name}")
        return category.to_dict()

    def update_category(self, category_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 更新分类 / Update category

        Args:
            category_id: 分类ID
            data: 更新数据

        Returns:
            更新后的分类字典

        Raises:
            ValueError: 分类不存在
        """
        category = self.db.query(RecordCategory).filter(RecordCategory.id == category_id).first()
        if not category:
            raise ValueError("分类不存在")

        # 更新字段
        for key, value in data.items():
            if hasattr(category, key) and key not in ('id', 'create_time', 'level', 'parent_id'):
                setattr(category, key, value)

        self.db.commit()
        self.db.refresh(category)

        logger.info(f"更新分类成功: {category.name}")
        return category.to_dict()

    def delete_category(self, category_id: int) -> bool:
        """@Function: 删除分类 / Delete category

        Args:
            category_id: 分类ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 分类不存在或有子分类
        """
        category = self.db.query(RecordCategory).filter(RecordCategory.id == category_id).first()
        if not category:
            raise ValueError("分类不存在")

        # 检查是否有子分类
        children = self.db.query(RecordCategory).filter(RecordCategory.parent_id == category_id).all()
        if children:
            # 将子分类移到父分类
            for child in children:
                child.parent_id = category.parent_id
                child.level = category.level
            self.db.commit()

        # 将该分类下的录制任务移到未分类
        self.db.query(RecordTask).filter(RecordTask.category_id == category_id).update(
            {"category_id": None}
        )

        self.db.delete(category)
        self.db.commit()

        logger.info(f"删除分类成功: {category.name}")
        return True

    def move_category(self, category_id: int, new_parent_id: Optional[int]) -> Dict[str, Any]:
        """@Function: 移动分类 / Move category

        Args:
            category_id: 分类ID
            new_parent_id: 新父分类ID（None 表示移到根级别）

        Returns:
            更新后的分类字典

        Raises:
            ValueError: 分类不存在或层级超限
        """
        category = self.db.query(RecordCategory).filter(RecordCategory.id == category_id).first()
        if not category:
            raise ValueError("分类不存在")

        # 计算新层级
        new_level = 1
        if new_parent_id:
            new_parent = self.db.query(RecordCategory).filter(RecordCategory.id == new_parent_id).first()
            if not new_parent:
                raise ValueError("目标父分类不存在")
            new_level = new_parent.level + 1

        # 检查层级限制
        if new_level > 3:
            raise ValueError("最多支持3级分类")

        # 更新分类及其所有子分类的层级
        self._update_category_level(category, new_level, new_parent_id)

        self.db.commit()
        self.db.refresh(category)

        logger.info(f"移动分类成功: {category.name}")
        return category.to_dict()

    def _update_category_level(self, category: RecordCategory, new_level: int, new_parent_id: Optional[int]):
        """@Function: 递归更新分类层级 / Recursively update category level"""
        category.level = new_level
        category.parent_id = new_parent_id

        children = self.db.query(RecordCategory).filter(RecordCategory.parent_id == category.id).all()
        for child in children:
            self._update_category_level(child, new_level + 1, category.id)

    def get_category_stats(self) -> List[Dict[str, Any]]:
        """@Function: 获取分类统计 / Get category statistics

        Returns:
            分类统计列表
        """
        categories = self.db.query(RecordCategory).all()
        result = []
        for cat in categories:
            task_count = self.db.query(RecordTask).filter(RecordTask.category_id == cat.id).count()
            result.append({
                "id": cat.id,
                "name": cat.name,
                "level": cat.level,
                "task_count": task_count,
            })
        return result
