#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理工具类
"""

import logging
import os
import json
from datetime import datetime
from config import LOG_DIR, LOG_FILES

class LoggerManager:
    """日志管理器，负责创建和管理各种类型的日志记录器"""
    
    def __init__(self):
        self.loggers = {}
        self._setup_loggers()
    
    def _setup_loggers(self):
        """设置所有类型的日志记录器"""
        
        # 日志格式配置
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        json_formatter = logging.Formatter('%(message)s')
        
        for log_type, filename in LOG_FILES.items():
            logger = logging.getLogger(log_type)
            logger.setLevel(logging.INFO)
            
            # 清除现有的处理器
            logger.handlers.clear()
            
            # 文件处理器
            file_handler = logging.FileHandler(
                os.path.join(LOG_DIR, filename), 
                encoding='utf-8'
            )
            
            if log_type in ['hr_database', 'system_access', 'audit_monitor']:
                file_handler.setFormatter(json_formatter)
            else:
                file_handler.setFormatter(detailed_formatter)
            
            logger.addHandler(file_handler)
            
            # 控制台处理器（仅用于主日志和错误日志）
            if log_type in ['main', 'error']:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(detailed_formatter)
                logger.addHandler(console_handler)
            
            self.loggers[log_type] = logger
    
    def get_logger(self, log_type):
        """获取指定类型的日志记录器"""
        return self.loggers.get(log_type, self.loggers['main'])
    
    def log_hr_record(self, employee_id, action, details):
        """记录HR数据库操作日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "HR_DATABASE",
            "employee_id": employee_id,
            "action": action,
            "details": details,
            "source_system": "HRIS"
        }
        self.get_logger('hr_database').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_system_access(self, user_id, system, action, result, ip_address=None):
        """记录系统访问日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "SYSTEM_ACCESS",
            "user_id": user_id,
            "system": system,
            "action": action,
            "result": result,
            "ip_address": ip_address or "192.168.1.100",
            "session_id": f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
        }
        self.get_logger('system_access').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_data_operation(self, operation, source, target, rows_count, duration):
        """记录数据操作日志"""
        self.get_logger('data_collection').info(
            f"数据操作 - 操作类型: {operation}, 数据源: {source}, 目标: {target}, "
            f"数据行数: {rows_count}, 耗时: {duration:.2f}秒"
        )
    
    def log_sync_operation(self, sync_type, data_count, duration, status):
        """记录数据同步日志"""
        self.get_logger('data_sync').info(
            f"数据同步 - 类型: {sync_type}, 数据量: {data_count}条, "
            f"耗时: {duration:.2f}秒, 状态: {status}"
        )
    
    def log_audit_event(self, event_type, employee_id, details, risk_level):
        """记录审计事件日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "AUDIT_EVENT",
            "event_type": event_type,
            "employee_id": employee_id,
            "details": details,
            "risk_level": risk_level,
            "audit_id": f"audit_{datetime.now().strftime('%Y%m%d%H%M%S')}_{employee_id}"
        }
        self.get_logger('audit_monitor').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_account_operation(self, employee_id, account_type, operation, system, status):
        """记录账号管理操作日志"""
        self.get_logger('account_management').info(
            f"账号管理 - 员工ID: {employee_id}, 账号类型: {account_type}, "
            f"操作: {operation}, 系统: {system}, 状态: {status}"
        )
    
    def log_violation_alert(self, employee_id, violation_type, system, details):
        """记录违规访问告警日志"""
        self.get_logger('violation_alert').warning(
            f"违规访问告警 - 员工ID: {employee_id}, 违规类型: {violation_type}, "
            f"涉及系统: {system}, 详情: {details}"
        )
    
    def log_performance(self, operation, target_time, actual_time, success):
        """记录性能监控日志"""
        status = "成功" if success else "超时"
        self.get_logger('performance').info(
            f"性能监控 - 操作: {operation}, 目标时间: {target_time}秒, "
            f"实际时间: {actual_time:.2f}秒, 状态: {status}"
        )
    
    def log_error(self, error_type, message, details=None):
        """记录错误日志"""
        error_msg = f"错误类型: {error_type}, 消息: {message}"
        if details:
            error_msg += f", 详情: {details}"
        self.get_logger('error').error(error_msg)
    
    def log_info(self, message):
        """记录主要信息日志"""
        self.get_logger('main').info(message)

# 全局日志管理器实例
logger_manager = LoggerManager() 