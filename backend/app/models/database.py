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
    from app.models.test_module import TestModule
    from app.models.test_tag import TestTag
    from app.models.record_category import RecordCategory

    Base.metadata.create_all(bind=engine)

    # 数据迁移：从用例表提取模块和标签 / Data migration: extract modules and tags from test_case
    _migrate_modules_and_tags()

    # 数据迁移：为录制任务表添加新字段 / Data migration: add new fields to record_task
    _migrate_record_task_fields()

    # 数据迁移：为用例表添加排序字段 / Data migration: add sort_order field to test_case
    _migrate_case_sort_order()


def _migrate_modules_and_tags():
    """@Function: 迁移现有用例中的模块和标签到新表 / Migrate existing modules and tags to new tables"""
    from app.models.test_case import TestCase
    from app.models.test_module import TestModule
    from app.models.test_tag import TestTag

    db = SessionLocal()
    try:
        # 迁移模块 / Migrate modules
        if db.query(TestModule).count() == 0:
            modules = db.query(TestCase.module).distinct().all()
            for i, (module_name,) in enumerate(modules):
                if module_name and module_name.strip():
                    db.add(TestModule(name=module_name.strip(), sort_order=i))
            db.commit()

        # 迁移标签 / Migrate tags
        if db.query(TestTag).count() == 0:
            tag_names = set()
            cases = db.query(TestCase.tags).all()
            for (tags_str,) in cases:
                if tags_str:
                    for tag in tags_str.split(","):
                        tag = tag.strip()
                        if tag:
                            tag_names.add(tag)
            for tag_name in tag_names:
                db.add(TestTag(name=tag_name))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"数据迁移失败 / Data migration failed: {e}")
    finally:
        db.close()


def _migrate_record_task_fields():
    """@Function: 为录制任务表添加新字段 / Add new fields to record_task table"""
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            # 检查 category_id 列是否存在
            result = conn.execute(text("PRAGMA table_info(record_task)"))
            columns = [row[1] for row in result.fetchall()]

            if 'category_id' not in columns:
                conn.execute(text("ALTER TABLE record_task ADD COLUMN category_id INTEGER DEFAULT NULL"))
                print("添加 record_task.category_id 列")

            if 'tags' not in columns:
                conn.execute(text("ALTER TABLE record_task ADD COLUMN tags VARCHAR(500) DEFAULT ''"))
                print("添加 record_task.tags 列")

            conn.commit()
    except Exception as e:
        print(f"录制任务表迁移失败 / Record task migration failed: {e}")


def _migrate_case_sort_order():
    """@Function: 为用例表添加排序字段 / Add sort_order field to test_case table"""
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            # 检查 sort_order 列是否存在
            result = conn.execute(text("PRAGMA table_info(test_case)"))
            columns = [row[1] for row in result.fetchall()]

            if 'sort_order' not in columns:
                conn.execute(text("ALTER TABLE test_case ADD COLUMN sort_order INTEGER DEFAULT 0"))
                print("添加 test_case.sort_order 列")

            conn.commit()
    except Exception as e:
        print(f"用例表迁移失败 / Test case migration failed: {e}")
