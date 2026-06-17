# -*- coding: utf-8 -*-
"""
录制任务数据模型 / Record task data model
@Function: 定义录制任务表结构，支持浏览器操作录制 / Define record task table for browser action recording
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class RecordTask(Base):
    """录制任务表 / Record task table"""
    __tablename__ = "record_task"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键 / Primary key")
    task_name = Column(String(200), nullable=False, comment="任务名称 / Task name")
    target_url = Column(String(500), default="", comment="目标URL / Target URL")
    browser_type = Column(String(50), default="chromium", comment="浏览器类型 / Browser type")
    status = Column(String(20), default="pending", comment="状态：pending/recording/completed/stopped / Status")
    step_count = Column(Integer, default=0, comment="步骤数量 / Step count")
    description = Column(Text, default="", comment="描述 / Description")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间 / Create time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间 / Update time")

    def to_dict(self):
        """@Function: 转换为字典 / Convert to dictionary"""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "target_url": self.target_url,
            "browser_type": self.browser_type,
            "status": self.status,
            "step_count": self.step_count,
            "description": self.description,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
