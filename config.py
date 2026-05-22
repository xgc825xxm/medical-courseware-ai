#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识源配置文件
支持本地文件和云端API混合模式
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 知识源配置
KNOWLEDGE_SOURCES = {
    'local_wiki': {
        'type': 'local',
        'path': BASE_DIR / 'wiki-samples',  # 示例路径，实际使用时修改
        'format': 'markdown',
        'enabled': True,
        'description': '本地Wiki知识库'
    },
    'local_literature': {
        'type': 'local', 
        'path': Path('E:/文献库'),  # 修改为你的文献库路径
        'format': 'pdf/docx',
        'enabled': False,  # 默认关闭，需要时开启
        'description': '本地文献库'
    },
    'lexiang': {
        'type': 'api',
        'base_url': 'https://api.lexiang.com',
        'api_key': os.getenv('LEXIANG_API_KEY', ''),
        'enabled': False,  # 需要API key时开启
        'description': '乐享知识库'
    },
    'ima': {
        'type': 'api',
        'base_url': 'https://ima.qq.com/api',
        'api_key': os.getenv('IMA_API_KEY', ''),
        'enabled': False,
        'description': 'IMA知识库'
    },
    'ones': {
        'type': 'api',
        'base_url': 'https://ones.cn/api',
        'api_key': os.getenv('ONES_API_KEY', ''),
        'enabled': False,
        'description': 'ONES'
    },
    'obsidian': {
        'type': 'local',
        'path': Path('E:/.opencode/小光/xiaoguang'),  # 修改为你的Obsidian路径
        'format': 'obsidian_vault',
        'enabled': False,  # 默认关闭
        'description': 'Obsidian个人库'
    }
}

# LLM配置
LLM_CONFIG = {
    'provider': 'openai',  # 或 'ollama', 'anthropic'
    'base_url': os.getenv('LLM_BASE_URL', 'http://localhost:11434'),  # Ollama默认地址
    'api_key': os.getenv('LLM_API_KEY', ''),
    'model': os.getenv('LLM_MODEL', 'qwen2'),  # 默认使用qwen2
    'temperature': 0.7,
    'max_tokens': 4000
}

# 输出配置
OUTPUT_CONFIG = {
    'output_dir': BASE_DIR / 'output',
    'format': 'markdown',  # 输出格式
    'save_intermediate': True  # 是否保存中间结果
}
