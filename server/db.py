#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库操作模块
基于SQLAlchemy实现数据库连接和ORM映射
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

# 获取当前配置
current_config = config['default']

# 创建数据库引擎
engine = create_engine(
    current_config.SQLALCHEMY_DATABASE_URI,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()

def get_db():
    """
    获取数据库会话
    使用依赖注入方式，自动管理会话的创建和关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
