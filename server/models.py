#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库模型定义
对应数据库中的表结构
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BIGINT
from sqlalchemy.sql import func
from db import Base

class User(Base):
    """用户表模型"""
    __tablename__ = 't_user'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    password = Column(String(64), nullable=False, comment='密码（MD5加密）')
    nickname = Column(String(50), default='', comment='昵称')
    role = Column(String(10), default='user', comment='角色：admin-管理员，user-普通用户')
    avatar = Column(String(255), default='', comment='头像地址')
    status = Column(Boolean, default=True, comment='状态：1-启用，0-禁用')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

class KnowledgeBase(Base):
    """知识库表模型"""
    __tablename__ = 't_knowledge_base'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='知识库ID')
    kb_name = Column(String(100), nullable=False, comment='知识库名称')
    description = Column(String(500), default='', comment='知识库描述')
    creator_id = Column(Integer, ForeignKey('t_user.id'), nullable=False, comment='创建者ID')
    doc_count = Column(Integer, default=0, comment='文档数量')
    status = Column(Boolean, default=True, comment='状态：1-正常，0-禁用')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

class Document(Base):
    """文档表模型"""
    __tablename__ = 't_document'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='文档ID')
    kb_id = Column(Integer, ForeignKey('t_knowledge_base.id'), nullable=False, comment='所属知识库ID')
    file_name = Column(String(255), nullable=False, comment='文件名')
    file_path = Column(String(500), nullable=False, comment='文件存储路径')
    file_size = Column(BIGINT, default=0, comment='文件大小（字节）')
    file_type = Column(String(20), nullable=False, comment='文件类型：txt/pdf/md/docx')
    chunk_count = Column(Integer, default=0, comment='分块数量')
    status = Column(String(20), default='uploading', comment='状态：uploading-上传中，vectorized-已向量化，failed-失败')
    creator_id = Column(Integer, ForeignKey('t_user.id'), nullable=False, comment='上传者ID')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')

class ChatHistory(Base):
    """对话历史表模型"""
    __tablename__ = 't_chat_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('t_user.id'), nullable=False, comment='用户ID')
    kb_id = Column(Integer, ForeignKey('t_knowledge_base.id'), nullable=False, comment='知识库ID')
    session_id = Column(String(64), nullable=False, comment='会话ID')
    question = Column(Text, nullable=False, comment='用户提问')
    answer = Column(Text, nullable=False, comment='AI回答')
    source_docs = Column(Text, comment='参考文档来源（JSON格式）')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
