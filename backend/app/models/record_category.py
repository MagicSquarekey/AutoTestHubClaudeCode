# -*- coding: utf-8 -*-
"""
录制分类数据模型 / Recording category data model
@Function: 定义录制片段分类表结构，支持多级分类 / Define recording category table with multi-level support
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class RecordCategory(Base):
    """录制分类表 / Recording category table"""
    __tablename__ = "record_category"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(Integer, ForeignKey('record_category.id'), nullable=True, comment="父分类ID")
    level = Column(Integer, default=1, comment="层级：1/2/3")
    sort_order = Column(Integer, default=0, comment="排序序号")
    description = Column(String(500), default="", comment="描述")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联子分类
    children = relationship("RecordCategory", backref="parent", remote_side=[id])

    def to_dict(self, include_children=False):
        """@Function: 转换为字典 / Convert to dictionary"""
        result = {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "level": self.level,
            "sort_order": self.sort_order,
            "description": self.description,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
        if include_children and self.children:
            result["children"] = [child.to_dict(include_children=True) for child in sorted(self.children, key=lambda x: x.sort_order)]
        return result

    def to_tree_dict(self):
        """@Function: 转换为树形字典 / Convert to tree dict"""
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "level": self.level,
            "sort_order": self.sort_order,
            "description": self.description,
            "children": [child.to_tree_dict() for child in sorted(self.children, key=lambda x: x.sort_order)] if self.children else [],
        }
