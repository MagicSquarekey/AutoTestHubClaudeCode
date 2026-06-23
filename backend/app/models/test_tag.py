# -*- coding: utf-8 -*-
"""
标签管理数据模型 / Tag management model
@Function: 定义测试标签表结构，支持用例多维度分类 / Define test tag table for multi-dimensional case classification
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.models.database import Base


class TestTag(Base):
    """测试标签表 / Test tag table"""
    __tablename__ = "test_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)        # 主键
    name = Column(String(50), nullable=False, unique=True)             # 标签名称
    color = Column(String(20), default="#409EFF")                      # 标签颜色
    description = Column(String(200), default="")                      # 标签描述
    status = Column(Integer, default=1)                                # 状态：1 启用 0 禁用
    create_time = Column(DateTime, default=datetime.now)               # 创建时间
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "status": self.status,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else "",
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else "",
        }
