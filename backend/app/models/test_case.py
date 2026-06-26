# -*- coding: utf-8 -*-
"""
测试用例数据模型 / Test case data model
@Function: 定义测试用例表结构，支持版本管理、分组、标签 / Define test case table with versioning, grouping, tags
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class TestCase(Base):
    """测试用例表 / Test case table"""
    __tablename__ = "test_case"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 / Primary key")
    case_name = Column(String(200), nullable=False, comment="用例名称 / Case name")
    module = Column(String(100), default="", comment="所属模块/分组 / Module/Group")
    tags = Column(String(500), default="", comment="标签，逗号分隔 / Tags, comma separated")
    priority = Column(String(10), default="P0", comment="优先级：P0/P1/P2 / Priority")
    description = Column(Text, default="", comment="用例描述 / Case description")
    steps = Column(Text, default="[]", comment="步骤内容，JSON 格式 / Steps in JSON format")
    setup_steps = Column(Text, default="[]", comment="前置步骤，JSON 格式 / Setup steps in JSON format")
    teardown_steps = Column(Text, default="[]", comment="后置步骤，JSON 格式 / Teardown steps in JSON format")
    version = Column(Integer, default=1, comment="版本号 / Version number")
    status = Column(Integer, default=1, comment="状态：1 启用 0 禁用 / Status: 1=enabled 0=disabled")
    platform = Column(String(50), default="web", comment="适用平台：web/android/ios/miniapp / Target platform")
    sort_order = Column(Integer, default=0, comment="排序顺序 / Sort order")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间 / Create time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间 / Update time")

    def to_dict(self):
        """@Function: 转换为字典 / Convert to dictionary"""
        return {
            "id": self.id,
            "case_name": self.case_name,
            "module": self.module,
            "tags": self.tags.split(",") if self.tags else [],
            "priority": self.priority,
            "description": self.description,
            "steps": self.steps,
            "setup_steps": self.setup_steps,
            "teardown_steps": self.teardown_steps,
            "version": self.version,
            "status": self.status,
            "platform": self.platform,
            "sort_order": self.sort_order,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
