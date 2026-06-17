# -*- coding: utf-8 -*-
"""
数据库配置与连接管理 / Database configuration and connection management
@Function: 提供 SQLite 数据库连接、会话管理、表初始化 / Provide SQLite connection, session management, table initialization
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件路径 / Database file path
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'autotest.db'}"

# 创建数据库引擎 / Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 单线程限制 / SQLite single-thread limit
    echo=False,
)

# 创建会话工厂 / Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明 ORM 基类 / Declare ORM base class
Base = declarative_base()


def get_db():
    """@Function: 获取数据库会话（依赖注入用）/ Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """@Function: 初始化数据库，创建所有表 / Initialize database, create all tables"""
    from app.models.test_case import TestCase
    from app.models.test_element import TestElement
    from app.models.exec_record import ExecRecord
    from app.models.sys_config import SysConfig
    from app.models.global_var import GlobalVar
    from app.models.test_suite import TestSuite
    from app.models.scheduler_task import SchedulerTask
    from app.models.record_task import RecordTask
    from app.models.record_step import RecordStep

    Base.metadata.create_all(bind=engine)
