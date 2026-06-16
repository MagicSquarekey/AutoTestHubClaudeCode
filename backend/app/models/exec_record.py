# -*- coding: utf-8 -*-
"""
执行记录数据模型
@Function: 定义执行记录表结构，记录每次任务执行的详细信息
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.models.database import Base


class ExecRecord(Base):
    """执行记录表"""
    __tablename__ = "exec_record"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    task_name = Column(String(200), default="", comment="任务名称")
    task_id = Column(String(100), unique=True, nullable=False, comment="任务唯一标识")
    case_count = Column(Integer, default=0, comment="用例总数")
    pass_count = Column(Integer, default=0, comment="通过数")
    fail_count = Column(Integer, default=0, comment="失败数")
    skip_count = Column(Integer, default=0, comment="跳过数")
    pass_rate = Column(Float, default=0.0, comment="通过率")
    exec_duration = Column(Integer, default=0, comment="执行耗时（秒）")
    platform = Column(String(50), default="web", comment="执行平台")
    device_info = Column(Text, default="{}", comment="设备信息，JSON格式")
    report_path = Column(String(500), default="", comment="报告文件路径")
    status = Column(String(20), default="pending", comment="执行状态：pending/running/completed/failed")
    error_message = Column(Text, default="", comment="错误信息")
    exec_time = Column(DateTime, default=datetime.now, comment="执行时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "task_id": self.task_id,
            "case_count": self.case_count,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "skip_count": self.skip_count,
            "pass_rate": self.pass_rate,
            "exec_duration": self.exec_duration,
            "platform": self.platform,
            "device_info": self.device_info,
            "report_path": self.report_path,
            "status": self.status,
            "error_message": self.error_message,
            "exec_time": self.exec_time.strftime("%Y-%m-%d %H:%M:%S") if self.exec_time else None,
        }
