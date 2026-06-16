# -*- coding: utf-8 -*-
"""
全局变量数据模型
@Function: 定义全局变量表结构，支持加密存储敏感数据
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models.database import Base


class GlobalVar(Base):
    """全局变量表"""
    __tablename__ = "global_var"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    var_name = Column(String(100), unique=True, nullable=False, comment="变量名")
    var_value = Column(Text, default="", comment="变量值")
    var_type = Column(String(50), default="string", comment="变量类型：string/number/boolean/encrypted")
    description = Column(String(500), default="", comment="变量说明")
    scope = Column(String(50), default="global", comment="作用域：global/module/case")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "var_name": self.var_name,
            "var_value": "******" if self.var_type == "encrypted" else self.var_value,
            "var_type": self.var_type,
            "description": self.description,
            "scope": self.scope,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
        }
