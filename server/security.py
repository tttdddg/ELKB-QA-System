#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全模块
包含JWT Token的生成、验证等功能
"""

import jwt
from datetime import datetime, timedelta
from flask import request, g
from functools import wraps
from config import config
from db import get_db
from models import User

# 获取配置
current_config = config['default']

def generate_token(user_id: int, username: str, role: str) -> str:
    """
    生成JWT Token
    :param user_id: 用户ID
    :param username: 用户名
    :param role: 用户角色
    :return: JWT Token字符串
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=current_config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    return jwt.encode(payload, current_config.JWT_SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    """
    验证JWT Token
    :param token: Token字符串
    :return: 解码后的payload，如果验证失败返回None
    """
    try:
        payload = jwt.decode(token, current_config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """
    登录装饰器
    验证请求中是否包含有效的JWT Token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'code': 401, 'message': '未登录或Token无效'}, 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return {'code': 401, 'message': 'Token已过期或无效'}, 401
        
        # 获取用户信息
        db = next(get_db())
        user = db.query(User).filter(User.id == payload['user_id']).first()
        
        if not user or not user.status:
            return {'code': 401, 'message': '用户不存在或已禁用'}, 401
        
        # 将用户信息存入g对象
        g.user = user
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    管理员权限装饰器
    要求用户必须是管理员角色
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'code': 401, 'message': '未登录或Token无效'}, 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return {'code': 401, 'message': 'Token已过期或无效'}, 401
        
        # 获取用户信息
        db = next(get_db())
        user = db.query(User).filter(User.id == payload['user_id']).first()
        
        if not user or not user.status:
            return {'code': 401, 'message': '用户不存在或已禁用'}, 401
        
        if user.role != 'admin':
            return {'code': 403, 'message': '权限不足，需要管理员权限'}, 403
        
        # 将用户信息存入g对象
        g.user = user
        
        return f(*args, **kwargs)
    return decorated_function
