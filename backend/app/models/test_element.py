# -*- coding: utf-8 -*-
"""
测试元素数据模型
@Function: 定义测试元素表结构，支持多端定位符、健康度管理
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class TestElement(Base):
    """测试元素表"""
    __tablename__ = "test_element"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    elem_name = Column(String(200), nullable=False, comment="元素名称")
    page_name = Column(String(200), default="", comment="所属页面")
    module = Column(String(100), default="", comment="所属模块")
    locators = Column(Text, default="[]", comment="多端定位符，JSON格式")
    quote_count = Column(Integer, default=0, comment="引用次数")
    fail_count = Column(Integer, default=0, comment="累计失败次数")
    success_count = Column(Integer, default=0, comment="累计成功次数")
    screenshot = Column(String(500), default="", comment="元素截图路径")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            "id": self.id,
            "elem_name": self.elem_name,
            "page_name": self.page_name,
            "module": self.module,
            "locators": json.loads(self.locators) if self.locators else [],
            "quote_count": self.quote_count,
            "fail_count": self.fail_count,
            "success_count": self.success_count,
            "health_rate": round(self.success_count / (self.success_count + self.fail_count) * 100, 2) if (self.success_count + self.fail_count) > 0 else 100,
            "screenshot": self.screenshot,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
