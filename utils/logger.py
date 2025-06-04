#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理工具类 - 增强版，支持真实企业场景
"""

import logging
import os
import json
from datetime import datetime, timedelta
from config import LOG_DIR, LOG_FILES
import random

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
            
            if log_type in ['hr_database', 'system_access', 'audit_monitor', 'security_incident', 'anomaly_detection']:
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
    
    def log_system_access(self, user_id, system, action, result, ip_address=None, risk_score=0.0, is_suspicious=False):
        """记录系统访问日志 - 增强版"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "SYSTEM_ACCESS",
            "user_id": user_id,
            "system": system,
            "action": action,
            "result": result,
            "ip_address": ip_address or "192.168.1.100",
            "session_id": f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}",
            "risk_score": risk_score,
            "is_suspicious": is_suspicious,
            "geolocation": self._get_geolocation_from_ip(ip_address),
            "user_agent": "Mozilla/5.0 (compatible; Enterprise-Monitor/1.0)"
        }
        self.get_logger('system_access').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_security_incident(self, incident_type, employee_id, severity, details, affected_systems=None):
        """记录安全事件日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "SECURITY_INCIDENT",
            "incident_id": f"INC_{datetime.now().strftime('%Y%m%d%H%M%S')}_{employee_id}",
            "incident_type": incident_type,
            "employee_id": employee_id,
            "severity": severity,
            "details": details,
            "affected_systems": affected_systems or [],
            "status": "新增",
            "investigation_required": severity in ["高", "极高"],
            "compliance_impact": self._assess_compliance_impact(incident_type, severity)
        }
        self.get_logger('security_incident').error(json.dumps(log_data, ensure_ascii=False))
    
    def log_anomaly_detection(self, anomaly_type, employee_id, confidence_score, anomaly_details, system=None):
        """记录异常检测日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "ANOMALY_DETECTION",
            "detection_id": f"ANOM_{datetime.now().strftime('%Y%m%d%H%M%S')}_{employee_id}",
            "anomaly_type": anomaly_type,
            "employee_id": employee_id,
            "system": system,
            "confidence_score": confidence_score,
            "details": anomaly_details,
            "detection_method": "行为分析引擎",
            "requires_investigation": confidence_score > 0.8,
            "risk_level": self._determine_anomaly_risk_level(confidence_score),
            "baseline_deviation": round(confidence_score * 100, 2)
        }
        self.get_logger('anomaly_detection').warning(json.dumps(log_data, ensure_ascii=False))
    
    def log_employee_risk_assessment(self, employee_id, risk_data):
        """记录员工风险评估日志"""
        # 计算下个月的第一天
        next_month = datetime.now().replace(day=28) + timedelta(days=4)
        next_review_date = next_month.replace(day=1)
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "RISK_ASSESSMENT",
            "employee_id": employee_id,
            "assessment_data": risk_data,
            "assessment_trigger": "离职申请",
            "next_review_date": next_review_date.isoformat()
        }
        self.get_logger('audit_monitor').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_privileged_access(self, employee_id, account_id, system, action, justification):
        """记录特权访问日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "PRIVILEGED_ACCESS",
            "employee_id": employee_id,
            "account_id": account_id,
            "system": system,
            "action": action,
            "business_justification": justification,
            "approval_status": "自动批准",
            "session_recorded": True,
            "compliance_requirements": ["特权账号审计", "SOX合规"]
        }
        self.get_logger('audit_monitor').info(json.dumps(log_data, ensure_ascii=False))
    
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
        """记录审计事件日志 - 增强版"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "AUDIT_EVENT",
            "event_type": event_type,
            "employee_id": employee_id,
            "details": details,
            "risk_level": risk_level,
            "audit_id": f"audit_{datetime.now().strftime('%Y%m%d%H%M%S')}_{employee_id}",
            "compliance_frameworks": self._get_applicable_compliance_frameworks(event_type),
            "remediation_required": risk_level in ["高", "极高"],
            "escalation_level": self._determine_escalation_level(risk_level)
        }
        self.get_logger('audit_monitor').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_account_operation(self, employee_id, account_type, operation, system, status):
        """记录账号管理操作日志 - 增强版"""
        operation_risk = self._assess_account_operation_risk(account_type, operation, status)
        
        self.get_logger('account_management').info(
            f"账号管理 - 员工ID: {employee_id}, 账号类型: {account_type}, "
            f"操作: {operation}, 系统: {system}, 状态: {status}, "
            f"风险等级: {operation_risk}, 时间戳: {datetime.now().isoformat()}"
        )
        
        # 如果是高风险操作，同时记录安全事件
        if operation_risk in ["高", "极高"]:
            self.log_security_incident(
                f"高风险账号操作-{operation}",
                employee_id,
                operation_risk,
                {
                    "account_type": account_type,
                    "operation": operation,
                    "system": system,
                    "status": status,
                    "automatic_detection": True
                },
                [system]
            )
    
    def log_violation_alert(self, employee_id, violation_type, system, details):
        """记录违规访问告警日志 - 增强版"""
        severity = self._determine_violation_severity(violation_type, system)
        
        self.get_logger('violation_alert').warning(
            f"违规访问告警 - 员工ID: {employee_id}, 违规类型: {violation_type}, "
            f"涉及系统: {system}, 详情: {details}, 严重性: {severity}, "
            f"告警时间: {datetime.now().isoformat()}"
        )
        
        # 严重违规自动上报为安全事件
        if severity in ["高", "极高"]:
            self.log_security_incident(
                violation_type,
                employee_id,
                severity,
                {
                    "violation_details": details,
                    "system": system,
                    "detection_method": "实时监控",
                    "immediate_action_required": True
                },
                [system]
            )
    
    def log_business_continuity_event(self, event_type, impact_level, affected_systems, details):
        """记录业务连续性事件"""
        self.get_logger('main').warning(
            f"业务连续性事件 - 事件类型: {event_type}, 影响级别: {impact_level}, "
            f"受影响系统: {', '.join(affected_systems)}, 详情: {details}, "
            f"事件时间: {datetime.now().isoformat()}"
        )
    
    def log_compliance_check(self, check_type, result, findings, recommendations):
        """记录合规检查日志"""
        next_check_date = datetime.now() + timedelta(days=30)
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "log_type": "COMPLIANCE_CHECK",
            "check_type": check_type,
            "result": result,
            "findings": findings,
            "recommendations": recommendations,
            "compliance_score": self._calculate_compliance_score(findings),
            "next_check_date": next_check_date.isoformat()
        }
        self.get_logger('audit_monitor').info(json.dumps(log_data, ensure_ascii=False))
    
    def log_performance(self, operation, target_time, actual_time, success):
        """记录性能监控日志"""
        status = "成功" if success else "超时"
        performance_ratio = actual_time / target_time if target_time > 0 else 0
        
        self.get_logger('performance').info(
            f"性能监控 - 操作: {operation}, 目标时间: {target_time}秒, "
            f"实际时间: {actual_time:.2f}秒, 状态: {status}, "
            f"性能比率: {performance_ratio:.2f}, 时间戳: {datetime.now().isoformat()}"
        )
    
    def log_error(self, error_type, message, details=None):
        """记录错误日志"""
        error_msg = f"错误类型: {error_type}, 消息: {message}"
        if details:
            error_msg += f", 详情: {details}"
        error_msg += f", 时间戳: {datetime.now().isoformat()}"
        self.get_logger('error').error(error_msg)
    
    def log_info(self, message):
        """记录主要信息日志"""
        self.get_logger('main').info(message)
    
    def _get_geolocation_from_ip(self, ip_address):
        """根据IP地址获取地理位置信息"""
        if not ip_address or ip_address.startswith("192.168"):
            return {"country": "中国", "city": "公司内网", "is_internal": True}
        else:
            cities = ["北京", "上海", "深圳", "广州", "杭州"]
            return {
                "country": "中国", 
                "city": random.choice(cities),
                "is_internal": False,
                "suspicious": True  # 外网访问标记为可疑
            }
    
    def _assess_compliance_impact(self, incident_type, severity):
        """评估合规影响"""
        high_impact_incidents = [
            "数据泄露", "特权账号滥用", "违规数据导出", 
            "系统入侵", "恶意软件植入"
        ]
        
        if incident_type in high_impact_incidents or severity == "极高":
            return "高影响"
        elif severity == "高":
            return "中影响"
        else:
            return "低影响"
    
    def _determine_anomaly_risk_level(self, confidence_score):
        """确定异常风险等级"""
        if confidence_score >= 0.9:
            return "极高"
        elif confidence_score >= 0.7:
            return "高"
        elif confidence_score >= 0.5:
            return "中"
        else:
            return "低"
    
    def _get_applicable_compliance_frameworks(self, event_type):
        """获取适用的合规框架"""
        frameworks = []
        
        if "财务" in event_type or "薪酬" in event_type:
            frameworks.append("SOX合规")
        
        if "数据" in event_type or "客户" in event_type:
            frameworks.extend(["个人信息保护法", "数据安全法"])
        
        if "特权" in event_type or "管理员" in event_type:
            frameworks.append("网络安全等级保护")
        
        return frameworks if frameworks else ["企业内控制度"]
    
    def _determine_escalation_level(self, risk_level):
        """确定上报级别"""
        escalation_mapping = {
            "极高": "高管层",
            "高": "部门总监",
            "中": "直接主管",
            "低": "系统管理员"
        }
        return escalation_mapping.get(risk_level, "系统管理员")
    
    def _assess_account_operation_risk(self, account_type, operation, status):
        """评估账号操作风险"""
        if account_type in ["特权账号", "数据库账号"] and operation in ["创建", "激活"]:
            return "高"
        elif status in ["移交失败", "禁用遗漏"]:
            return "高"
        elif account_type == "特权账号":
            return "中"
        else:
            return "低"
    
    def _determine_violation_severity(self, violation_type, system):
        """确定违规严重性"""
        high_severity_violations = [
            "离职后账号访问", "VPN暴力破解", "恶意软件植入", 
            "数据泄露", "账号盗用"
        ]
        
        sensitive_systems = [
            "财务系统", "HR系统", "代码仓库", "生产环境", 
            "客户数据库", "薪酬系统"
        ]
        
        if violation_type in high_severity_violations:
            return "极高"
        elif system in sensitive_systems:
            return "高"
        else:
            return "中"
    
    def _calculate_compliance_score(self, findings):
        """计算合规评分"""
        if not findings:
            return 100
        
        critical_findings = len([f for f in findings if f.get('severity') == '严重'])
        major_findings = len([f for f in findings if f.get('severity') == '重要'])
        minor_findings = len([f for f in findings if f.get('severity') == '一般'])
        
        score = 100 - (critical_findings * 20 + major_findings * 10 + minor_findings * 5)
        return max(0, score)

# 全局日志管理器实例
logger_manager = LoggerManager() 