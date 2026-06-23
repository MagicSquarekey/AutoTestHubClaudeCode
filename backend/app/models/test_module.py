# -*- coding: utf-8 -*-
"""
模块管理数据模型 / Module management model
@Function: 定义测试模块表结构，支持用例分组管理 / Define test module table for case grouping
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.models.database import Base


class TestModule(Base):
    """测试模块表 / Test module table"""
    __tablename__ = "test_module"

    id = Column(Integer, primary_key=True, autoincrement=True)        # 主键
    name = Column(String(100), nullable=False, unique=True)            # 模块名称
    description = Column(String(500), default="")                      # 模块描述
    sort_order = Column(Integer, default=0)                            # 排序序号
    status = Column(Integer, default=1)                                # 状态：1 启用 0 禁用
    create_time = Column(DateTime, default=datetime.now)               # 创建时间
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sort_order": self.sort_order,
            "status": self.status,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else "",
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else "",
        }
