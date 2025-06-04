#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统访问监控模拟器 - 增强版，注重真实的关联性和流程逻辑
"""

import random
import time
from datetime import datetime, timedelta
from models.employee import SystemAccessLog
from utils.logger import logger_manager
from config import SYSTEM_CONFIG, SIMULATION_CONFIG, TIME_CONFIG, ENTERPRISE_SYSTEMS, ANOMALY_PATTERNS

class AccessMonitorSimulator:
    """系统访问监控模拟器 - 真实关联性版本"""
    
    def __init__(self, hr_system):
        self.hr_system = hr_system
        self.access_logs = []
        self.violation_alerts = []
        self.user_session_states = {}  # 跟踪用户会话状态
        self.system_activity_timeline = {}  # 系统活动时间线
        logger_manager.log_info("系统访问监控模拟器初始化完成")
    
    def generate_daily_access_logs(self, date=None):
        """生成每日系统访问日志 - 增强关联性"""
        if not date:
            date = datetime.now()
        
        # 获取所有活跃员工和已离职员工
        active_employees = list(self.hr_system.employees.values())
        resigned_employees = list(self.hr_system.resigned_employees.values())
        
        daily_logs_count = 0
        
        # 为活跃员工生成正常访问日志（按真实工作时间序列）
        for employee in active_employees:
            if employee.status == "在职":
                daily_logs_count += self._generate_realistic_employee_workday(employee, date)
        
        # 为已离职员工生成潜在的违规访问日志
        for employee in resigned_employees:
            if self._should_generate_violation_log(employee, date):
                daily_logs_count += self._generate_violation_access_sequence(employee, date)
        
        logger_manager.log_info(f"生成每日访问日志完成，共 {daily_logs_count} 条记录")
        return daily_logs_count
    
    def _generate_realistic_employee_workday(self, employee, date):
        """为员工生成真实的工作日访问序列"""
        logs_count = 0
        
        # 获取员工的工作模式
        work_pattern = employee.behavior_profile['work_pattern']
        
        # 确定当天的工作时间
        start_time = max(8, work_pattern['typical_start_time'])
        end_time = min(20, work_pattern['typical_end_time'])
        
        # 判断是否加班
        is_overtime = random.random() < 0.3 if work_pattern['overtime_frequency'] == "经常" else random.random() < 0.1
        if is_overtime:
            end_time += random.uniform(1, 4)
        
        # 生成工作日时间序列
        current_time = date.replace(hour=int(start_time), minute=random.randint(0, 59))
        work_end_time = date.replace(hour=int(end_time), minute=random.randint(0, 59))
        
        # 1. 上班第一件事：登录系统
        logs_count += self._generate_morning_login_sequence(employee, current_time)
        
        # 2. 工作时间内的正常业务操作
        logs_count += self._generate_business_operations_sequence(employee, current_time, work_end_time)
        
        # 3. 下班前的操作
        logs_count += self._generate_evening_logout_sequence(employee, work_end_time)
        
        # 4. 如果离职在即，可能产生异常行为
        if employee.status == "离职申请":
            logs_count += self._generate_pre_resignation_activities(employee, current_time, work_end_time)
        
        return logs_count
    
    def _generate_morning_login_sequence(self, employee, start_time):
        """生成早晨登录序列"""
        logs_count = 0
        login_sequence = ["邮件系统", "OA系统"]  # 基础系统
        
        # 根据角色添加特定系统
        if employee.role == "技术人员":
            login_sequence.extend(["代码仓库", "监控系统"])
        elif employee.role == "财务人员":
            login_sequence.extend(["财务系统", "ERP系统"])
        elif employee.role == "销售人员":
            login_sequence.extend(["CRM系统", "客户数据库"])
        elif employee.role == "HR人员":
            login_sequence.extend(["HR系统", "薪酬系统"])
        
        # 按逻辑顺序登录系统
        current_time = start_time
        for i, system in enumerate(login_sequence):
            if system in employee.system_permissions:
                # 登录时间间隔2-5分钟
                current_time += timedelta(minutes=random.randint(2, 5))
                
                access_log = SystemAccessLog(employee.employee_id, system, "登录")
                access_log.timestamp = current_time
                access_log.result = "成功"
                
                # 更新用户会话状态
                self._update_user_session(employee.employee_id, system, "login", current_time)
                
                self.access_logs.append(access_log)
                self._log_with_context(access_log, f"员工{employee.name}开始工作日，登录{system}")
                logs_count += 1
        
        return logs_count
    
    def _generate_business_operations_sequence(self, employee, start_time, end_time):
        """生成工作时间业务操作序列"""
        logs_count = 0
        current_time = start_time + timedelta(minutes=30)  # 登录后30分钟开始业务操作
        
        # 根据角色生成特定的业务流程
        business_flows = self._get_role_specific_business_flows(employee.role)
        
        while current_time < end_time:
            # 选择业务流程
            flow = random.choice(business_flows)
            
            # 执行业务流程中的操作序列
            for operation in flow['operations']:
                if current_time >= end_time:
                    break
                
                system = operation['system']
                if system in employee.system_permissions:
                    # 生成操作日志
                    access_log = SystemAccessLog(employee.employee_id, system, operation['action'])
                    access_log.timestamp = current_time
                    access_log.result = "成功" if random.random() > 0.05 else "失败"
                    
                    # 根据操作类型设置数据量
                    if "导出" in operation['action'] or "下载" in operation['action']:
                        access_log.data_volume = random.randint(1000, 50000)
                    elif "查询" in operation['action']:
                        access_log.data_volume = random.randint(10, 100)
                    
                    self.access_logs.append(access_log)
                    self._log_with_context(access_log, f"员工{employee.name}执行业务操作: {operation['action']}")
                    logs_count += 1
                    
                    # 操作间隔时间
                    current_time += timedelta(minutes=random.randint(5, 30))
            
            # 流程间隔时间
            current_time += timedelta(minutes=random.randint(15, 60))
        
        return logs_count
    
    def _generate_evening_logout_sequence(self, employee, end_time):
        """生成下班登出序列"""
        logs_count = 0
        
        # 获取当天已登录的系统
        logged_in_systems = self._get_user_active_sessions(employee.employee_id)
        
        # 按相反顺序登出系统
        logout_time = end_time
        for system in reversed(logged_in_systems):
            access_log = SystemAccessLog(employee.employee_id, system, "登出")
            access_log.timestamp = logout_time
            access_log.result = "成功"
            
            # 更新会话状态
            self._update_user_session(employee.employee_id, system, "logout", logout_time)
            
            self.access_logs.append(access_log)
            self._log_with_context(access_log, f"员工{employee.name}下班，登出{system}")
            logs_count += 1
            
            logout_time += timedelta(minutes=random.randint(1, 3))
        
        return logs_count
    
    def _generate_pre_resignation_activities(self, employee, start_time, end_time):
        """生成离职前的异常活动序列"""
        logs_count = 0
        
        # 只有高风险员工才可能产生异常行为
        if employee.resignation_risk_score > 0.6:
            # 检查是否触发异常行为
            for anomaly in employee.anomaly_history:
                if anomaly['phase'] == 'pre_resignation' and not anomaly.get('logged', False):
                    logs_count += self._execute_anomaly_sequence(employee, anomaly, start_time, end_time)
                    anomaly['logged'] = True
        
        return logs_count
    
    def _execute_anomaly_sequence(self, employee, anomaly, start_time, end_time):
        """执行异常行为序列"""
        logs_count = 0
        anomaly_type = anomaly['type']
        
        if anomaly_type == "大量下载":
            # 生成大量下载操作的时间序列
            download_time = start_time + timedelta(hours=random.uniform(2, 6))
            target_systems = ["文档管理", "客户数据库", "代码仓库"]
            
            for system in target_systems:
                if system in employee.system_permissions:
                    for i in range(random.randint(5, 15)):
                        access_log = SystemAccessLog(employee.employee_id, system, "大量下载文件", is_anomalous=True)
                        access_log.timestamp = download_time + timedelta(minutes=i*2)
                        access_log.data_volume = random.randint(10000, 100000)  # 大数据量
                        access_log.result = "成功"
                        
                        self.access_logs.append(access_log)
                        self._create_anomaly_alert(employee, system, access_log, anomaly_type)
                        logs_count += 1
        
        elif anomaly_type == "频繁访问敏感系统":
            # 异常频繁访问
            sensitive_systems = ["财务系统", "HR系统", "薪酬系统"]
            access_time = start_time + timedelta(hours=random.uniform(1, 7))
            
            for _ in range(random.randint(20, 50)):
                system = random.choice([s for s in sensitive_systems if s in employee.system_permissions])
                if system:
                    access_log = SystemAccessLog(employee.employee_id, system, "频繁查询敏感信息", is_anomalous=True)
                    access_log.timestamp = access_time
                    access_log.result = "成功"
                    
                    self.access_logs.append(access_log)
                    logs_count += 1
                    access_time += timedelta(minutes=random.randint(1, 5))
        
        elif anomaly_type == "异常时间访问":
            # 非工作时间访问
            night_time = end_time + timedelta(hours=random.randint(2, 8))
            systems = list(employee.system_permissions.keys())
            
            for system in random.sample(systems, min(3, len(systems))):
                access_log = SystemAccessLog(employee.employee_id, system, "深夜访问系统", is_anomalous=True)
                access_log.timestamp = night_time
                access_log.result = "成功"
                
                self.access_logs.append(access_log)
                self._create_anomaly_alert(employee, system, access_log, anomaly_type)
                logs_count += 1
                night_time += timedelta(minutes=random.randint(10, 30))
        
        return logs_count
    
    def _generate_violation_access_sequence(self, employee, date):
        """为已离职员工生成违规访问序列"""
        logs_count = 0
        
        # 计算离职后天数
        days_since_resignation = (date.date() - employee.last_work_date.date()).days
        
        # 生成违规访问的时间序列
        violation_scenarios = [
            {"time": "深夜", "hour_range": (22, 4), "risk_multiplier": 2.0},
            {"time": "周末", "hour_range": (9, 17), "risk_multiplier": 1.5},
            {"time": "工作时间", "hour_range": (9, 17), "risk_multiplier": 1.0}
        ]
        
        scenario = random.choice(violation_scenarios)
        
        # 选择违规访问时间
        if scenario["time"] == "深夜":
            hour = random.randint(22, 23) if random.random() > 0.5 else random.randint(0, 4)
        else:
            hour = random.randint(*scenario["hour_range"])
        
        violation_time = date.replace(hour=hour, minute=random.randint(0, 59))
        
        # 生成违规访问序列
        violation_patterns = [
            self._attempt_credential_reuse,
            self._attempt_vpn_access,
            self._attempt_system_backdoor,
            self._social_engineering_attempt
        ]
        
        selected_pattern = random.choice(violation_patterns)
        logs_count += selected_pattern(employee, violation_time, days_since_resignation)
        
        return logs_count
    
    def _attempt_credential_reuse(self, employee, violation_time, days_since_resignation):
        """尝试重用凭据"""
        logs_count = 0
        
        # 尝试访问原有系统
        for system in random.sample(list(employee.system_permissions.keys()), min(3, len(employee.system_permissions))):
            for attempt in range(random.randint(1, 5)):
                access_log = SystemAccessLog(employee.employee_id, system, "尝试登录", is_anomalous=True)
                access_log.timestamp = violation_time + timedelta(minutes=attempt * 2)
                access_log.result = "被拒绝" if attempt > 0 else random.choice(["成功", "失败", "被拒绝"])
                access_log.ip_address = f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"  # 外网IP
                
                self.access_logs.append(access_log)
                
                if access_log.result == "成功":
                    self._create_severe_violation_alert(employee, system, access_log, "离职后账号访问", days_since_resignation)
                
                logs_count += 1
        
        return logs_count
    
    def _attempt_vpn_access(self, employee, violation_time, days_since_resignation):
        """尝试VPN访问"""
        logs_count = 0
        
        # 生成VPN暴力破解序列
        for attempt in range(random.randint(10, 50)):
            access_log = SystemAccessLog(employee.employee_id, "VPN", "暴力破解登录", is_anomalous=True)
            access_log.timestamp = violation_time + timedelta(seconds=attempt * 30)
            access_log.result = "失败"
            access_log.ip_address = f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            
            self.access_logs.append(access_log)
            logs_count += 1
            
            if attempt == 0:  # 第一次尝试时记录告警
                self._create_severe_violation_alert(employee, "VPN", access_log, "VPN暴力破解", days_since_resignation)
        
        return logs_count
    
    def _attempt_system_backdoor(self, employee, violation_time, days_since_resignation):
        """尝试系统后门访问"""
        logs_count = 0
        
        if employee.role == "技术人员":
            # 技术人员可能尝试后门访问
            backdoor_systems = ["生产环境", "监控系统", "备份系统"]
            
            for system in backdoor_systems:
                if system in employee.system_permissions:
                    access_log = SystemAccessLog(employee.employee_id, system, "后门访问尝试", is_anomalous=True)
                    access_log.timestamp = violation_time
                    access_log.result = random.choice(["成功", "失败", "被拒绝"])
                    access_log.ip_address = f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                    
                    self.access_logs.append(access_log)
                    self._create_severe_violation_alert(employee, system, access_log, "恶意软件植入", days_since_resignation)
                    logs_count += 1
        
        return logs_count
    
    def _social_engineering_attempt(self, employee, violation_time, days_since_resignation):
        """社会工程学攻击尝试"""
        logs_count = 0
        
        # 使用其他员工账号尝试访问
        active_employees = list(self.hr_system.employees.values())
        if active_employees:
            target_employee = random.choice(active_employees)
            
            # 模拟使用他人账号访问
            access_log = SystemAccessLog(target_employee.employee_id, "邮件系统", "可疑邮件发送", is_anomalous=True)
            access_log.timestamp = violation_time
            access_log.result = "成功"
            # 但IP地址显示异常
            access_log.ip_address = f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            
            self.access_logs.append(access_log)
            self._create_severe_violation_alert(employee, "邮件系统", access_log, "社会工程学攻击", days_since_resignation)
            logs_count += 1
        
        return logs_count
    
    def _get_role_specific_business_flows(self, role):
        """获取角色特定的业务流程"""
        business_flows = {
            "技术人员": [
                {
                    "name": "代码开发流程",
                    "operations": [
                        {"system": "代码仓库", "action": "拉取最新代码"},
                        {"system": "代码仓库", "action": "提交代码"},
                        {"system": "生产环境", "action": "部署应用"},
                        {"system": "监控系统", "action": "检查部署状态"}
                    ]
                },
                {
                    "name": "系统维护流程",
                    "operations": [
                        {"system": "监控系统", "action": "查看系统监控"},
                        {"system": "生产环境", "action": "查看系统日志"},
                        {"system": "备份系统", "action": "检查备份状态"}
                    ]
                }
            ],
            "财务人员": [
                {
                    "name": "财务处理流程",
                    "operations": [
                        {"system": "财务系统", "action": "查询财务数据"},
                        {"system": "ERP系统", "action": "录入财务凭证"},
                        {"system": "财务系统", "action": "生成财务报表"},
                        {"system": "财务报表系统", "action": "审核财务报告"}
                    ]
                },
                {
                    "name": "薪酬处理流程",
                    "operations": [
                        {"system": "HR系统", "action": "获取考勤数据"},
                        {"system": "薪酬系统", "action": "计算薪酬"},
                        {"system": "财务系统", "action": "确认薪酬支付"}
                    ]
                }
            ],
            "销售人员": [
                {
                    "name": "客户管理流程",
                    "operations": [
                        {"system": "CRM系统", "action": "查询客户信息"},
                        {"system": "客户数据库", "action": "更新客户资料"},
                        {"system": "合同管理系统", "action": "创建销售合同"}
                    ]
                },
                {
                    "name": "销售报告流程",
                    "operations": [
                        {"system": "CRM系统", "action": "统计销售数据"},
                        {"system": "客户数据库", "action": "分析客户行为"},
                        {"system": "CRM系统", "action": "生成销售报告"}
                    ]
                }
            ],
            "HR人员": [
                {
                    "name": "人事管理流程",
                    "operations": [
                        {"system": "HR系统", "action": "查询员工信息"},
                        {"system": "HR系统", "action": "更新员工档案"},
                        {"system": "薪酬系统", "action": "维护薪酬结构"}
                    ]
                },
                {
                    "name": "离职处理流程",
                    "operations": [
                        {"system": "HR系统", "action": "处理离职申请"},
                        {"system": "薪酬系统", "action": "计算离职补偿"},
                        {"system": "HR系统", "action": "更新员工状态"}
                    ]
                }
            ]
        }
        
        return business_flows.get(role, [
            {
                "name": "一般办公流程",
                "operations": [
                    {"system": "邮件系统", "action": "查看邮件"},
                    {"system": "OA系统", "action": "处理审批"},
                    {"system": "文档管理", "action": "查看文档"}
                ]
            }
        ])
    
    def _update_user_session(self, user_id, system, action, timestamp):
        """更新用户会话状态"""
        if user_id not in self.user_session_states:
            self.user_session_states[user_id] = {}
        
        if action == "login":
            self.user_session_states[user_id][system] = {
                "login_time": timestamp,
                "status": "active"
            }
        elif action == "logout":
            if system in self.user_session_states[user_id]:
                self.user_session_states[user_id][system]["logout_time"] = timestamp
                self.user_session_states[user_id][system]["status"] = "inactive"
    
    def _get_user_active_sessions(self, user_id):
        """获取用户当前活跃会话"""
        if user_id not in self.user_session_states:
            return []
        
        active_systems = []
        for system, session in self.user_session_states[user_id].items():
            if session.get("status") == "active":
                active_systems.append(system)
        
        return active_systems
    
    def _log_with_context(self, access_log, context_message):
        """带上下文信息记录访问日志"""
        logger_manager.log_system_access(
            access_log.user_id,
            access_log.system,
            access_log.action_type,
            access_log.result,
            access_log.ip_address,
            access_log.risk_score,
            access_log.is_suspicious
        )
        
        if access_log.is_suspicious:
            logger_manager.log_anomaly_detection(
                access_log.action_type,
                access_log.user_id,
                access_log.risk_score,
                {
                    "context": context_message,
                    "data_volume": access_log.data_volume,
                    "geolocation": access_log.geolocation,
                    "device_fingerprint": access_log.device_fingerprint
                },
                access_log.system
            )
    
    def _create_anomaly_alert(self, employee, system, access_log, anomaly_type):
        """创建异常告警"""
        logger_manager.log_violation_alert(
            employee.employee_id,
            anomaly_type,
            system,
            f"检测到{employee.name}({employee.role})的异常行为：{anomaly_type}，"
            f"访问时间：{access_log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}，"
            f"数据量：{access_log.data_volume}KB"
        )
    
    def _create_severe_violation_alert(self, employee, system, access_log, violation_type, days_since_resignation):
        """创建严重违规告警"""
        alert_details = {
            "employee_name": employee.name,
            "employee_role": employee.role,
            "department": employee.department,
            "resignation_date": employee.last_work_date.isoformat() if employee.last_work_date else None,
            "days_since_resignation": days_since_resignation,
            "access_timestamp": access_log.timestamp.isoformat(),
            "access_result": access_log.result,
            "ip_address": access_log.ip_address,
            "geolocation": access_log.geolocation,
            "risk_assessment": employee.get_risk_assessment()
        }
        
        logger_manager.log_violation_alert(
            employee.employee_id,
            violation_type,
            system,
            alert_details
        )
        
        # 同时记录为安全事件
        logger_manager.log_security_incident(
            violation_type,
            employee.employee_id,
            "极高",
            alert_details,
            [system]
        )
    
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
        
        # 根据员工风险评分调整概率
        adjusted_probability = violation_probability * employee.resignation_risk_score
        
        return random.random() < adjusted_probability
    
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
        high_risk_alerts = len([alert for alert in self.violation_alerts if alert.get('risk_level') in ['高', '极高']])
        
        # 按违规类型统计
        violation_types = {}
        for alert in self.violation_alerts:
            vtype = alert.get('violation_type', '未知')
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        # 按系统统计
        system_violations = {}
        for alert in self.violation_alerts:
            system = alert.get('system', '未知')
            system_violations[system] = system_violations.get(system, 0) + 1
        
        stats = {
            "total_violation_alerts": total_alerts,
            "high_risk_alerts": high_risk_alerts,
            "violation_by_type": violation_types,
            "violation_by_system": system_violations,
            "pending_alerts": len([alert for alert in self.violation_alerts if alert.get('status') == '待处理'])
        }
        
        return stats 