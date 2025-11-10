#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供环境变量加载等通用功能
"""

import os
from dotenv import load_dotenv


def load_env_config():
    """从.env文件加载配置"""
    load_dotenv()

    config = {
        'qq_email': os.getenv('QQ_EMAIL'),
        'qq_auth_code': os.getenv('QQ_AUTH_CODE'),
        'recipient_email': os.getenv('RECIPIENT_EMAIL'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY')
    }

    # 验证配置
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise ValueError(f"缺少环境变量: {', '.join(missing)}")

    return config
