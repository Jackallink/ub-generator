#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR系统模拟器
"""

import random
import time
import json
from datetime import datetime, timedelta
from models.employee import Employee, AccountTransferRecord
from utils.logger import logger_manager
from config import SIMULATION_CONFIG, DATA_CONFIG, SYSTEM_CONFIG

class HRSystemSimulator:
    """HR系统模拟器"""
    
    def __init__(self):
        self.employees = {}
        self.resigned_employees = {}
        self.transfer_records = []
        self._initialize_employees()
        logger_manager.log_info("HR系统模拟器初始化完成")
    
    def _initialize_employees(self):
        """初始化员工数据"""
        logger_manager.log_info(f"开始初始化 {SIMULATION_CONFIG['total_employees']} 名员工数据")
        
        for i in range(SIMULATION_CONFIG['total_employees']):
            employee = Employee()
            self.employees[employee.employee_id] = employee
            
            # 记录员工创建日志
            logger_manager.log_hr_record(
                employee.employee_id,
                "员工入职",
                {
                    "name": employee.name,
                    "department": employee.department,
                    "position": employee.position,
                    "hire_date": employee.hire_date.isoformat() if hasattr(employee.hire_date, 'isoformat') else str(employee.hire_date)
                }
            )
        
        logger_manager.log_info(f"员工数据初始化完成，共 {len(self.employees)} 名员工")
    
    def process_daily_resignations(self):
        """处理每日离职申请"""
        # 计算每日离职人数（基于月离职率）
        daily_resignations = int(SIMULATION_CONFIG['total_employees'] * SIMULATION_CONFIG['resignation_rate'] / 30)
        daily_resignations = max(1, daily_resignations)  # 至少1人
        
        # 随机选择离职员工
        active_employees = [emp for emp in self.employees.values() if emp.status == "在职"]
        if len(active_employees) < daily_resignations:
            daily_resignations = len(active_employees)
        
        resigning_employees = random.sample(active_employees, daily_resignations)
        
        logger_manager.log_info(f"开始处理今日离职申请，共 {daily_resignations} 人")
        
        for employee in resigning_employees:
            self._process_resignation_application(employee)
        
        return len(resigning_employees)
    
    def _process_resignation_application(self, employee):
        """处理单个员工的离职申请"""
        resignation_type = random.choice(["主动离职", "被动离职"])
        
        # 不直接传递reason参数，让Employee类自己根据resignation_type选择
        employee.initiate_resignation(resignation_type=resignation_type)
        
        # 记录离职申请日志
        logger_manager.log_hr_record(
            employee.employee_id,
            "离职申请提交",
            {
                "employee_name": employee.name,
                "department": employee.department,
                "resignation_type": resignation_type,
                "resignation_reason": employee.resignation_reason,
                "expected_last_work_date": employee.last_work_date.isoformat()
            }
        )
        
        # 生成账号移交记录
        self._generate_account_transfer_records(employee)
        
        logger_manager.log_info(f"员工 {employee.name}({employee.employee_id}) 提交离职申请")
    
    def _generate_account_transfer_records(self, employee):
        """生成账号移交记录"""
        for account_key, account_info in employee.accounts.items():
            if account_info['status'] == 'active':
                transfer_record = AccountTransferRecord(employee.employee_id, account_info)
                self.transfer_records.append(transfer_record)
                
                # 记录账号移交日志
                logger_manager.log_account_operation(
                    employee.employee_id,
                    account_info['account_type'],
                    "创建移交记录",
                    account_info['system'],
                    transfer_record.transfer_status
                )
    
    def process_resignation_completions(self):
        """处理离职完成流程"""
        # 找到应该完成离职的员工（离职申请且过了最后工作日）
        current_date = datetime.now()
        completing_employees = []
        
        for employee in self.employees.values():
            if (employee.status == "离职申请" and 
                employee.last_work_date and 
                employee.last_work_date.date() <= current_date.date()):
                completing_employees.append(employee)
        
        logger_manager.log_info(f"开始处理离职完成流程，共 {len(completing_employees)} 人")
        
        for employee in completing_employees:
            self._complete_resignation(employee)
        
        return len(completing_employees)
    
    def _complete_resignation(self, employee):
        """完成员工离职流程"""
        employee.complete_resignation()
        
        # 移动到已离职员工列表
        self.resigned_employees[employee.employee_id] = employee
        
        # 记录离职完成日志
        logger_manager.log_hr_record(
            employee.employee_id,
            "离职流程完成",
            {
                "employee_name": employee.name,
                "department": employee.department,
                "actual_resignation_date": datetime.now().isoformat(),
                "accounts_disabled": len([acc for acc in employee.accounts.values() if acc['status'] == 'disabled']),
                "permissions_revoked": len([perm for perm in employee.system_permissions.values() if perm['status'] == 'revoked'])
            }
        )
        
        # 更新账号移交记录状态
        self._update_transfer_records_status(employee.employee_id)
        
        logger_manager.log_info(f"员工 {employee.name}({employee.employee_id}) 离职流程完成")
    
    def _update_transfer_records_status(self, employee_id):
        """更新账号移交记录状态"""
        for record in self.transfer_records:
            if record.employee_id == employee_id and record.transfer_status == "待移交":
                # 随机决定移交是否成功
                success_rate = 0.95  # 95%成功率
                if random.random() < success_rate:
                    record.transfer_status = "已移交"
                    record.notes = "移交成功"
                else:
                    record.transfer_status = "移交失败"
                    record.notes = random.choice(["系统故障", "权限不足", "目标账号不存在"])
                
                logger_manager.log_account_operation(
                    employee_id,
                    record.account_type,
                    "更新移交状态",
                    record.system,
                    record.transfer_status
                )
    
    def extract_employee_data(self, start_date=None, end_date=None):
        """提取员工数据（模拟数据库查询）"""
        start_time = time.time()
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()
        
        # 模拟数据提取过程
        extracted_data = []
        for employee in list(self.employees.values()) + list(self.resigned_employees.values()):
            if (employee.resignation_date and 
                start_date <= employee.resignation_date <= end_date):
                extracted_data.append(employee.to_dict())
        
        # 模拟查询耗时
        query_time = random.uniform(0.1, 2.0)
        time.sleep(query_time)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger_manager.log_data_operation(
            "HR数据提取",
            "HRIS数据库",
            "数据仓库",
            len(extracted_data),
            duration
        )
        
        return extracted_data
    
    def get_transfer_records(self, employee_id=None):
        """获取账号移交记录"""
        if employee_id:
            return [record.to_dict() for record in self.transfer_records if record.employee_id == employee_id]
        return [record.to_dict() for record in self.transfer_records]
    
    def simulate_database_operations(self):
        """模拟数据库日常操作"""
        operations = [
            "员工信息查询", "离职流程查询", "账号状态检查", 
            "权限验证", "数据备份", "系统维护"
        ]
        
        for i in range(random.randint(10, 50)):
            operation = random.choice(operations)
            employee_id = random.choice(list(self.employees.keys())) if self.employees else "SYSTEM"
            
            # 模拟操作耗时
            operation_time = random.uniform(0.01, 0.5)
            time.sleep(operation_time)
            
            logger_manager.log_hr_record(
                employee_id,
                operation,
                {
                    "operation_id": f"OP_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                    "duration": f"{operation_time:.3f}s",
                    "result": "成功" if random.random() > 0.05 else "失败"
                }
            )
    
    def get_statistics(self):
        """获取系统统计信息"""
        total_employees = len(self.employees) + len(self.resigned_employees)
        active_employees = len(self.employees)
        resigned_employees = len(self.resigned_employees)
        pending_transfers = len([r for r in self.transfer_records if r.transfer_status == "待移交"])
        failed_transfers = len([r for r in self.transfer_records if r.transfer_status == "移交失败"])
        
        stats = {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "resigned_employees": resigned_employees,
            "total_transfer_records": len(self.transfer_records),
            "pending_transfers": pending_transfers,
            "failed_transfers": failed_transfers,
            "transfer_success_rate": f"{((len(self.transfer_records) - pending_transfers - failed_transfers) / max(1, len(self.transfer_records)) * 100):.2f}%"
        }
        
        return stats 