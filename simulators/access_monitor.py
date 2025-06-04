#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统访问监控模拟器
"""

import random
import time
from datetime import datetime, timedelta
from models.employee import SystemAccessLog
from utils.logger import logger_manager
from config import SYSTEM_CONFIG, SIMULATION_CONFIG, TIME_CONFIG

class AccessMonitorSimulator:
    """系统访问监控模拟器"""
    
    def __init__(self, hr_system):
        self.hr_system = hr_system
        self.access_logs = []
        self.violation_alerts = []
        logger_manager.log_info("系统访问监控模拟器初始化完成")
    
    def generate_daily_access_logs(self, date=None):
        """生成每日系统访问日志"""
        if not date:
            date = datetime.now()
        
        # 获取所有活跃员工
        active_employees = list(self.hr_system.employees.values())
        resigned_employees = list(self.hr_system.resigned_employees.values())
        
        daily_logs_count = 0
        
        # 为活跃员工生成正常访问日志
        for employee in active_employees:
            if employee.status == "在职":
                daily_logs_count += self._generate_employee_access_logs(employee, date, is_normal=True)
        
        # 为已离职员工生成潜在的违规访问日志
        for employee in resigned_employees:
            if self._should_generate_violation_log(employee, date):
                daily_logs_count += self._generate_employee_access_logs(employee, date, is_normal=False)
        
        logger_manager.log_info(f"生成每日访问日志完成，共 {daily_logs_count} 条记录")
        return daily_logs_count
    
    def _generate_employee_access_logs(self, employee, date, is_normal=True):
        """为单个员工生成访问日志"""
        logs_count = 0
        
        # 确定该员工有访问权限的系统
        accessible_systems = []
        for system, permission in employee.system_permissions.items():
            if permission['status'] == 'active' or (not is_normal and permission['status'] == 'revoked'):
                accessible_systems.append(system)
        
        if not accessible_systems:
            return 0
        
        # 根据是否正常访问决定日志数量
        if is_normal:
            daily_access_count = random.randint(5, 20)  # 正常员工每天5-20次访问
        else:
            daily_access_count = random.randint(1, 3)   # 违规访问较少
        
        for _ in range(daily_access_count):
            system = random.choice(accessible_systems)
            
            # 生成访问日志
            access_log = SystemAccessLog(employee.employee_id, system)
            access_log.timestamp = self._generate_access_timestamp(date, is_normal)
            
            # 如果是非正常访问（已离职员工），调整结果
            if not is_normal:
                access_log.result = random.choice(["被拒绝", "失败", "成功"])
                # 记录违规访问告警
                if access_log.result == "成功":
                    self._create_violation_alert(employee, system, access_log)
            
            self.access_logs.append(access_log)
            
            # 记录系统访问日志
            logger_manager.log_system_access(
                employee.employee_id,
                system,
                access_log.action_type,
                access_log.result,
                access_log.ip_address
            )
            
            logs_count += 1
        
        return logs_count
    
    def _generate_access_timestamp(self, date, is_normal=True):
        """生成访问时间戳"""
        if is_normal:
            # 正常工作时间 9:00-18:00
            hour = random.randint(9, 18)
            minute = random.randint(0, 59)
        else:
            # 非正常时间访问（可能的违规行为）
            hour = random.choice(list(range(0, 9)) + list(range(19, 24)))
            minute = random.randint(0, 59)
        
        access_time = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        return access_time
    
    def _should_generate_violation_log(self, employee, date):
        """判断是否应该为已离职员工生成违规访问日志"""
        if not employee.last_work_date:
            return False
        
        # 计算离职后的天数
        days_since_resignation = (date.date() - employee.last_work_date.date()).days
        
        # 离职后7天内的宽限期，违规概率较低
        if days_since_resignation <= TIME_CONFIG['account_grace_period']:
            violation_probability = SIMULATION_CONFIG['violation_rate'] * 0.5
        else:
            violation_probability = SIMULATION_CONFIG['violation_rate']
        
        return random.random() < violation_probability
    
    def _create_violation_alert(self, employee, system, access_log):
        """创建违规访问告警"""
        violation_types = [
            "离职后账号访问", "越权操作", "异常时间访问", 
            "异常地点访问", "批量数据下载", "敏感资源访问"
        ]
        
        violation_type = random.choice(violation_types)
        
        # 计算风险等级
        days_since_resignation = (datetime.now().date() - employee.last_work_date.date()).days
        if days_since_resignation <= 7:
            risk_level = "中等"
        elif days_since_resignation <= 30:
            risk_level = "高"
        else:
            risk_level = "极高"
        
        violation_details = {
            "employee_name": employee.name,
            "department": employee.department,
            "resignation_date": employee.last_work_date.isoformat(),
            "days_since_resignation": days_since_resignation,
            "access_timestamp": access_log.timestamp.isoformat(),
            "ip_address": access_log.ip_address,
            "resource_accessed": access_log.resource,
            "action_performed": access_log.action_type
        }
        
        # 记录审计事件
        logger_manager.log_audit_event(
            violation_type,
            employee.employee_id,
            violation_details,
            risk_level
        )
        
        # 记录违规告警
        logger_manager.log_violation_alert(
            employee.employee_id,
            violation_type,
            system,
            f"员工{employee.name}在离职{days_since_resignation}天后访问{system}"
        )
        
        # 保存告警记录
        alert_record = {
            "alert_id": f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{employee.employee_id}",
            "employee_id": employee.employee_id,
            "violation_type": violation_type,
            "system": system,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat(),
            "details": violation_details,
            "status": "待处理"
        }
        
        self.violation_alerts.append(alert_record)
    
    def process_semi_structured_logs(self):
        """处理半结构化操作日志"""
        start_time = time.time()
        
        # 模拟从各个系统收集半结构化日志
        systems = SYSTEM_CONFIG['access_systems']
        total_logs_processed = 0
        
        for system in systems:
            # 模拟每个系统的日志处理
            system_logs = random.randint(50000, 100000)  # 每个系统5-10万条日志
            
            # 模拟日志解析和结构化过程
            processing_time = random.uniform(1.0, 5.0)
            time.sleep(processing_time)
            
            total_logs_processed += system_logs
            
            logger_manager.log_data_operation(
                "半结构化日志处理",
                f"{system}原始日志",
                "结构化数据库",
                system_logs,
                processing_time
            )
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        logger_manager.log_info(f"半结构化日志处理完成，共处理 {total_logs_processed} 条记录，耗时 {total_duration:.2f} 秒")
        
        return total_logs_processed, total_duration
    
    def extract_structured_data(self, user_accounts=None):
        """提取结构化操作记录"""
        start_time = time.time()
        
        if not user_accounts:
            # 获取所有相关用户账号
            user_accounts = []
            for employee in list(self.hr_system.employees.values()) + list(self.hr_system.resigned_employees.values()):
                if employee.status in ["离职申请", "已离职"]:
                    user_accounts.extend([acc['account_id'] for acc in employee.accounts.values()])
        
        # 模拟按用户账号集合检索结构化数据
        extracted_records = []
        for account_id in user_accounts:
            # 模拟数据库查询
            account_logs = [log for log in self.access_logs if log.user_id.endswith(account_id.split('_')[0])]
            extracted_records.extend([log.to_dict() for log in account_logs])
        
        # 模拟查询耗时
        query_time = random.uniform(0.5, 2.0)
        time.sleep(query_time)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger_manager.log_data_operation(
            "结构化数据提取",
            "操作记录数据库",
            "审计系统",
            len(extracted_records),
            duration
        )
        
        return extracted_records
    
    def monitor_account_status(self):
        """监控账号状态合规性"""
        compliance_issues = []
        
        # 检查已离职员工的账号状态
        for employee in self.hr_system.resigned_employees.values():
            for account_key, account_info in employee.accounts.items():
                if account_info['status'] == 'active':
                    issue = {
                        "issue_type": "账号未及时禁用",
                        "employee_id": employee.employee_id,
                        "employee_name": employee.name,
                        "account_id": account_info['account_id'],
                        "system": account_info['system'],
                        "resignation_date": employee.last_work_date.isoformat() if employee.last_work_date else None,
                        "detected_time": datetime.now().isoformat()
                    }
                    compliance_issues.append(issue)
                    
                    logger_manager.log_audit_event(
                        "账号合规检查",
                        employee.employee_id,
                        issue,
                        "高"
                    )
        
        # 检查移交记录完整性
        for employee in self.hr_system.resigned_employees.values():
            transfer_records = [r for r in self.hr_system.transfer_records if r.employee_id == employee.employee_id]
            expected_transfers = len([acc for acc in employee.accounts.values() if acc['status'] in ['active', 'disabled']])
            
            if len(transfer_records) < expected_transfers:
                issue = {
                    "issue_type": "移交记录不完整",
                    "employee_id": employee.employee_id,
                    "employee_name": employee.name,
                    "expected_transfers": expected_transfers,
                    "actual_transfers": len(transfer_records),
                    "detected_time": datetime.now().isoformat()
                }
                compliance_issues.append(issue)
                
                logger_manager.log_audit_event(
                    "移交记录检查",
                    employee.employee_id,
                    issue,
                    "中等"
                )
        
        logger_manager.log_info(f"账号状态合规检查完成，发现 {len(compliance_issues)} 个问题")
        return compliance_issues
    
    def get_violation_statistics(self):
        """获取违规访问统计"""
        total_alerts = len(self.violation_alerts)
        high_risk_alerts = len([alert for alert in self.violation_alerts if alert['risk_level'] in ['高', '极高']])
        
        # 按违规类型统计
        violation_types = {}
        for alert in self.violation_alerts:
            vtype = alert['violation_type']
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        # 按系统统计
        system_violations = {}
        for alert in self.violation_alerts:
            system = alert['system']
            system_violations[system] = system_violations.get(system, 0) + 1
        
        stats = {
            "total_violation_alerts": total_alerts,
            "high_risk_alerts": high_risk_alerts,
            "violation_by_type": violation_types,
            "violation_by_system": system_violations,
            "pending_alerts": len([alert for alert in self.violation_alerts if alert['status'] == '待处理'])
        }
        
        return stats 