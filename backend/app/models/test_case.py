# -*- coding: utf-8 -*-
"""
测试用例数据模型
@Function: 定义测试用例表结构，支持版本管理、分组、标签
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class TestCase(Base):
    """测试用例表"""
    __tablename__ = "test_case"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    case_name = Column(String(200), nullable=False, comment="用例名称")
    module = Column(String(100), default="", comment="所属模块/分组")
    tags = Column(String(500), default="", comment="标签，逗号分隔")
    priority = Column(String(10), default="P0", comment="优先级：P0/P1/P2")
    description = Column(Text, default="", comment="用例描述")
    steps = Column(Text, default="[]", comment="步骤内容，JSON格式")
    version = Column(Integer, default=1, comment="版本号")
    status = Column(Integer, default=1, comment="状态：1启用 0禁用")
    platform = Column(String(50), default="web", comment="适用平台：web/android/ios/miniapp")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "case_name": self.case_name,
            "module": self.module,
            "tags": self.tags.split(",") if self.tags else [],
            "priority": self.priority,
            "description": self.description,
            "steps": self.steps,
            "version": self.version,
            "status": self.status,
            "platform": self.platform,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
