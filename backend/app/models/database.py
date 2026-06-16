# -*- coding: utf-8 -*-
"""
数据库配置与连接管理
@Function: 提供SQLite数据库连接、会话管理、表初始化
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'autotest.db'}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """@Function: 获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """@Function: 初始化数据库，创建所有表"""
    from app.models.test_case import TestCase
    from app.models.test_element import TestElement
    from app.models.exec_record import ExecRecord
    from app.models.sys_config import SysConfig
    from app.models.global_var import GlobalVar
    from app.models.test_suite import TestSuite
    from app.models.scheduler_task import SchedulerTask

    Base.metadata.create_all(bind=engine)
