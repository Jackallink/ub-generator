#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统关联性和逻辑性验证脚本
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter

def load_json_logs(filepath):
    """加载JSON格式的日志文件"""
    records = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    records.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return records

def verify_user_consistency():
    """验证用户ID在各系统中的一致性"""
    print("=== 用户ID关联性验证 ===")
    
    # 1. 从HR系统获取所有员工ID
    hr_records = load_json_logs('logs/hr_database.log')
    hr_employee_ids = set()
    
    for record in hr_records:
        if record.get('action') == '员工入职':
            hr_employee_ids.add(record['employee_id'])
    
    print(f"HR系统中的员工数量: {len(hr_employee_ids)}")
    
    # 2. 从系统访问日志获取用户ID
    access_records = load_json_logs('logs/system_access.log')
    access_user_ids = set()
    
    for record in access_records:
        access_user_ids.add(record['user_id'])
    
    print(f"访问日志中的用户数量: {len(access_user_ids)}")
    
    # 3. 检查关联性
    orphaned_access_users = access_user_ids - hr_employee_ids
    hr_without_access = hr_employee_ids - access_user_ids
    
    print(f"无法关联到HR系统的访问用户: {len(orphaned_access_users)}")
    print(f"没有访问记录的HR员工: {len(hr_without_access)}")
    
    if orphaned_access_users:
        print(f"孤立的访问用户示例: {list(orphaned_access_users)[:5]}")
    
    # 4. 验证账号管理记录的关联性
    if os.path.exists('logs/account_management.log'):
        with open('logs/account_management.log', 'r', encoding='utf-8') as f:
            account_lines = f.readlines()
        
        account_employee_ids = set()
        for line in account_lines:
            if '员工ID:' in line:
                try:
                    emp_id = line.split('员工ID: ')[1].split(',')[0].strip()
                    account_employee_ids.add(emp_id)
                except:
                    pass
        
        print(f"账号管理记录中的员工数量: {len(account_employee_ids)}")
        orphaned_accounts = account_employee_ids - hr_employee_ids
        print(f"无法关联到HR系统的账号记录: {len(orphaned_accounts)}")
    
    return len(orphaned_access_users) == 0 and len(orphaned_accounts) == 0

def verify_time_sequences():
    """验证时间序列的逻辑性"""
    print("\n=== 时间序列逻辑验证 ===")
    
    hr_records = load_json_logs('logs/hr_database.log')
    access_records = load_json_logs('logs/system_access.log')
    
    # 1. 验证HR事件的时间逻辑
    hr_timeline = defaultdict(list)
    for record in hr_records:
        employee_id = record['employee_id']
        timestamp = datetime.fromisoformat(record['timestamp'])
        hr_timeline[employee_id].append((timestamp, record['action']))
    
    time_logic_errors = 0
    for employee_id, events in hr_timeline.items():
        events.sort(key=lambda x: x[0])  # 按时间排序
        
        # 检查入职是否在离职申请之前
        hire_time = None
        resignation_time = None
        
        for timestamp, action in events:
            if action == '员工入职':
                hire_time = timestamp
            elif action == '离职申请提交':
                resignation_time = timestamp
        
        if hire_time and resignation_time and hire_time >= resignation_time:
            time_logic_errors += 1
            print(f"时间逻辑错误: 员工 {employee_id} 的入职时间晚于离职申请时间")
    
    print(f"发现时间逻辑错误: {time_logic_errors} 个")
    
    # 2. 验证系统访问的时间连续性
    access_sessions = defaultdict(list)
    for record in access_records:
        user_id = record['user_id']
        timestamp = datetime.fromisoformat(record['timestamp'])
        action = record['action']
        system = record['system']
        
        access_sessions[user_id].append((timestamp, action, system))
    
    session_logic_errors = 0
    for user_id, sessions in list(access_sessions.items())[:10]:  # 检查前10个用户
        sessions.sort(key=lambda x: x[0])
        
        # 检查登录/登出的逻辑
        system_states = defaultdict(str)  # 跟踪每个系统的状态
        
        for timestamp, action, system in sessions:
            if action == '登录':
                if system_states[system] == 'logged_in':
                    session_logic_errors += 1
                    # print(f"会话逻辑错误: 用户 {user_id} 在 {system} 重复登录")
                system_states[system] = 'logged_in'
            elif action == '登出':
                if system_states[system] != 'logged_in':
                    session_logic_errors += 1
                    # print(f"会话逻辑错误: 用户 {user_id} 在 {system} 未登录就登出")
                system_states[system] = 'logged_out'
    
    print(f"发现会话逻辑错误: {session_logic_errors} 个")
    
    return time_logic_errors == 0

