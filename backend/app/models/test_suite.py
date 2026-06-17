# -*- coding: utf-8 -*-
"""
测试套件数据模型 / Test suite data model
@Function: 定义测试套件表结构，支持用例集管理 / Define test suite table for case collection management
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class TestSuite(Base):
    """测试套件表 / Test suite table"""
    __tablename__ = "test_suite"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    suite_name = Column(String(200), nullable=False, comment="套件名称")
    description = Column(Text, default="", comment="套件描述")
    case_ids = Column(Text, default="[]", comment="用例ID列表，JSON格式")
    case_order = Column(Text, default="[]", comment="用例执行顺序，JSON格式")
    suite_type = Column(String(50), default="regression", comment="套件类型：smoke/regression/custom")
    platform = Column(String(50), default="web", comment="适用平台")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """@Function: 转换为字典 / Convert to dictionary"""
        import json
        return {
            "id": self.id,
            "suite_name": self.suite_name,
            "description": self.description,
            "case_ids": json.loads(self.case_ids) if self.case_ids else [],
            "case_order": json.loads(self.case_order) if self.case_order else [],
            "suite_type": self.suite_type,
            "platform": self.platform,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
