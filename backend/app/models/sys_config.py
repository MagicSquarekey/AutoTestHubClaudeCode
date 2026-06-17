# -*- coding: utf-8 -*-
"""
系统配置数据模型 / System configuration data model
@Function: 定义系统配置表结构，存储全局配置项 / Define system config table for global settings
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class SysConfig(Base):
    """系统配置表 / System configuration table"""
    __tablename__ = "sys_config"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, default="", comment="配置值")
    config_type = Column(String(50), default="string", comment="配置类型：string/number/boolean/json/encrypted")
    description = Column(String(500), default="", comment="配置说明")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """@Function: 转换为字典 / Convert to dictionary"""
        return {
            "id": self.id,
            "config_key": self.config_key,
            "config_value": self.config_value,
            "config_type": self.config_type,
            "description": self.description,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
