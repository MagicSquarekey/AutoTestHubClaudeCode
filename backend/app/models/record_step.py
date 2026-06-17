# -*- coding: utf-8 -*-
"""
录制步骤数据模型 / Record step data model
@Function: 定义录制步骤表结构，记录用户操作步骤 / Define record step table for user action steps
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.models.database import Base


class RecordStep(Base):
    """录制步骤表 / Record step table"""
    __tablename__ = "record_step"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 / Primary key")
    task_id = Column(Integer, ForeignKey("record_task.id"), nullable=False, comment="关联任务ID / Task ID")
    step_order = Column(Integer, nullable=False, comment="步骤顺序 / Step order")
    action_type = Column(String(50), nullable=False, comment="操作类型：click/input/select/hover/navigate/wait/keyboard / Action type")
    element_locators = Column(Text, default="{}", comment="元素定位符，JSON格式 / Element locators in JSON")
    element_name = Column(String(200), default="", comment="元素名称 / Element name")
    input_value = Column(Text, default="", comment="输入值/URL/按键 / Input value/URL/key")
    screenshot = Column(String(500), default="", comment="截图路径 / Screenshot path")
    page_url = Column(String(500), default="", comment="操作时页面URL / Page URL at action time")
    status = Column(String(20), default="recorded", comment="状态：recorded/edited / Status")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间 / Create time")

    def to_dict(self):
        """@Function: 转换为字典 / Convert to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "step_order": self.step_order,
            "action_type": self.action_type,
            "element_locators": self.element_locators,
            "element_name": self.element_name,
            "input_value": self.input_value,
            "screenshot": self.screenshot,
            "page_url": self.page_url,
            "status": self.status,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
        }