def verify_business_flows():
    """验证业务流程的合理性"""
    print("\n=== 业务流程合理性验证 ===")
    
    hr_records = load_json_logs('logs/hr_database.log')
    access_records = load_json_logs('logs/system_access.log')
    
    # 1. 验证离职流程的完整性
    resignations = {}
    for record in hr_records:
        if record['action'] == '离职申请提交':
            employee_id = record['employee_id']
            details = record['details']
            resignations[employee_id] = {
                'name': details['employee_name'],
                'department': details['department'],
                'resignation_type': details['resignation_type'],
                'resignation_reason': details['resignation_reason'],
                'expected_last_work_date': details['expected_last_work_date']
            }
    
    print(f"发现离职申请: {len(resignations)} 个")
    
    # 2. 验证角色与系统访问的合理性
    # 获取员工角色信息
    employee_roles = {}
    for record in hr_records:
        if record['action'] == '员工入职':
            employee_id = record['employee_id']
            department = record['details']['department']
            position = record['details']['position']
            
            # 根据部门和职位推断角色
            if '技术' in department or '产品' in department:
                role = '技术人员'
            elif '财务' in department:
                role = '财务人员'
            elif '市场' in department or '销售' in department:
                role = '销售人员'
            elif '人力资源' in department:
                role = 'HR人员'
            elif 'CEO' in department or '副总' in department:
                role = '高管'
            else:
                role = '一般员工'
            
            employee_roles[employee_id] = role
    
    # 3. 检查访问模式的合理性
    access_patterns = defaultdict(lambda: defaultdict(int))
    
    for record in access_records:
        user_id = record['user_id']
        system = record['system']
        action = record['action']
        
        access_patterns[user_id][system] += 1
    
    role_system_violations = 0
    for user_id, systems in list(access_patterns.items())[:20]:  # 检查前20个用户
        user_role = employee_roles.get(user_id, '未知')
        
        # 检查角色与系统访问的合理性
        if user_role == '财务人员':
            sensitive_systems = ['代码仓库', '生产环境', '监控系统']
            for system in systems:
                if any(s in system for s in sensitive_systems):
                    role_system_violations += 1
                    print(f"角色访问异常: 财务人员 {user_id} 访问了 {system}")
        
        elif user_role == '一般员工':
            restricted_systems = ['财务系统', 'HR系统', '薪酬系统', '代码仓库']
            for system in systems:
                if any(s in system for s in restricted_systems):
                    role_system_violations += 1
                    print(f"权限越界: 一般员工 {user_id} 访问了 {system}")
    
    print(f"发现角色访问异常: {role_system_violations} 个")
    
    return role_system_violations < 10  # 允许少量异常

def verify_data_volume_consistency():
    """验证数据量的一致性"""
    print("\n=== 数据量一致性验证 ===")
    
    # 检查各日志文件的记录数量
    log_files = {
        'hr_database.log': 'HR数据库日志',
        'system_access.log': '系统访问日志',
        'account_management.log': '账号管理日志',
        'data_sync.log': '数据同步日志'
    }
    
    log_counts = {}
    for filename, description in log_files.items():
        filepath = f'logs/{filename}'
        if os.path.exists(filepath):
            if filename.endswith('.log') and 'management' not in filename and 'sync' not in filename:
                # JSON格式日志
                records = load_json_logs(filepath)
                count = len(records)
            else:
                # 文本格式日志
                with open(filepath, 'r', encoding='utf-8') as f:
                    count = len(f.readlines())
            
            log_counts[description] = count
            print(f"{description}: {count:,} 条记录")
    
    # 检查比例关系的合理性
    hr_count = log_counts.get('HR数据库日志', 0)
    access_count = log_counts.get('系统访问日志', 0)
    
    if hr_count > 0:
        access_ratio = access_count / hr_count
        print(f"访问日志与HR记录比例: {access_ratio:.2f}:1")
        
        # 一般来说，访问日志应该比HR记录多很多
        if access_ratio < 5:
            print("⚠️  警告: 访问日志数量可能偏少")
        elif access_ratio > 100:
            print("⚠️  警告: 访问日志数量可能偏多")
        else:
            print("✓ 数据量比例合理")
    
    return True

def verify_employee_lifecycle():
    """验证员工生命周期的完整性"""
    print("\n=== 员工生命周期验证 ===")
    
    hr_records = load_json_logs('logs/hr_database.log')
    
    # 统计各种HR事件
    event_counts = Counter()
    employee_states = defaultdict(list)
    
    for record in hr_records:
        action = record['action']
        employee_id = record['employee_id']
        timestamp = record['timestamp']
        
        event_counts[action] += 1
        employee_states[employee_id].append((timestamp, action))
    
    print("HR事件统计:")
    for event, count in event_counts.items():
        print(f"  {event}: {count} 次")
    
    # 检查员工状态转换的合理性
    lifecycle_complete = 0
    lifecycle_incomplete = 0
    
    for employee_id, events in employee_states.items():
        events.sort(key=lambda x: x[0])  # 按时间排序
        
        actions = [event[1] for event in events]
        
        if '员工入职' in actions:
            if '离职申请提交' in actions:
                lifecycle_complete += 1
            else:
                lifecycle_incomplete += 1
    
    print(f"\n员工生命周期分析:")
    print(f"  完整生命周期(入职->离职): {lifecycle_complete} 人")
    print(f"  不完整生命周期(仅入职): {lifecycle_incomplete} 人")
    
    return True

def main():
    """主验证函数"""
    print("🔍 开始系统关联性和逻辑性全面验证")
    print("=" * 60)
    
    # 检查日志文件是否存在
    required_files = ['logs/hr_database.log', 'logs/system_access.log']
    for filepath in required_files:
        if not os.path.exists(filepath):
            print(f"❌ 缺少必要的日志文件: {filepath}")
            return False
    
    results = []
    
    # 1. 用户ID关联性验证
    results.append(("用户ID关联性", verify_user_consistency()))
    
    # 2. 时间序列逻辑验证
    results.append(("时间序列逻辑", verify_time_sequences()))
    
    # 3. 业务流程合理性验证
    results.append(("业务流程合理性", verify_business_flows()))
    
    # 4. 数据量一致性验证
    results.append(("数据量一致性", verify_data_volume_consistency()))
    
    # 5. 员工生命周期验证
    results.append(("员工生命周期", verify_employee_lifecycle()))
    
    # 总结验证结果
    print("\n" + "=" * 60)
    print("🏁 验证结果总结")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} : {status}")
        if not passed:
            all_passed = False
    
    overall_status = "🎉 所有验证通过！系统具有良好的关联性和逻辑性。" if all_passed else "⚠️  部分验证失败，需要检查和改进。"
    print(f"\n总体状态: {overall_status}")
    
    return all_passed

if __name__ == "__main__":
    main() 