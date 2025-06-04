#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步模拟器
"""

import random
import time
import threading
from datetime import datetime, timedelta
from utils.logger import logger_manager
from config import DATA_CONFIG, PERFORMANCE_CONFIG

class DataSyncSimulator:
    """数据同步模拟器"""
    
    def __init__(self, hr_system, access_monitor):
        self.hr_system = hr_system
        self.access_monitor = access_monitor
        self.last_sync_time = datetime.now() - timedelta(hours=1)
        self.sync_running = False
        logger_manager.log_info("数据同步模拟器初始化完成")
    
    def perform_full_extraction(self):
        """执行全量数据提取"""
        if self.sync_running:
            logger_manager.log_error("数据同步", "全量提取请求被拒绝，同步正在进行中")
            return False
        
        self.sync_running = True
        start_time = time.time()
        
        try:
            logger_manager.log_info("开始执行全量数据提取")
            
            # 阶段1：提取HR系统数据
            hr_data = self._extract_hr_data_full()
            logger_manager.log_sync_operation(
                "全量提取-HR数据",
                len(hr_data),
                time.time() - start_time,
                "进行中"
            )
            
            # 阶段2：提取系统访问日志
            access_data = self._extract_access_logs_full()
            logger_manager.log_sync_operation(
                "全量提取-访问日志",
                len(access_data),
                time.time() - start_time,
                "进行中"
            )
            
            # 阶段3：处理半结构化日志
            semi_logs_count, semi_duration = self.access_monitor.process_semi_structured_logs()
            
            # 阶段4：数据转换和加载
            transformed_data = self._transform_and_load_data(hr_data, access_data)
            
            total_duration = time.time() - start_time
            total_records = len(hr_data) + len(access_data) + semi_logs_count
            
            # 检查性能要求
            success = total_duration <= PERFORMANCE_CONFIG['full_extract_time_limit']
            status = "成功" if success else "超时"
            
            logger_manager.log_sync_operation(
                "全量数据提取",
                total_records,
                total_duration,
                status
            )
            
            logger_manager.log_performance(
                "全量数据提取",
                PERFORMANCE_CONFIG['full_extract_time_limit'],
                total_duration,
                success
            )
            
            if success:
                logger_manager.log_info(f"全量数据提取成功完成，共处理 {total_records} 条记录，耗时 {total_duration:.2f} 秒")
            else:
                logger_manager.log_error(
                    "性能超时",
                    f"全量数据提取超时，目标时间: {PERFORMANCE_CONFIG['full_extract_time_limit']}秒，实际耗时: {total_duration:.2f}秒"
                )
            
            return success
            
        except Exception as e:
            logger_manager.log_error("全量提取异常", str(e))
            return False
        finally:
            self.sync_running = False
    
    def _extract_hr_data_full(self):
        """全量提取HR数据"""
        logger_manager.log_info("开始全量提取HR数据")
        
        # 模拟大量数据查询
        all_employees = list(self.hr_system.employees.values()) + list(self.hr_system.resigned_employees.values())
        hr_data = []
        
        batch_size = 1000
        total_batches = (len(all_employees) + batch_size - 1) // batch_size
        
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(all_employees))
            batch_employees = all_employees[start_idx:end_idx]
            
            # 模拟批量查询耗时
            batch_time = random.uniform(0.5, 2.0)
            time.sleep(batch_time)
            
            for employee in batch_employees:
                hr_data.append(employee.to_dict())
            
            logger_manager.log_data_operation(
                f"HR数据批量提取-批次{i+1}",
                "HRIS数据库",
                "数据仓库",
                len(batch_employees),
                batch_time
            )
        
        # 获取移交记录
        transfer_records = self.hr_system.get_transfer_records()
        hr_data.extend(transfer_records)
        
        logger_manager.log_info(f"HR数据全量提取完成，共 {len(hr_data)} 条记录")
        return hr_data
    
    def _extract_access_logs_full(self):
        """全量提取访问日志数据"""
        logger_manager.log_info("开始全量提取访问日志数据")
        
        # 模拟从各系统提取访问日志
        access_data = []
        
        # 提取结构化访问记录
        structured_data = self.access_monitor.extract_structured_data()
        access_data.extend(structured_data)
        
        # 模拟额外的历史日志提取
        historical_logs_count = random.randint(800000, 1200000)  # 80-120万条历史日志
        
        # 分批处理历史日志
        batch_size = 50000
        total_batches = (historical_logs_count + batch_size - 1) // batch_size
        
        for i in range(total_batches):
            batch_count = min(batch_size, historical_logs_count - i * batch_size)
            
            # 模拟批量提取耗时
            batch_time = random.uniform(1.0, 3.0)
            time.sleep(batch_time)
            
            # 生成模拟的历史日志数据
            for _ in range(batch_count):
                mock_log = {
                    "log_id": f"HIST_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}_{_}",
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                    "user_id": f"EMP{random.randint(100000, 999999)}",
                    "system": random.choice(["VPN", "邮件系统", "办公系统", "开发环境"]),
                    "action": random.choice(["登录", "登出", "文件访问", "数据查询"]),
                    "result": "成功"
                }
                access_data.append(mock_log)
            
            logger_manager.log_data_operation(
                f"访问日志批量提取-批次{i+1}",
                "各系统日志库",
                "数据仓库",
                batch_count,
                batch_time
            )
        
        logger_manager.log_info(f"访问日志全量提取完成，共 {len(access_data)} 条记录")
        return access_data
    
    def _transform_and_load_data(self, hr_data, access_data):
        """数据转换和加载"""
        logger_manager.log_info("开始数据转换和加载")
        start_time = time.time()
        
        # 模拟数据清洗和转换
        cleaning_time = random.uniform(30, 120)  # 30秒到2分钟的清洗时间
        time.sleep(cleaning_time)
        
        # 模拟数据加载到目标系统
        loading_time = random.uniform(60, 180)  # 1-3分钟的加载时间
        time.sleep(loading_time)
        
        total_time = time.time() - start_time
        total_records = len(hr_data) + len(access_data)
        
        logger_manager.log_data_operation(
            "数据转换和加载",
            "临时存储",
            "目标数据仓库",
            total_records,
            total_time
        )
        
        return {"hr_records": len(hr_data), "access_records": len(access_data)}
    
    def perform_incremental_sync(self):
        """执行增量数据同步"""
        if self.sync_running:
            logger_manager.log_error("数据同步", "增量同步请求被拒绝，同步正在进行中")
            return False
        
        start_time = time.time()
        
        try:
            logger_manager.log_info("开始执行增量数据同步")
            
            # 计算同步时间窗口
            sync_window_start = self.last_sync_time
            sync_window_end = datetime.now()
            
            # 获取增量数据
            incremental_data = self._get_incremental_data(sync_window_start, sync_window_end)
            
            # 模拟增量同步处理时间
            processing_time = random.uniform(1.0, 10.0)
            time.sleep(processing_time)
            
            total_duration = time.time() - start_time
            
            # 检查性能要求
            success = total_duration <= PERFORMANCE_CONFIG['incremental_sync_time_limit']
            status = "成功" if success else "超时"
            
            logger_manager.log_sync_operation(
                "增量数据同步",
                incremental_data['total_records'],
                total_duration,
                status
            )
            
            logger_manager.log_performance(
                "增量数据同步",
                PERFORMANCE_CONFIG['incremental_sync_time_limit'],
                total_duration,
                success
            )
            
            if success:
                self.last_sync_time = sync_window_end
                logger_manager.log_info(f"增量数据同步成功完成，同步 {incremental_data['total_records']} 条记录，耗时 {total_duration:.2f} 秒")
            else:
                logger_manager.log_error(
                    "性能超时",
                    f"增量数据同步超时，目标时间: {PERFORMANCE_CONFIG['incremental_sync_time_limit']}秒，实际耗时: {total_duration:.2f}秒"
                )
            
            return success
            
        except Exception as e:
            logger_manager.log_error("增量同步异常", str(e))
            return False
    
    def _get_incremental_data(self, start_time, end_time):
        """获取增量数据"""
        incremental_data = {
            "new_resignations": [],
            "new_access_logs": [],
            "account_changes": [],
            "total_records": 0
        }
        
        # 获取新离职员工数据
        for employee in self.hr_system.employees.values():
            if (employee.resignation_date and 
                start_time <= employee.resignation_date <= end_time):
                incremental_data["new_resignations"].append(employee.to_dict())
        
        # 获取最近一个季度相关记录（针对新离职员工）
        for employee in incremental_data["new_resignations"]:
            # 模拟获取该员工过去90天的记录
            historical_records_count = random.randint(100, 1000)
            incremental_data["total_records"] += historical_records_count
        
        # 获取新增访问日志
        new_logs_count = random.randint(0, DATA_CONFIG['incremental_sync_max'])
        incremental_data["new_access_logs"] = [f"LOG_{i}" for i in range(new_logs_count)]
        
        # 获取账号变更记录
        account_changes_count = random.randint(0, 100)
        incremental_data["account_changes"] = [f"CHANGE_{i}" for i in range(account_changes_count)]
        
        incremental_data["total_records"] = (
            len(incremental_data["new_resignations"]) +
            len(incremental_data["new_access_logs"]) +
            len(incremental_data["account_changes"]) +
            incremental_data["total_records"]
        )
        
        logger_manager.log_data_operation(
            "增量数据获取",
            "各源系统",
            "同步缓存",
            incremental_data["total_records"],
            random.uniform(0.5, 2.0)
        )
        
        return incremental_data
    
    def start_scheduled_sync(self):
        """启动定时同步任务"""
        def sync_worker():
            while True:
                try:
                    # 每10分钟执行一次增量同步
                    time.sleep(PERFORMANCE_CONFIG['sync_frequency_minutes'] * 60)
                    
                    if not self.sync_running:
                        self.perform_incremental_sync()
                    else:
                        logger_manager.log_info("跳过定时同步，同步任务正在进行中")
                        
                except Exception as e:
                    logger_manager.log_error("定时同步异常", str(e))
        
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        logger_manager.log_info("定时同步任务已启动")
    
    def simulate_data_validation(self):
        """模拟数据验证过程"""
        logger_manager.log_info("开始数据质量验证")
        
        validation_results = {
            "data_integrity_check": random.choice(["通过", "失败"]),
            "completeness_check": random.choice(["通过", "警告"]),
            "consistency_check": random.choice(["通过", "失败"]),
            "timeliness_check": random.choice(["通过", "通过"])
        }
        
        # 模拟验证耗时
        validation_time = random.uniform(5, 30)
        time.sleep(validation_time)
        
        failed_checks = [check for check, result in validation_results.items() if result == "失败"]
        warning_checks = [check for check, result in validation_results.items() if result == "警告"]
        
        if failed_checks:
            logger_manager.log_error(
                "数据质量验证",
                f"验证失败的检查项: {', '.join(failed_checks)}"
            )
        
        if warning_checks:
            logger_manager.log_info(f"数据质量验证警告: {', '.join(warning_checks)}")
        
        logger_manager.log_data_operation(
            "数据质量验证",
            "同步数据",
            "验证报告",
            1,
            validation_time
        )
        
        return validation_results
    
    def get_sync_statistics(self):
        """获取同步统计信息"""
        stats = {
            "last_sync_time": self.last_sync_time.isoformat(),
            "sync_running": self.sync_running,
            "next_scheduled_sync": (self.last_sync_time + timedelta(minutes=PERFORMANCE_CONFIG['sync_frequency_minutes'])).isoformat(),
            "sync_frequency_minutes": PERFORMANCE_CONFIG['sync_frequency_minutes'],
            "performance_limits": {
                "full_extract_limit": PERFORMANCE_CONFIG['full_extract_time_limit'],
                "incremental_sync_limit": PERFORMANCE_CONFIG['incremental_sync_time_limit']
            }
        }
        
        return stats 