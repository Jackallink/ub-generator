#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工离职流程日志模拟器配置文件 v1.0.0
"""

from version import __version__, __version_info__

# ==================== 版本配置 ====================
VERSION_CONFIG = {
    "version": __version__,
    "version_info": __version_info__,
    "config_version": "1.0.0",
    "compatibility_check": True,
    "update_check_enabled": False
}

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

# 企业系统配置
ENTERPRISE_SYSTEMS = {
    # 核心业务系统
    "core_systems": {
        "ERP系统": {"sensitivity": "高", "access_hours": "7x24", "monitor_level": "严格"},
        "财务系统": {"sensitivity": "极高", "access_hours": "工作时间", "monitor_level": "严格"},
        "CRM系统": {"sensitivity": "高", "access_hours": "7x24", "monitor_level": "严格"},
        "HR系统": {"sensitivity": "极高", "access_hours": "工作时间", "monitor_level": "严格"},
    },
    
    # 敏感信息系统
    "sensitive_systems": {
        "代码仓库": {"sensitivity": "极高", "access_hours": "7x24", "monitor_level": "严格"},
        "生产环境": {"sensitivity": "极高", "access_hours": "限制", "monitor_level": "严格"},
        "客户数据库": {"sensitivity": "极高", "access_hours": "工作时间", "monitor_level": "严格"},
        "财务报表系统": {"sensitivity": "极高", "access_hours": "工作时间", "monitor_level": "严格"},
        "薪酬系统": {"sensitivity": "极高", "access_hours": "限制", "monitor_level": "严格"},
        "合同管理系统": {"sensitivity": "高", "access_hours": "工作时间", "monitor_level": "正常"},
        "知识产权系统": {"sensitivity": "极高", "access_hours": "工作时间", "monitor_level": "严格"},
    },
    
    # 办公系统
    "office_systems": {
        "邮件系统": {"sensitivity": "中", "access_hours": "7x24", "monitor_level": "正常"},
        "即时通讯": {"sensitivity": "中", "access_hours": "7x24", "monitor_level": "正常"},
        "文档管理": {"sensitivity": "中", "access_hours": "7x24", "monitor_level": "正常"},
        "OA系统": {"sensitivity": "中", "access_hours": "7x24", "monitor_level": "正常"},
        "视频会议": {"sensitivity": "低", "access_hours": "7x24", "monitor_level": "正常"},
    },
    
    # 基础设施
    "infrastructure": {
        "VPN": {"sensitivity": "高", "access_hours": "7x24", "monitor_level": "严格"},
        "堡垒机": {"sensitivity": "极高", "access_hours": "限制", "monitor_level": "严格"},
        "监控系统": {"sensitivity": "高", "access_hours": "限制", "monitor_level": "严格"},
        "备份系统": {"sensitivity": "高", "access_hours": "限制", "monitor_level": "严格"},
    }
}

# 员工角色和权限配置
EMPLOYEE_ROLES = {
    "高管": {
        "departments": ["CEO办公室", "副总办公室"],
        "systems_access": ["全部"],
        "risk_profile": "高风险",
        "resignation_impact": "极高",
        "monitoring_level": "特别关注"
    },
    "财务人员": {
        "departments": ["财务部"],
        "systems_access": ["财务系统", "ERP系统", "薪酬系统", "合同管理系统"],
        "risk_profile": "高风险",
        "resignation_impact": "高",
        "monitoring_level": "重点关注"
    },
    "技术人员": {
        "departments": ["技术部", "产品部"],
        "systems_access": ["代码仓库", "生产环境", "监控系统", "备份系统"],
        "risk_profile": "极高风险",
        "resignation_impact": "极高",
        "monitoring_level": "特别关注"
    },
    "销售人员": {
        "departments": ["市场部", "销售部"],
        "systems_access": ["CRM系统", "客户数据库", "合同管理系统"],
        "risk_profile": "高风险", 
        "resignation_impact": "高",
        "monitoring_level": "重点关注"
    },
    "HR人员": {
        "departments": ["人力资源部"],
        "systems_access": ["HR系统", "薪酬系统"],
        "risk_profile": "极高风险",
        "resignation_impact": "极高",
        "monitoring_level": "特别关注"
    },
    "一般员工": {
        "departments": ["运营部", "法务部", "行政部"],
        "systems_access": ["办公系统"],
        "risk_profile": "中风险",
        "resignation_impact": "中",
        "monitoring_level": "常规关注"
    }
}

# 异常行为模式配置
ANOMALY_PATTERNS = {
    # 离职前异常行为
    "pre_resignation": {
        "大量下载": {"probability": 0.15, "severity": "高", "description": "离职前大量下载公司文件"},
        "频繁访问敏感系统": {"probability": 0.12, "severity": "极高", "description": "异常频繁访问敏感系统"},
        "权限探测": {"probability": 0.08, "severity": "高", "description": "尝试访问超出权限范围的系统"},
        "数据导出": {"probability": 0.10, "severity": "极高", "description": "导出客户数据、员工信息等敏感数据"},
        "代码仓库克隆": {"probability": 0.20, "severity": "极高", "description": "技术人员大量克隆代码仓库"},
        "异常时间访问": {"probability": 0.25, "severity": "中", "description": "非工作时间频繁访问系统"}
    },
    
    # 离职后违规行为
    "post_resignation": {
        "账号盗用": {"probability": 0.05, "severity": "极高", "description": "使用他人账号访问系统"},
        "VPN暴力破解": {"probability": 0.03, "severity": "极高", "description": "尝试暴力破解VPN密码"},
        "社会工程学攻击": {"probability": 0.02, "severity": "高", "description": "诱导其他员工提供访问权限"},
        "远程访问尝试": {"probability": 0.08, "severity": "高", "description": "从外部网络尝试访问内部系统"},
        "恶意软件植入": {"probability": 0.01, "severity": "极高", "description": "在离职前植入恶意软件"},
        "数据泄露": {"probability": 0.03, "severity": "极高", "description": "向竞争对手泄露公司机密"}
    },
    
    # 管理流程异常
    "process_anomalies": {
        "权限回收延迟": {"probability": 0.30, "severity": "高", "description": "HR流程不规范导致权限回收延迟"},
        "账号禁用遗漏": {"probability": 0.25, "severity": "高", "description": "部分系统账号未及时禁用"},
        "移交记录缺失": {"probability": 0.20, "severity": "中", "description": "账号移交记录不完整"},
        "审批流程绕过": {"probability": 0.15, "severity": "高", "description": "紧急离职绕过正常审批流程"},
        "设备回收遗漏": {"probability": 0.35, "severity": "中", "description": "工作设备未及时回收"},
        "证件注销延迟": {"probability": 0.40, "severity": "中", "description": "工卡、门禁卡注销延迟"}
    }
}

# 离职原因分类（影响风险评估）
RESIGNATION_REASONS = {
    "主动离职": {
        "个人发展": {"risk_multiplier": 1.0, "probability": 0.30},
        "薪酬不满": {"risk_multiplier": 1.5, "probability": 0.20},
        "工作环境": {"risk_multiplier": 1.8, "probability": 0.15},
        "家庭原因": {"risk_multiplier": 0.8, "probability": 0.15},
        "健康原因": {"risk_multiplier": 0.5, "probability": 0.10},
        "继续深造": {"risk_multiplier": 0.7, "probability": 0.10}
    },
    "被动离职": {
        "绩效不达标": {"risk_multiplier": 2.0, "probability": 0.40},
        "违规违纪": {"risk_multiplier": 3.0, "probability": 0.25},
        "组织调整": {"risk_multiplier": 1.5, "probability": 0.20},
        "经济性裁员": {"risk_multiplier": 2.5, "probability": 0.15}
    }
}

# 系统配置
SYSTEM_CONFIG = {
    "hr_systems": ["HRIS", "ERP", "OA", "财务系统", "考勤系统"],
    "access_systems": list(ENTERPRISE_SYSTEMS["core_systems"].keys()) + 
                     list(ENTERPRISE_SYSTEMS["sensitive_systems"].keys()) + 
                     list(ENTERPRISE_SYSTEMS["office_systems"].keys()) + 
                     list(ENTERPRISE_SYSTEMS["infrastructure"].keys()),
    "account_types": ["域账号", "邮箱账号", "VPN账号", "数据库账号", "应用账号", "特权账号"],
    "departments": ["技术部", "产品部", "市场部", "销售部", "人力资源部", "财务部", "运营部", "法务部", "行政部", "CEO办公室", "副总办公室"],
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
    "security_incident": "security_incident.log",
    "anomaly_detection": "anomaly_detection.log",
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
    "urgent_resignation_days": 3,  # 紧急离职天数
    "security_review_days": 14,  # 安全审查期（天）
}

# 模拟数据配置
SIMULATION_CONFIG = {
    "total_employees": 1000,  # 总员工数
    "resignation_rate": 0.02,  # 月离职率 2%
    "violation_rate": 0.05,  # 违规访问概率 5%
    "system_downtime_rate": 0.01,  # 系统故障率 1%
    "high_risk_employee_rate": 0.15,  # 高风险员工比例 15%
    "anomaly_detection_accuracy": 0.85,  # 异常检测准确率 85%
    "false_positive_rate": 0.05,  # 误报率 5%
}

# 风险评分配置
RISK_SCORING = {
    "employee_role_weight": 0.3,
    "system_sensitivity_weight": 0.25,
    "resignation_reason_weight": 0.2,
    "behavior_pattern_weight": 0.15,
    "timing_weight": 0.1,
    
    "risk_thresholds": {
        "低风险": 0.3,
        "中风险": 0.6,
        "高风险": 0.8,
        "极高风险": 1.0
    }
}

# 真实企业场景配置
REALISTIC_SCENARIOS = {
    "typical_workday": {
        "start_hour": 9,
        "end_hour": 18,
        "peak_hours": [10, 14, 16],
        "lunch_break": [12, 13],
        "overtime_probability": 0.3,
        "weekend_work_probability": 0.15
    },
    
    "business_cycles": {
        "month_end": {"activity_multiplier": 1.8, "days": [28, 29, 30, 31]},
        "quarter_end": {"activity_multiplier": 2.2, "months": [3, 6, 9, 12]},
        "year_end": {"activity_multiplier": 2.5, "month": 12}
    },
    
    "emergency_scenarios": {
        "system_outage": {"probability": 0.02, "duration_hours": [1, 8]},
        "security_incident": {"probability": 0.01, "response_time_hours": [0.5, 4]},
        "data_breach": {"probability": 0.005, "investigation_days": [7, 30]}
    }
} 