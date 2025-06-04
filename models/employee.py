#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工数据模型
"""

import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from config import SYSTEM_CONFIG, TIME_CONFIG

fake = Faker('zh_CN')

class Employee:
    """员工信息模型"""
    
    def __init__(self, employee_id=None):
        self.employee_id = employee_id or f"EMP{random.randint(100000, 999999)}"
        self.name = fake.name()
        self.department = random.choice(SYSTEM_CONFIG['departments'])
        self.position = fake.job()
        self.hire_date = fake.date_between(start_date='-5y', end_date='today')
        self.email = f"{self.employee_id.lower()}@company.com"
        self.phone = fake.phone_number()
        self.status = "在职"  # 在职、离职申请、已离职
        
        # 离职相关信息
        self.resignation_date = None
        self.last_work_date = None
        self.resignation_reason = None
        self.resignation_type = None  # 主动离职、被动离职
        
        # 账号信息
        self.accounts = self._generate_accounts()
        
        # 系统访问权限
        self.system_permissions = self._generate_permissions()
    
    def _generate_accounts(self):
        """生成员工账号信息"""
        accounts = {}
        for account_type in SYSTEM_CONFIG['account_types']:
            for system in SYSTEM_CONFIG['access_systems']:
                if random.random() > 0.3:  # 70%概率拥有该系统账号
                    account_id = f"{self.employee_id}_{system.replace('系统', '')}"
                    accounts[f"{system}_{account_type}"] = {
                        "account_id": account_id,
                        "account_type": account_type,
                        "system": system,
                        "status": "active",
                        "created_date": self.hire_date,
                        "last_login": fake.date_time_between(start_date='-30d', end_date='now')
                    }
        return accounts
    
    def _generate_permissions(self):
        """生成系统权限信息"""
        permissions = {}
        for system in SYSTEM_CONFIG['access_systems']:
            if random.random() > 0.2:  # 80%概率拥有该系统权限
                permissions[system] = {
                    "access_level": random.choice(["读取", "读写", "管理员"]),
                    "granted_date": self.hire_date,
                    "expiry_date": None,
                    "status": "active"
                }
        return permissions
    
    def initiate_resignation(self, resignation_type="主动离职", reason=None):
        """发起离职申请"""
        self.status = "离职申请"
        self.resignation_type = resignation_type
        self.resignation_date = datetime.now()
        self.last_work_date = self.resignation_date + timedelta(days=TIME_CONFIG['resignation_notice_days'])
        self.resignation_reason = reason or random.choice([
            "个人发展", "薪酬待遇", "工作环境", "家庭原因", "健康原因", "继续深造"
        ])
    
    def complete_resignation(self):
        """完成离职"""
        self.status = "已离职"
        # 禁用所有账号
        for account_key, account_info in self.accounts.items():
            account_info['status'] = 'disabled'
            account_info['disabled_date'] = datetime.now()
        
        # 撤销所有系统权限
        for system, permission in self.system_permissions.items():
            permission['status'] = 'revoked'
            permission['revoked_date'] = datetime.now()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "department": self.department,
            "position": self.position,
            "hire_date": self.hire_date.isoformat() if isinstance(self.hire_date, datetime) else str(self.hire_date),
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "resignation_date": self.resignation_date.isoformat() if self.resignation_date else None,
            "last_work_date": self.last_work_date.isoformat() if self.last_work_date else None,
            "resignation_reason": self.resignation_reason,
            "resignation_type": self.resignation_type,
            "accounts": self.accounts,
            "system_permissions": self.system_permissions
        }

class AccountTransferRecord:
    """账号移交记录模型"""
    
    def __init__(self, employee_id, account_info, transfer_to=None):
        self.record_id = str(uuid.uuid4())
        self.employee_id = employee_id
        self.account_id = account_info['account_id']
        self.account_type = account_info['account_type']
        self.system = account_info['system']
        self.transfer_to = transfer_to or f"ADMIN_{random.randint(1000, 9999)}"
        self.transfer_date = datetime.now()
        self.transfer_status = random.choice(["待移交", "已移交", "移交失败"])
        self.notes = ""
    
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
            "notes": self.notes
        }

class SystemAccessLog:
    """系统访问日志模型"""
    
    def __init__(self, user_id, system, action_type=None):
        self.log_id = str(uuid.uuid4())
        self.user_id = user_id
        self.system = system
        self.action_type = action_type or random.choice([
            "登录", "登出", "文件访问", "数据查询", "数据修改", "权限操作"
        ])
        self.timestamp = datetime.now() - timedelta(
            minutes=random.randint(0, 60*24*7)  # 最近一周内的随机时间
        )
        self.ip_address = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
        self.user_agent = fake.user_agent()
        self.result = random.choice(["成功", "失败", "被拒绝"])
        self.resource = fake.file_path()
    
    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "system": self.system,
            "action_type": self.action_type,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "result": self.result,
            "resource": self.resource
        } 