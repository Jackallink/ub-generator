#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工离职流程日志模拟器 - 配置文件
"""

import os
from datetime import datetime, timedelta

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# 创建必要的目录
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# 数据规模配置
DATA_CONFIG = {
    "daily_log_rows": 500000,  # 日均数据行：50万
    "daily_structured_rows": 10000,  # 日均结构化数据：1万
    "quarterly_total_rows": 1000000,  # 季度总数据：100万行
    "incremental_sync_max": 5000,  # 增量同步最大数据量：0-5000条
}

# 性能要求配置
PERFORMANCE_CONFIG = {
    "full_extract_time_limit": 900,  # 全量提取时间限制：15分钟
    "incremental_sync_time_limit": 15,  # 增量同步时间限制：15秒
    "sync_frequency_minutes": 10,  # 同步频率：10分钟
}

# 系统配置
SYSTEM_CONFIG = {
    "hr_systems": ["HRIS", "ERP", "OA", "财务系统", "考勤系统"],
    "access_systems": ["VPN", "邮件系统", "办公系统", "开发环境", "数据库系统", "文件服务器"],
    "account_types": ["域账号", "邮箱账号", "VPN账号", "数据库账号", "应用账号"],
    "departments": ["技术部", "产品部", "市场部", "人力资源部", "财务部", "运营部", "法务部"],
}

# 日志文件配置
LOG_FILES = {
    "hr_database": "hr_database.log",
    "system_access": "system_access.log", 
    "data_collection": "data_collection.log",
    "data_sync": "data_sync.log",
    "audit_monitor": "audit_monitor.log",
    "account_management": "account_management.log",
    "violation_alert": "violation_alert.log",
    "performance": "performance.log",
    "error": "error.log",
    "main": "main.log"
}

# 时间配置
TIME_CONFIG = {
    "simulation_start": datetime.now() - timedelta(days=90),  # 从90天前开始模拟
    "simulation_end": datetime.now(),
    "resignation_notice_days": 30,  # 离职通知提前天数
    "account_grace_period": 7,  # 账号宽限期（天）
}

# 模拟数据配置
SIMULATION_CONFIG = {
    "total_employees": 1000,  # 总员工数
    "resignation_rate": 0.02,  # 月离职率 2%
    "violation_rate": 0.05,  # 违规访问概率 5%
    "system_downtime_rate": 0.01,  # 系统故障率 1%
} 