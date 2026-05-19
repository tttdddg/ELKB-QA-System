#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函数模块
包含MD5加密、文件操作等通用工具函数
"""

import hashlib
import os
import uuid

def md5_hash(text: str) -> str:
    """
    对字符串进行MD5加密
    :param text: 要加密的字符串
    :return: MD5加密后的字符串（32位）
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def generate_uuid() -> str:
    """
    生成UUID字符串（不带连字符）
    :return: UUID字符串
    """
    return str(uuid.uuid4()).replace('-', '')

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    检查文件扩展名是否在允许列表中
    :param filename: 文件名
    :param allowed_extensions: 允许的扩展名集合
    :return: 是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名（小写）
    :param filename: 文件名
    :return: 扩展名
    """
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def ensure_dir_exists(dir_path: str):
    """
    确保目录存在，不存在则创建
    :param dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def format_file_size(bytes_size: int) -> str:
    """
    将字节大小格式化为可读的字符串
    :param bytes_size: 字节数
    :return: 格式化后的字符串
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
