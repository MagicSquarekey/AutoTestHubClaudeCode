# -*- coding: utf-8 -*-
"""
定时任务数据模型
@Function: 定义定时任务表结构，支持Cron调度
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class SchedulerTask(Base):
    """定时任务表"""
    __tablename__ = "scheduler_task"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    suite_id = Column(Integer, nullable=False, comment="关联套件ID")
    cron_expression = Column(String(100), default="", comment="Cron表达式")
    platform = Column(String(50), default="web", comment="执行平台")
    device_id = Column(String(200), default="", comment="执行设备ID")
    notify_type = Column(String(50), default="none", comment="通知类型：none/feishu/wecom/email")
    notify_config = Column(Text, default="{}", comment="通知配置，JSON格式")
    status = Column(Integer, default=1, comment="状态：1启用 0禁用")
    last_exec_time = Column(DateTime, comment="上次执行时间")
    next_exec_time = Column(DateTime, comment="下次执行时间")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "suite_id": self.suite_id,
            "cron_expression": self.cron_expression,
            "platform": self.platform,
            "device_id": self.device_id,
            "notify_type": self.notify_type,
            "notify_config": self.notify_config,
            "status": self.status,
            "last_exec_time": self.last_exec_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_exec_time else None,
            "next_exec_time": self.next_exec_time.strftime("%Y-%m-%d %H:%M:%S") if self.next_exec_time else None,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
