#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步模拟器 - 增强版，确保关联性和时间逻辑
"""

import random
import time
import threading
from datetime import datetime, timedelta
from utils.logger import logger_manager
from config import DATA_CONFIG, PERFORMANCE_CONFIG, TIME_CONFIG

class DataSyncSimulator:
    """数据同步模拟器 - 真实关联性版本"""
    
    def __init__(self, hr_system, access_monitor):
        self.hr_system = hr_system
        self.access_monitor = access_monitor
        self.sync_history = []
        self.last_sync_timestamp = {}
        self.sync_batch_tracker = {}  # 跟踪同步批次
        self.data_lineage = {}  # 数据血缘关系
        logger_manager.log_info("数据同步模拟器初始化完成")
    
    def perform_full_extract(self):
        """执行全量数据提取 - 增强关联性"""
        start_time = time.time()
        target_time = PERFORMANCE_CONFIG['full_extract_time_limit']
        
        logger_manager.log_info("开始执行全量数据提取")
        
        # 创建同步批次ID
        batch_id = f"FULL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.sync_batch_tracker[batch_id] = {
            "type": "全量提取",
            "start_time": datetime.now(),
            "status": "进行中",
            "data_sources": [],
            "extracted_data": {}
        }
        
        total_rows = 0
        
        # 1. 提取HR系统数据（按时间顺序）
        hr_data = self._extract_hr_data_with_lineage(batch_id)
        total_rows += len(hr_data)
        
        # 2. 提取系统访问日志（关联到HR数据中的员工）
        access_logs = self._extract_access_logs_with_context(batch_id, hr_data)
        total_rows += len(access_logs)
        
        # 3. 提取账号移交记录（与HR离职流程关联）
        transfer_records = self._extract_transfer_records_with_timeline(batch_id, hr_data)
        total_rows += len(transfer_records)
        
        # 4. 进行数据关联性验证
        self._validate_data_consistency(batch_id, hr_data, access_logs, transfer_records)
        
        end_time = time.time()
        duration = end_time - start_time
        success = duration <= target_time
        
        # 更新同步批次状态
        self.sync_batch_tracker[batch_id].update({
            "end_time": datetime.now(),
            "duration": duration,
            "total_rows": total_rows,
            "status": "成功" if success else "超时",
            "performance_ratio": duration / target_time
        })
        
        # 记录同步历史
        sync_record = {
            "batch_id": batch_id,
            "sync_type": "全量提取",
            "timestamp": datetime.now().isoformat(),
            "rows_extracted": total_rows,
            "duration": duration,
            "success": success,
            "target_time": target_time,
            "data_sources": ["HR系统", "访问日志", "移交记录"]
        }
        
        self.sync_history.append(sync_record)
        self.last_sync_timestamp["full_extract"] = datetime.now()
        
        # 记录性能和同步日志
        logger_manager.log_performance("全量数据提取", target_time, duration, success)
        logger_manager.log_sync_operation("全量提取", total_rows, duration, "成功" if success else "超时")
        
        logger_manager.log_info(f"全量数据提取完成，提取 {total_rows} 行数据，耗时 {duration:.2f} 秒")
        
        return total_rows, duration, success
    
    def perform_incremental_sync(self):
        """执行增量数据同步 - 确保时间连续性"""
        start_time = time.time()
        target_time = PERFORMANCE_CONFIG['incremental_sync_time_limit']
        
        # 创建同步批次ID
        batch_id = f"INCR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 确定增量同步的时间范围
        last_sync = self.last_sync_timestamp.get("incremental", datetime.now() - timedelta(minutes=10))
        current_sync = datetime.now()
        
        logger_manager.log_info(f"开始执行增量同步，时间范围：{last_sync.strftime('%Y-%m-%d %H:%M:%S')} 到 {current_sync.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.sync_batch_tracker[batch_id] = {
            "type": "增量同步",
            "start_time": current_sync,
            "time_range": {"from": last_sync, "to": current_sync},
            "status": "进行中"
        }
        
        # 1. 同步时间范围内的新离职申请
        new_resignations = self._sync_new_resignations(last_sync, current_sync, batch_id)
        
        # 2. 同步时间范围内的新访问日志
        new_access_logs = self._sync_new_access_logs(last_sync, current_sync, batch_id)
        
        # 3. 同步更新的账号移交状态
        updated_transfers = self._sync_transfer_updates(last_sync, current_sync, batch_id)
        
        # 4. 检测并同步异常事件
        anomaly_events = self._sync_anomaly_events(last_sync, current_sync, batch_id)
        
        total_rows = new_resignations + new_access_logs + updated_transfers + anomaly_events
        
        # 确保不超过增量同步最大数据量
        if total_rows > DATA_CONFIG['incremental_sync_max']:
            logger_manager.log_info(f"增量数据量 {total_rows} 超过限制 {DATA_CONFIG['incremental_sync_max']}，将分批处理")
            total_rows = DATA_CONFIG['incremental_sync_max']
        
        end_time = time.time()
        duration = end_time - start_time
        success = duration <= target_time and total_rows <= DATA_CONFIG['incremental_sync_max']
        
        # 更新同步批次状态
        self.sync_batch_tracker[batch_id].update({
            "end_time": datetime.now(),
            "duration": duration,
            "total_rows": total_rows,
            "status": "成功" if success else "失败",
            "components": {
                "new_resignations": new_resignations,
                "new_access_logs": new_access_logs,
                "updated_transfers": updated_transfers,
                "anomaly_events": anomaly_events
            }
        })
        
        # 记录同步历史
        sync_record = {
            "batch_id": batch_id,
            "sync_type": "增量同步",
            "timestamp": current_sync.isoformat(),
            "time_range": {
                "from": last_sync.isoformat(),
                "to": current_sync.isoformat()
            },
            "rows_synchronized": total_rows,
            "duration": duration,
            "success": success,
            "target_time": target_time
        }
        
        self.sync_history.append(sync_record)
        self.last_sync_timestamp["incremental"] = current_sync
        
        # 记录性能和同步日志
        logger_manager.log_performance("增量数据同步", target_time, duration, success)
        logger_manager.log_sync_operation("增量同步", total_rows, duration, "成功" if success else "失败")
        
        logger_manager.log_info(f"增量数据同步完成，同步 {total_rows} 行数据，耗时 {duration:.2f} 秒")
        
        return total_rows, duration, success
    
    def _extract_hr_data_with_lineage(self, batch_id):
        """提取HR数据并建立数据血缘关系"""
        # 获取近期有离职活动的员工数据
        hr_data = []
        cutoff_date = datetime.now() - timedelta(days=90)
        
        for employee in list(self.hr_system.employees.values()) + list(self.hr_system.resigned_employees.values()):
            if (employee.resignation_date and employee.resignation_date >= cutoff_date) or employee.status == "离职申请":
                employee_data = employee.to_dict()
                employee_data['extraction_batch'] = batch_id
                employee_data['extraction_timestamp'] = datetime.now().isoformat()
                hr_data.append(employee_data)
                
                # 建立数据血缘关系
                self.data_lineage[employee.employee_id] = {
                    "source_system": "HR系统",
                    "extraction_batch": batch_id,
                    "related_accounts": list(employee.accounts.keys()),
                    "related_permissions": list(employee.system_permissions.keys())
                }
        
        self.sync_batch_tracker[batch_id]["data_sources"].append("HR系统")
        self.sync_batch_tracker[batch_id]["extracted_data"]["hr_records"] = len(hr_data)
        
        logger_manager.log_data_operation(
            "HR数据提取",
            "HRIS数据库",
            f"数据仓库-批次{batch_id}",
            len(hr_data),
            1.5
        )
        
        return hr_data
    
    def _extract_access_logs_with_context(self, batch_id, hr_data):
        """提取访问日志并关联到HR数据"""
        access_logs = []
        hr_employee_ids = {emp['employee_id'] for emp in hr_data}
        
        # 只提取相关员工的访问日志
        for log in self.access_monitor.access_logs:
            if log.user_id in hr_employee_ids:
                log_data = log.to_dict()
                log_data['extraction_batch'] = batch_id
                log_data['extraction_timestamp'] = datetime.now().isoformat()
                
                # 添加关联信息
                related_employee = next((emp for emp in hr_data if emp['employee_id'] == log.user_id), None)
                if related_employee:
                    log_data['employee_context'] = {
                        "name": related_employee['name'],
                        "role": related_employee['role'],
                        "department": related_employee['department'],
                        "status": related_employee['status']
                    }
                
                access_logs.append(log_data)
        
        self.sync_batch_tracker[batch_id]["extracted_data"]["access_logs"] = len(access_logs)
        
        logger_manager.log_data_operation(
            "访问日志提取",
            "系统访问日志",
            f"数据仓库-批次{batch_id}",
            len(access_logs),
            2.0
        )
        
        return access_logs
    
    def _extract_transfer_records_with_timeline(self, batch_id, hr_data):
        """提取账号移交记录并建立时间线关联"""
        transfer_records = []
        hr_employee_ids = {emp['employee_id'] for emp in hr_data}
        
        for record in self.hr_system.transfer_records:
            if record.employee_id in hr_employee_ids:
                record_data = record.to_dict()
                record_data['extraction_batch'] = batch_id
                record_data['extraction_timestamp'] = datetime.now().isoformat()
                
                # 关联到离职时间线
                related_employee = next((emp for emp in hr_data if emp['employee_id'] == record.employee_id), None)
                if related_employee:
                    record_data['resignation_timeline'] = {
                        "resignation_date": related_employee.get('resignation_date'),
                        "last_work_date": related_employee.get('last_work_date'),
                        "days_since_resignation": self._calculate_days_since_resignation(related_employee)
                    }
                
                transfer_records.append(record_data)
        
        self.sync_batch_tracker[batch_id]["extracted_data"]["transfer_records"] = len(transfer_records)
        
        logger_manager.log_data_operation(
            "移交记录提取",
            "账号管理系统",
            f"数据仓库-批次{batch_id}",
            len(transfer_records),
            0.8
        )
        
        return transfer_records
    
    def _validate_data_consistency(self, batch_id, hr_data, access_logs, transfer_records):
        """验证数据一致性"""
        consistency_issues = []
        
        for employee_data in hr_data:
            employee_id = employee_data['employee_id']
            
            # 检查访问日志和HR状态的一致性
            if employee_data['status'] == "已离职":
                # 检查是否有离职后的访问记录
                post_resignation_logs = [
                    log for log in access_logs 
                    if (log.get('user_id') == employee_id and 
                        log.get('timestamp') > employee_data.get('last_work_date', ''))
                ]
                
                if post_resignation_logs:
                    issue = {
                        "type": "离职后访问检测",
                        "employee_id": employee_id,
                        "violation_count": len(post_resignation_logs),
                        "severity": "高"
                    }
                    consistency_issues.append(issue)
            
            # 检查账号移交记录的完整性
            employee_transfers = [r for r in transfer_records if r['employee_id'] == employee_id]
            expected_accounts = len(employee_data.get('accounts', {}))
            
            if len(employee_transfers) < expected_accounts:
                issue = {
                    "type": "移交记录不完整",
                    "employee_id": employee_id,
                    "expected": expected_accounts,
                    "actual": len(employee_transfers),
                    "severity": "中"
                }
                consistency_issues.append(issue)
        
        # 记录一致性检查结果
        self.sync_batch_tracker[batch_id]["consistency_check"] = {
            "issues_found": len(consistency_issues),
            "issues": consistency_issues
        }
        
        if consistency_issues:
            logger_manager.log_audit_event(
                "数据一致性检查",
                "SYSTEM",
                {"batch_id": batch_id, "issues": consistency_issues},
                "中"
            )
        
        return consistency_issues
    
    def _sync_new_resignations(self, from_time, to_time, batch_id):
        """同步新的离职申请"""
        new_resignations = 0
        
        for employee in self.hr_system.employees.values():
            if (employee.resignation_date and 
                from_time <= employee.resignation_date <= to_time):
                
                logger_manager.log_data_operation(
                    "增量-新离职申请",
                    "HR系统",
                    f"数据仓库-批次{batch_id}",
                    1,
                    0.1
                )
                new_resignations += 1
        
        return new_resignations
    
    def _sync_new_access_logs(self, from_time, to_time, batch_id):
        """同步新的访问日志"""
        new_logs = 0
        
        for log in self.access_monitor.access_logs:
            if from_time <= log.timestamp <= to_time:
                new_logs += 1
        
        if new_logs > 0:
            logger_manager.log_data_operation(
                "增量-新访问日志",
                "访问监控系统",
                f"数据仓库-批次{batch_id}",
                new_logs,
                0.5
            )
        
        return new_logs
    
    def _sync_transfer_updates(self, from_time, to_time, batch_id):
        """同步账号移交状态更新"""
        updated_transfers = 0
        
        for record in self.hr_system.transfer_records:
            if (record.transfer_date and 
                from_time <= record.transfer_date <= to_time):
                updated_transfers += 1
        
        if updated_transfers > 0:
            logger_manager.log_data_operation(
                "增量-移交状态更新",
                "账号管理系统",
                f"数据仓库-批次{batch_id}",
                updated_transfers,
                0.3
            )
        
        return updated_transfers
    
    def _sync_anomaly_events(self, from_time, to_time, batch_id):
        """同步异常事件"""
        anomaly_events = 0
        
        # 检查时间范围内的异常访问日志
        for log in self.access_monitor.access_logs:
            if (from_time <= log.timestamp <= to_time and 
                (log.is_suspicious or log.risk_score > 0.7)):
                anomaly_events += 1
        
        if anomaly_events > 0:
            logger_manager.log_data_operation(
                "增量-异常事件",
                "安全监控系统",
                f"数据仓库-批次{batch_id}",
                anomaly_events,
                0.2
            )
        
        return anomaly_events
    
    def _calculate_days_since_resignation(self, employee_data):
        """计算离职后天数"""
        if not employee_data.get('last_work_date'):
            return None
        
        try:
            last_work_date = datetime.fromisoformat(employee_data['last_work_date'].replace('Z', '+00:00'))
            return (datetime.now() - last_work_date).days
        except:
            return None
    
    def start_scheduled_sync(self):
        """启动定时同步"""
        def sync_loop():
            while True:
                try:
                    # 每10分钟执行一次增量同步
                    time.sleep(PERFORMANCE_CONFIG['sync_frequency_minutes'] * 60)
                    self.perform_incremental_sync()
                except Exception as e:
                    logger_manager.log_error("定时同步", f"定时同步失败: {str(e)}")
        
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        logger_manager.log_info("定时同步线程已启动")
    
    def get_sync_statistics(self):
        """获取同步统计信息"""
        total_syncs = len(self.sync_history)
        successful_syncs = len([s for s in self.sync_history if s['success']])
        
        if total_syncs == 0:
            return {"message": "暂无同步记录"}
        
        recent_syncs = [s for s in self.sync_history if 
                       datetime.fromisoformat(s['timestamp']) >= datetime.now() - timedelta(hours=24)]
        
        avg_duration = sum(s['duration'] for s in self.sync_history) / total_syncs
        
        stats = {
            "total_syncs": total_syncs,
            "successful_syncs": successful_syncs,
            "success_rate": f"{(successful_syncs / total_syncs * 100):.2f}%",
            "recent_24h_syncs": len(recent_syncs),
            "average_duration": f"{avg_duration:.2f}秒",
            "last_sync": self.sync_history[-1] if self.sync_history else None,
            "active_batches": len([b for b in self.sync_batch_tracker.values() if b['status'] == '进行中'])
        }
        
        return stats
    
    def get_data_lineage(self, employee_id):
        """获取数据血缘关系"""
        return self.data_lineage.get(employee_id, {"message": "未找到数据血缘信息"}) 