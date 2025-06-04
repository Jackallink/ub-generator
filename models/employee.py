#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工数据模型 - 增强版，模拟真实企业环境
"""

import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from config import (SYSTEM_CONFIG, TIME_CONFIG, EMPLOYEE_ROLES, 
                   ENTERPRISE_SYSTEMS, RESIGNATION_REASONS, ANOMALY_PATTERNS, 
                   REALISTIC_SCENARIOS, RISK_SCORING)
import json

fake = Faker('zh_CN')

class Employee:
    """员工信息模型 - 真实企业场景版本"""
    
    def __init__(self, employee_id=None):
        self.employee_id = employee_id or f"EMP{random.randint(100000, 999999)}"
        self.name = fake.name()
        
        # 随机分配员工角色和部门
        self.role, self.role_config = self._assign_employee_role()
        self.department = random.choice(self.role_config['departments'])
        self.position = self._generate_realistic_position()
        
        # 基础信息
        self.hire_date = fake.date_between(start_date='-5y', end_date='today')
        self.email = f"{self.employee_id.lower()}@company.com"
        self.phone = fake.phone_number()
        self.status = "在职"  # 在职、离职申请、已离职
        
        # 员工特征
        self.performance_rating = random.choice(["优秀", "良好", "合格", "待改进"])
        self.security_clearance = self._assign_security_clearance()
        self.risk_profile = self.role_config['risk_profile']
        self.monitoring_level = self.role_config['monitoring_level']
        
        # 离职相关信息
        self.resignation_date = None
        self.last_work_date = None
        self.resignation_reason = None
        self.resignation_type = None  # 主动离职、被动离职
        self.resignation_risk_score = 0.0
        self.is_urgent_resignation = False
        
        # 账号信息
        self.accounts = self._generate_realistic_accounts()
        
        # 系统访问权限
        self.system_permissions = self._generate_realistic_permissions()
        
        # 行为特征
        self.behavior_profile = self._generate_behavior_profile()
        
        # 异常行为记录
        self.anomaly_history = []
        self.security_incidents = []
    
    def _assign_employee_role(self):
        """分配员工角色"""
        # 根据真实企业比例分配角色
        role_weights = {
            "高管": 0.02,
            "财务人员": 0.08,
            "技术人员": 0.25,
            "销售人员": 0.20,
            "HR人员": 0.05,
            "一般员工": 0.40
        }
        
        roles = list(role_weights.keys())
        weights = list(role_weights.values())
        selected_role = random.choices(roles, weights=weights)[0]
        
        return selected_role, EMPLOYEE_ROLES[selected_role]
    
    def _generate_realistic_position(self):
        """生成真实的职位名称"""
        position_mapping = {
            "高管": ["CEO", "CTO", "CFO", "COO", "副总裁", "总监"],
            "财务人员": ["财务经理", "会计", "出纳", "财务分析师", "税务专员", "审计师"],
            "技术人员": ["软件工程师", "架构师", "运维工程师", "测试工程师", "产品经理", "UI设计师", "数据分析师"],
            "销售人员": ["销售经理", "客户经理", "市场专员", "商务拓展", "销售代表", "区域经理"],
            "HR人员": ["HR经理", "招聘专员", "薪酬专员", "培训专员", "HRBP", "人事助理"],
            "一般员工": ["行政助理", "法务专员", "运营专员", "文档管理员", "前台", "秘书"]
        }
        
        return random.choice(position_mapping[self.role])
    
    def _assign_security_clearance(self):
        """分配安全等级"""
        clearance_mapping = {
            "高管": random.choices(["机密", "秘密"], weights=[0.8, 0.2])[0],
            "财务人员": random.choices(["秘密", "内部"], weights=[0.7, 0.3])[0],
            "技术人员": random.choices(["机密", "秘密"], weights=[0.6, 0.4])[0],
            "销售人员": random.choices(["秘密", "内部"], weights=[0.5, 0.5])[0],
            "HR人员": random.choices(["机密", "秘密"], weights=[0.8, 0.2])[0],
            "一般员工": random.choices(["内部", "公开"], weights=[0.8, 0.2])[0]
        }
        
        return clearance_mapping[self.role]
    
    def _generate_realistic_accounts(self):
        """生成真实的账号信息"""
        accounts = {}
        
        # 所有员工都有的基础账号
        base_accounts = ["域账号", "邮箱账号"]
        
        # 根据角色分配特殊账号
        role_specific_accounts = {
            "高管": ["特权账号", "VPN账号"],
            "财务人员": ["数据库账号", "应用账号"],
            "技术人员": ["特权账号", "VPN账号", "数据库账号"],
            "销售人员": ["VPN账号", "应用账号"],
            "HR人员": ["数据库账号", "应用账号"],
            "一般员工": ["应用账号"]
        }
        
        all_account_types = base_accounts + role_specific_accounts.get(self.role, [])
        
        # 为每种账号类型在相关系统中创建账号
        available_systems = self.role_config.get('systems_access', [])
        if "全部" in available_systems:
            available_systems = SYSTEM_CONFIG['access_systems']
        
        for account_type in all_account_types:
            for system in available_systems:
                if self._should_have_account(system, account_type):
                    account_id = f"{self.employee_id}_{system.replace('系统', '').replace('环境', '')}"
                    accounts[f"{system}_{account_type}"] = {
                        "account_id": account_id,
                        "account_type": account_type,
                        "system": system,
                        "status": "active",
                        "created_date": self.hire_date,
                        "last_login": fake.date_time_between(start_date='-30d', end_date='now'),
                        "login_count": random.randint(1, 500),
                        "failed_login_attempts": random.randint(0, 3),
                        "is_privileged": account_type in ["特权账号", "数据库账号"]
                    }
        
        return accounts
    
    def _should_have_account(self, system, account_type):
        """判断是否应该在指定系统拥有指定类型的账号"""
        # 获取系统信息
        system_info = None
        for category in ENTERPRISE_SYSTEMS.values():
            if system in category:
                system_info = category[system]
                break
        
        if not system_info:
            return random.random() > 0.3
        
        # 根据角色和系统敏感性决定
        if system_info['sensitivity'] == "极高":
            if account_type == "特权账号":
                return self.role in ["高管", "技术人员", "财务人员"]
            else:
                return self.role in ["高管", "技术人员", "财务人员", "HR人员"]
        elif system_info['sensitivity'] == "高":
            return self.role != "一般员工" or random.random() > 0.5
        else:
            return random.random() > 0.2
    
    def _generate_realistic_permissions(self):
        """生成真实的系统权限"""
        permissions = {}
        
        available_systems = self.role_config.get('systems_access', [])
        if "全部" in available_systems:
            available_systems = SYSTEM_CONFIG['access_systems']
        
        for system in available_systems:
            if random.random() > 0.1:  # 90%概率拥有权限
                permissions[system] = {
                    "access_level": self._determine_access_level(system),
                    "granted_date": self.hire_date,
                    "granted_by": f"MGR_{random.randint(1000, 9999)}",
                    "expiry_date": None,
                    "status": "active",
                    "business_justification": self._generate_business_justification(system),
                    "last_review_date": fake.date_between(start_date='-1y', end_date='today')
                }
        
        return permissions
    
    def _determine_access_level(self, system):
        """根据角色和系统确定访问级别"""
        if self.role == "高管":
            return random.choices(["管理员", "读写", "读取"], weights=[0.6, 0.3, 0.1])[0]
        elif self.role in ["技术人员", "财务人员", "HR人员"]:
            return random.choices(["管理员", "读写", "读取"], weights=[0.3, 0.5, 0.2])[0]
        else:
            return random.choices(["读写", "读取"], weights=[0.3, 0.7])[0]
    
    def _generate_business_justification(self, system):
        """生成业务合理性说明"""
        justifications = {
            "ERP系统": "日常业务处理需要",
            "财务系统": "财务数据查询和报表生成",
            "CRM系统": "客户关系管理",
            "HR系统": "人力资源管理",
            "代码仓库": "软件开发和代码管理",
            "生产环境": "生产系统运维",
            "客户数据库": "客户信息查询",
            "邮件系统": "日常工作沟通",
            "VPN": "远程办公访问"
        }
        
        return justifications.get(system, "业务工作需要")
    
    def _generate_behavior_profile(self):
        """生成员工行为档案"""
        return {
            "work_pattern": self._generate_work_pattern(),
            "system_usage": self._generate_system_usage_pattern(),
            "risk_indicators": self._generate_risk_indicators(),
            "communication_style": random.choice(["主动", "被动", "正常"]),
            "collaboration_level": random.choice(["高", "中", "低"]),
            "learning_attitude": random.choice(["积极", "一般", "消极"])
        }
    
    def _generate_work_pattern(self):
        """生成工作模式"""
        scenarios = REALISTIC_SCENARIOS['typical_workday']
        return {
            "typical_start_time": scenarios['start_hour'] + random.uniform(-1, 1),
            "typical_end_time": scenarios['end_hour'] + random.uniform(-2, 3),
            "overtime_frequency": random.choices(["经常", "偶尔", "很少"], weights=[0.3, 0.5, 0.2])[0],
            "weekend_work": random.choices(["是", "否"], weights=[scenarios['weekend_work_probability'], 1-scenarios['weekend_work_probability']])[0],
            "remote_work_preference": random.choices(["高", "中", "低"], weights=[0.3, 0.4, 0.3])[0]
        }
    
    def _generate_system_usage_pattern(self):
        """生成系统使用模式"""
        return {
            "daily_login_frequency": random.randint(3, 20),
            "session_duration_avg": random.uniform(0.5, 8.0),  # 小时
            "preferred_access_time": random.choice(["早晨", "上午", "下午", "晚上"]),
            "multi_system_usage": random.choices(["是", "否"], weights=[0.7, 0.3])[0],
            "mobile_access": random.choices(["经常", "偶尔", "从不"], weights=[0.4, 0.4, 0.2])[0]
        }
    
    def _generate_risk_indicators(self):
        """生成风险指标"""
        base_risk = 0.1
        
        # 根据角色调整风险
        role_risk_adjustment = {
            "高管": 0.3,
            "技术人员": 0.25, 
            "财务人员": 0.2,
            "HR人员": 0.2,
            "销售人员": 0.15,
            "一般员工": 0.05
        }
        
        # 根据绩效调整风险
        performance_risk = {
            "优秀": -0.05,
            "良好": 0.0,
            "合格": 0.05,
            "待改进": 0.15
        }
        
        total_risk = base_risk + role_risk_adjustment[self.role] + performance_risk[self.performance_rating]
        
        return {
            "overall_risk_score": min(1.0, max(0.0, total_risk)),
            "data_sensitivity_access": self.role in ["高管", "技术人员", "财务人员", "HR人员"],
            "privileged_access": any(acc.get('is_privileged', False) for acc in self.accounts.values()),
            "external_network_access": "VPN" in [acc['system'] for acc in self.accounts.values()],
            "performance_issues": self.performance_rating == "待改进"
        }
    
    def initiate_resignation(self, resignation_type=None, reason=None, is_urgent=False):
        """发起离职申请 - 增强版"""
        self.status = "离职申请"
        self.is_urgent_resignation = is_urgent
        
        # 确定离职类型
        if not resignation_type:
            resignation_type = random.choices(
                ["主动离职", "被动离职"], 
                weights=[0.7, 0.3]
            )[0]
        
        self.resignation_type = resignation_type
        
        # 确定离职原因
        if not reason:
            reason_category = RESIGNATION_REASONS[resignation_type]
            reasons = list(reason_category.keys())
            probabilities = [reason_category[r]['probability'] for r in reasons]
            reason = random.choices(reasons, weights=probabilities)[0]
        
        self.resignation_reason = reason
        self.resignation_date = datetime.now()
        
        # 确定最后工作日
        if is_urgent:
            notice_days = TIME_CONFIG['urgent_resignation_days']
        else:
            notice_days = TIME_CONFIG['resignation_notice_days']
        
        self.last_work_date = self.resignation_date + timedelta(days=notice_days)
        
        # 计算风险评分
        self.resignation_risk_score = self._calculate_resignation_risk()
        
        # 可能触发离职前异常行为
        self._potentially_trigger_pre_resignation_anomalies()
    
    def _calculate_resignation_risk(self):
        """计算离职风险评分"""
        weights = RISK_SCORING
        
        # 角色风险
        role_risk_scores = {
            "高管": 0.9,
            "技术人员": 0.8,
            "财务人员": 0.8,
            "HR人员": 0.8,
            "销售人员": 0.6,
            "一般员工": 0.3
        }
        role_score = role_risk_scores[self.role]
        
        # 系统敏感性风险
        max_sensitivity = 0
        for system in self.system_permissions.keys():
            for category in ENTERPRISE_SYSTEMS.values():
                if system in category:
                    sensitivity_scores = {"极高": 1.0, "高": 0.7, "中": 0.4, "低": 0.2}
                    max_sensitivity = max(max_sensitivity, 
                                        sensitivity_scores.get(category[system]['sensitivity'], 0.2))
        
        # 离职原因风险
        reason_risk = RESIGNATION_REASONS[self.resignation_type][self.resignation_reason]['risk_multiplier'] / 3.0
        
        # 行为模式风险
        behavior_risk = self.behavior_profile['risk_indicators']['overall_risk_score']
        
        # 时间因素风险（紧急离职风险更高）
        timing_risk = 0.8 if self.is_urgent_resignation else 0.3
        
        # 计算总风险评分
        total_risk = (
            role_score * weights['employee_role_weight'] +
            max_sensitivity * weights['system_sensitivity_weight'] +
            reason_risk * weights['resignation_reason_weight'] +
            behavior_risk * weights['behavior_pattern_weight'] +
            timing_risk * weights['timing_weight']
        )
        
        return min(1.0, total_risk)
    
    def _potentially_trigger_pre_resignation_anomalies(self):
        """可能触发离职前异常行为"""
        anomalies = ANOMALY_PATTERNS['pre_resignation']
        
        for anomaly_type, config in anomalies.items():
            # 根据风险评分调整异常概率
            adjusted_probability = config['probability'] * self.resignation_risk_score
            
            if random.random() < adjusted_probability:
                self._record_anomaly("pre_resignation", anomaly_type, config)
    
    def _record_anomaly(self, phase, anomaly_type, config):
        """记录异常行为"""
        anomaly = {
            "anomaly_id": str(uuid.uuid4()),
            "phase": phase,
            "type": anomaly_type,
            "severity": config['severity'],
            "description": config['description'],
            "timestamp": datetime.now(),
            "detected": random.random() < 0.85,  # 85%检测率
            "false_positive": random.random() < 0.05  # 5%误报率
        }
        
        self.anomaly_history.append(anomaly)
    
    def complete_resignation(self):
        """完成员工离职流程 - 增强版"""
        self.status = "已离职"
        
        # 模拟流程异常
        process_anomalies = ANOMALY_PATTERNS['process_anomalies']
        for anomaly_type, config in process_anomalies.items():
            if random.random() < config['probability']:
                self._record_anomaly("process", anomaly_type, config)
        
        # 处理账号禁用
        for account_key, account_info in self.accounts.items():
            # 检查是否存在禁用遗漏
            if random.random() < 0.25:  # 25%概率遗漏
                account_info['status'] = 'active'  # 遗漏禁用
                account_info['disabled_date'] = None
                account_info['disable_reason'] = "禁用遗漏"
            else:
                account_info['status'] = 'disabled'
                account_info['disabled_date'] = datetime.now()
                account_info['disable_reason'] = "员工离职"
        
        # 处理权限撤销
        for system, permission in self.system_permissions.items():
            # 检查是否存在权限回收延迟
            if random.random() < 0.30:  # 30%概率延迟
                # 延迟1-7天撤销
                delay_days = random.randint(1, 7)
                permission['status'] = 'active'  # 暂时保持激活
                permission['scheduled_revoke_date'] = datetime.now() + timedelta(days=delay_days)
            else:
                permission['status'] = 'revoked'
                permission['revoked_date'] = datetime.now()
                permission['revoked_by'] = f"SYS_AUTO_{random.randint(1000, 9999)}"
    
    def simulate_post_resignation_activities(self):
        """模拟离职后活动"""
        if self.status != "已离职":
            return []
        
        post_anomalies = []
        anomalies = ANOMALY_PATTERNS['post_resignation']
        
        for anomaly_type, config in anomalies.items():
            # 根据风险评分和离职原因调整概率
            risk_multiplier = RESIGNATION_REASONS[self.resignation_type][self.resignation_reason]['risk_multiplier']
            adjusted_probability = config['probability'] * self.resignation_risk_score * risk_multiplier
            
            if random.random() < adjusted_probability:
                anomaly = self._record_anomaly("post_resignation", anomaly_type, config)
                post_anomalies.append(anomaly)
        
        return post_anomalies
    
    def get_risk_assessment(self):
        """获取风险评估报告"""
        risk_thresholds = RISK_SCORING['risk_thresholds']
        
        risk_level = "低风险"
        for level, threshold in sorted(risk_thresholds.items(), key=lambda x: x[1]):
            if self.resignation_risk_score >= threshold:
                risk_level = level
        
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "risk_score": self.resignation_risk_score,
            "risk_level": risk_level,
            "monitoring_level": self.monitoring_level,
            "resignation_type": self.resignation_type,
            "resignation_reason": self.resignation_reason,
            "is_urgent": self.is_urgent_resignation,
            "high_value_systems": [
                system for system in self.system_permissions.keys()
                if any(system in category and category[system]['sensitivity'] in ["极高", "高"] 
                      for category in ENTERPRISE_SYSTEMS.values())
            ],
            "privileged_accounts": [
                acc['account_id'] for acc in self.accounts.values() 
                if acc.get('is_privileged', False)
            ],
            "anomaly_count": len(self.anomaly_history),
            "security_incidents": len(self.security_incidents)
        }
    
    def to_dict(self):
        """转换为字典格式 - 增强版"""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "position": self.position,
            "hire_date": self.hire_date.isoformat() if isinstance(self.hire_date, datetime) else str(self.hire_date),
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "performance_rating": self.performance_rating,
            "security_clearance": self.security_clearance,
            "risk_profile": self.risk_profile,
            "monitoring_level": self.monitoring_level,
            "resignation_date": self.resignation_date.isoformat() if self.resignation_date else None,
            "last_work_date": self.last_work_date.isoformat() if self.last_work_date else None,
            "resignation_reason": self.resignation_reason,
            "resignation_type": self.resignation_type,
            "resignation_risk_score": self.resignation_risk_score,
            "is_urgent_resignation": self.is_urgent_resignation,
            "accounts": self.accounts,
            "system_permissions": self.system_permissions,
            "behavior_profile": self.behavior_profile,
            "anomaly_history": len(self.anomaly_history),
            "security_incidents": len(self.security_incidents)
        }

class AccountTransferRecord:
    """账号移交记录模型 - 增强版"""
    
    def __init__(self, employee_id, account_info, transfer_to=None):
        self.record_id = str(uuid.uuid4())
        self.employee_id = employee_id
        self.account_id = account_info['account_id']
        self.account_type = account_info['account_type']
        self.system = account_info['system']
        self.transfer_to = transfer_to or f"ADMIN_{random.randint(1000, 9999)}"
        self.transfer_date = datetime.now()
        
        # 增强的状态和风险评估
        self.transfer_status = self._determine_transfer_status(account_info)
        self.risk_level = self._assess_transfer_risk(account_info)
        self.urgency = "高" if account_info.get('is_privileged', False) else "中"
        self.business_impact = self._assess_business_impact(account_info)
        self.compliance_requirements = self._get_compliance_requirements(account_info)
        
        self.notes = self._generate_transfer_notes()
        self.verification_required = account_info.get('is_privileged', False)
        self.approval_status = "待审批" if self.verification_required else "自动批准"
    
    def _determine_transfer_status(self, account_info):
        """确定移交状态"""
        if account_info.get('is_privileged', False):
            # 特权账号移交更容易出现问题
            return random.choices(
                ["待移交", "已移交", "移交失败", "等待审批"], 
                weights=[0.4, 0.3, 0.2, 0.1]
            )[0]
        else:
            return random.choices(
                ["待移交", "已移交", "移交失败"], 
                weights=[0.3, 0.6, 0.1]
            )[0]
    
    def _assess_transfer_risk(self, account_info):
        """评估移交风险"""
        if account_info.get('is_privileged', False):
            return random.choice(["高", "极高"])
        elif account_info['system'] in ["财务系统", "HR系统", "代码仓库"]:
            return "高"
        else:
            return random.choice(["中", "低"])
    
    def _assess_business_impact(self, account_info):
        """评估业务影响"""
        high_impact_systems = ["ERP系统", "财务系统", "生产环境", "客户数据库"]
        if account_info['system'] in high_impact_systems:
            return "高"
        elif account_info.get('is_privileged', False):
            return "中"
        else:
            return "低"
    
    def _get_compliance_requirements(self, account_info):
        """获取合规要求"""
        requirements = []
        
        if account_info.get('is_privileged', False):
            requirements.append("特权账号审计")
        
        if account_info['system'] in ["财务系统", "HR系统"]:
            requirements.append("数据保护合规")
        
        if account_info['account_type'] == "数据库账号":
            requirements.append("数据访问记录保留")
        
        return requirements
    
    def _generate_transfer_notes(self):
        """生成移交备注"""
        notes_templates = [
            "正常移交流程",
            "需要业务方确认",
            "等待系统管理员处理",
            "涉及敏感数据，需额外审批",
            "账号已临时禁用",
            "移交给直接上级",
            "系统维护中，延迟处理"
        ]
        return random.choice(notes_templates)
    
    def to_dict(self):
        return {
            "record_id": self.record_id,
            "employee_id": self.employee_id,
            "account_id": self.account_id,
            "account_type": self.account_type,
            "system": self.system,
            "transfer_to": self.transfer_to,
            "transfer_date": self.transfer_date.isoformat(),
            "transfer_status": self.transfer_status,
            "risk_level": self.risk_level,
            "urgency": self.urgency,
            "business_impact": self.business_impact,
            "compliance_requirements": self.compliance_requirements,
            "notes": self.notes,
            "verification_required": self.verification_required,
            "approval_status": self.approval_status
        }

class SystemAccessLog:
    """系统访问日志模型 - 增强版"""
    
    def __init__(self, user_id, system, action_type=None, is_anomalous=False):
        self.log_id = str(uuid.uuid4())
        self.user_id = user_id
        self.system = system
        self.action_type = action_type or self._generate_realistic_action(system)
        self.timestamp = datetime.now() - timedelta(
            minutes=random.randint(0, 60*24*7)  # 最近一周内的随机时间
        )
        
        # 网络信息
        self.ip_address = self._generate_realistic_ip()
        self.user_agent = fake.user_agent()
        self.session_id = f"sess_{self.timestamp.strftime('%Y%m%d%H%M%S')}_{user_id}"
        
        # 访问结果和详情
        self.result = self._determine_access_result(is_anomalous)
        self.resource = self._generate_realistic_resource(system)
        self.data_volume = self._generate_data_volume()
        
        # 风险指标
        self.risk_score = self._calculate_access_risk(is_anomalous)
        self.is_suspicious = is_anomalous or self.risk_score > 0.7
        
        # 上下文信息
        self.geolocation = self._generate_geolocation()
        self.device_fingerprint = self._generate_device_fingerprint()
        
    def _generate_realistic_action(self, system):
        """根据系统生成真实的操作类型"""
        action_mapping = {
            "财务系统": ["查询报表", "录入凭证", "审批付款", "导出数据", "生成财务报告"],
            "HR系统": ["查询员工信息", "更新薪酬", "审批请假", "生成人事报表", "维护组织架构"],
            "代码仓库": ["提交代码", "拉取代码", "创建分支", "合并请求", "查看历史"],
            "生产环境": ["部署应用", "查看日志", "重启服务", "监控告警", "数据库备份"],
            "客户数据库": ["查询客户信息", "更新客户资料", "导出客户列表", "数据分析", "删除记录"],
            "邮件系统": ["发送邮件", "接收邮件", "搜索邮件", "删除邮件", "设置规则"],
            "VPN": ["建立连接", "断开连接", "传输数据", "访问内网", "下载文件"]
        }
        
        return random.choice(action_mapping.get(system, 
            ["登录", "登出", "文件访问", "数据查询", "数据修改", "权限操作"]))
    
    def _generate_realistic_ip(self):
        """生成真实的IP地址"""
        # 内网IP vs 外网IP
        if random.random() < 0.8:  # 80%内网访问
            return f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
        else:  # 20%外网访问
            return f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    
    def _determine_access_result(self, is_anomalous):
        """确定访问结果"""
        if is_anomalous:
            return random.choices(
                ["成功", "失败", "被拒绝", "超时"], 
                weights=[0.3, 0.3, 0.3, 0.1]
            )[0]
        else:
            return random.choices(
                ["成功", "失败", "被拒绝"], 
                weights=[0.85, 0.1, 0.05]
            )[0]
    
    def _generate_realistic_resource(self, system):
        """生成真实的资源路径"""
        resource_mapping = {
            "财务系统": ["/financial/reports", "/financial/vouchers", "/financial/accounts"],
            "HR系统": ["/hr/employees", "/hr/payroll", "/hr/attendance"],
            "代码仓库": ["/repos/project-a", "/repos/project-b", "/repos/shared-lib"],
            "生产环境": ["/apps/web-service", "/apps/api-gateway", "/apps/database"],
            "客户数据库": ["/customer/profiles", "/customer/transactions", "/customer/analytics"],
            "邮件系统": ["/mail/inbox", "/mail/sent", "/mail/archive"],
            "文档管理": ["/docs/contracts", "/docs/proposals", "/docs/templates"]
        }
        
        resources = resource_mapping.get(system, ["/app/data", "/app/config", "/app/logs"])
        return random.choice(resources) + f"/{fake.file_name()}"
    
    def _generate_data_volume(self):
        """生成数据传输量"""
        # KB为单位
        if self.action_type in ["导出数据", "下载文件", "数据备份"]:
            return random.randint(1000, 100000)  # 1MB-100MB
        elif self.action_type in ["查询", "登录", "登出"]:
            return random.randint(1, 100)  # 1KB-100KB
        else:
            return random.randint(10, 1000)  # 10KB-1MB
    
    def _calculate_access_risk(self, is_anomalous):
        """计算访问风险评分"""
        risk_score = 0.1  # 基础风险
        
        # 异常行为加分
        if is_anomalous:
            risk_score += 0.5
        
        # 时间因素
        hour = self.timestamp.hour
        if hour < 6 or hour > 22:  # 非正常工作时间
            risk_score += 0.3
        
        # IP地址因素
        if not self.ip_address.startswith("192.168"):  # 外网访问
            risk_score += 0.2
        
        # 访问结果因素
        if self.result in ["失败", "被拒绝"]:
            risk_score += 0.2
        
        # 数据量因素
        if self.data_volume > 50000:  # 大量数据传输
            risk_score += 0.3
        
        return min(1.0, risk_score)
    
    def _generate_geolocation(self):
        """生成地理位置信息"""
        cities = ["北京", "上海", "深圳", "广州", "杭州", "成都", "西安", "武汉"]
        return {
            "country": "中国",
            "city": random.choice(cities),
            "latitude": round(random.uniform(20, 50), 6),
            "longitude": round(random.uniform(70, 140), 6)
        }
    
    def _generate_device_fingerprint(self):
        """生成设备指纹"""
        os_list = ["Windows 10", "Windows 11", "macOS", "Ubuntu", "CentOS"]
        browsers = ["Chrome", "Firefox", "Safari", "Edge"]
        
        return {
            "os": random.choice(os_list),
            "browser": random.choice(browsers),
            "resolution": random.choice(["1920x1080", "1366x768", "2560x1440", "3840x2160"]),
            "timezone": "Asia/Shanghai",
            "language": "zh-CN"
        }
    
    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "system": self.system,
            "action_type": self.action_type,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "result": self.result,
            "resource": self.resource,
            "data_volume": self.data_volume,
            "risk_score": self.risk_score,
            "is_suspicious": self.is_suspicious,
            "geolocation": self.geolocation,
            "device_fingerprint": self.device_fingerprint
        } 