#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工离职流程日志模拟器 - 主程序
"""

import time
import signal
import sys
import threading
from datetime import datetime
from simulators.hr_system import HRSystemSimulator
from simulators.access_monitor import AccessMonitorSimulator
from simulators.data_sync import DataSyncSimulator
from utils.logger import logger_manager

class LogSimulatorMain:
    """日志模拟器主控制器"""
    
    def __init__(self):
        self.running = False
        self.hr_system = None
        self.access_monitor = None
        self.data_sync = None
        
    def initialize_systems(self):
        """初始化所有模拟器系统"""
        logger_manager.log_info("=== 员工离职流程日志模拟器启动 ===")
        
        try:
            # 初始化HR系统模拟器
            logger_manager.log_info("初始化HR系统模拟器...")
            self.hr_system = HRSystemSimulator()
            
            # 初始化访问监控模拟器
            logger_manager.log_info("初始化系统访问监控模拟器...")
            self.access_monitor = AccessMonitorSimulator(self.hr_system)
            
            # 初始化数据同步模拟器
            logger_manager.log_info("初始化数据同步模拟器...")
            self.data_sync = DataSyncSimulator(self.hr_system, self.access_monitor)
            
            logger_manager.log_info("所有系统模拟器初始化完成")
            return True
            
        except Exception as e:
            logger_manager.log_error("系统初始化", f"初始化失败: {str(e)}")
            return False
    
    def run_simulation(self):
        """运行模拟器"""
        if not self.initialize_systems():
            logger_manager.log_error("启动失败", "系统初始化失败，模拟器无法启动")
            return
        
        self.running = True
        logger_manager.log_info("开始运行员工离职流程模拟")
        
        try:
            # 启动定时同步任务
            self.data_sync.start_scheduled_sync()
            
            # 模拟第一天的运行情况
            self._simulate_day_operations()
            
            # 模拟全量数据提取（季度任务）
            self._simulate_quarterly_full_extraction()
            
            # 持续模拟增量同步和监控
            self._run_continuous_simulation()
            
        except KeyboardInterrupt:
            logger_manager.log_info("接收到停止信号，正在关闭模拟器...")
            self.shutdown()
        except Exception as e:
            logger_manager.log_error("运行异常", f"模拟器运行异常: {str(e)}")
            self.shutdown()
    
    def _simulate_day_operations(self):
        """模拟一天的业务操作"""
        logger_manager.log_info("=== 模拟每日业务操作 ===")
        
        # 1. 处理每日离职申请
        resignation_count = self.hr_system.process_daily_resignations()
        logger_manager.log_info(f"处理每日离职申请完成，共 {resignation_count} 人")
        
        # 2. 处理离职完成流程
        completion_count = self.hr_system.process_resignation_completions()
        logger_manager.log_info(f"处理离职完成流程，共 {completion_count} 人")
        
        # 3. 生成系统访问日志
        access_logs_count = self.access_monitor.generate_daily_access_logs()
        logger_manager.log_info(f"生成每日访问日志完成，共 {access_logs_count} 条")
        
        # 4. 模拟HR数据库日常操作
        self.hr_system.simulate_database_operations()
        
        # 5. 处理半结构化日志
        logs_count, duration = self.access_monitor.process_semi_structured_logs()
        logger_manager.log_info(f"处理半结构化日志完成，共 {logs_count} 条，耗时 {duration:.2f} 秒")
        
        # 6. 执行增量同步
        sync_success = self.data_sync.perform_incremental_sync()
        logger_manager.log_info(f"增量同步执行完成，状态: {'成功' if sync_success else '失败'}")
        
        # 7. 执行审计监控
        self._perform_audit_monitoring()
    
    def _simulate_quarterly_full_extraction(self):
        """模拟季度全量数据提取"""
        logger_manager.log_info("=== 开始季度全量数据提取 ===")
        
        # 执行全量数据提取
        extraction_success = self.data_sync.perform_full_extraction()
        
        if extraction_success:
            logger_manager.log_info("季度全量数据提取成功完成")
            
            # 执行数据验证
            validation_results = self.data_sync.simulate_data_validation()
            logger_manager.log_info(f"数据验证完成，结果: {validation_results}")
        else:
            logger_manager.log_error("季度任务", "全量数据提取失败")
    
    def _perform_audit_monitoring(self):
        """执行审计监控"""
        logger_manager.log_info("=== 执行审计监控 ===")
        
        # 1. 监控账号状态合规性
        compliance_issues = self.access_monitor.monitor_account_status()
        if compliance_issues:
            logger_manager.log_info(f"发现 {len(compliance_issues)} 个合规问题")
            for issue in compliance_issues[:5]:  # 只记录前5个问题的详情
                logger_manager.log_audit_event(
                    issue['issue_type'],
                    issue['employee_id'],
                    issue,
                    "高" if "账号未及时禁用" in issue['issue_type'] else "中等"
                )
        
        # 2. 生成统计报告
        self._generate_statistics_report()
    
    def _generate_statistics_report(self):
        """生成统计报告"""
        logger_manager.log_info("=== 生成统计报告 ===")
        
        # HR系统统计
        hr_stats = self.hr_system.get_statistics()
        logger_manager.log_info(f"HR系统统计: {hr_stats}")
        
        # 违规访问统计
        violation_stats = self.access_monitor.get_violation_statistics()
        logger_manager.log_info(f"违规访问统计: {violation_stats}")
        
        # 同步系统统计
        sync_stats = self.data_sync.get_sync_statistics()
        logger_manager.log_info(f"数据同步统计: {sync_stats}")
        
        # 整体系统健康度评估
        self._assess_system_health(hr_stats, violation_stats, sync_stats)
    
    def _assess_system_health(self, hr_stats, violation_stats, sync_stats):
        """评估系统健康度"""
        health_score = 100
        health_issues = []
        
        # 检查移交成功率
        transfer_success_rate = float(hr_stats['transfer_success_rate'].replace('%', ''))
        if transfer_success_rate < 95:
            health_score -= 20
            health_issues.append(f"移交成功率偏低: {transfer_success_rate}%")
        
        # 检查违规访问情况
        if violation_stats['high_risk_alerts'] > 0:
            health_score -= 15
            health_issues.append(f"存在 {violation_stats['high_risk_alerts']} 个高风险违规访问")
        
        # 检查待处理告警
        if violation_stats['pending_alerts'] > 10:
            health_score -= 10
            health_issues.append(f"待处理告警过多: {violation_stats['pending_alerts']} 个")
        
        # 记录健康度评估
        if health_score >= 90:
            health_level = "优秀"
        elif health_score >= 75:
            health_level = "良好"
        elif health_score >= 60:
            health_level = "一般"
        else:
            health_level = "需要关注"
        
        logger_manager.log_audit_event(
            "系统健康度评估",
            "SYSTEM",
            {
                "health_score": health_score,
                "health_level": health_level,
                "issues": health_issues,
                "assessment_time": datetime.now().isoformat()
            },
            "低" if health_score >= 75 else "中等" if health_score >= 60 else "高"
        )
        
        logger_manager.log_info(f"系统健康度评估完成 - 得分: {health_score}, 等级: {health_level}")
    
    def _run_continuous_simulation(self):
        """运行连续模拟"""
        logger_manager.log_info("=== 进入连续模拟模式 ===")
        logger_manager.log_info("模拟器将继续运行，每分钟生成新的日志数据...")
        logger_manager.log_info("按 Ctrl+C 停止模拟器")
        
        while self.running:
            try:
                # 每分钟生成一些模拟数据
                time.sleep(60)
                
                # 模拟一些随机的系统活动
                self._simulate_random_activities()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger_manager.log_error("连续模拟", f"模拟过程中发生异常: {str(e)}")
                time.sleep(5)  # 等待5秒后继续
    
    def _simulate_random_activities(self):
        """模拟随机的系统活动"""
        import random
        
        # 随机生成一些员工的系统访问日志
        if random.random() < 0.3:  # 30%概率
            self.access_monitor.generate_daily_access_logs()
        
        # 随机处理一些HR数据库操作
        if random.random() < 0.2:  # 20%概率
            self.hr_system.simulate_database_operations()
        
        # 随机检查账号合规性
        if random.random() < 0.1:  # 10%概率
            self.access_monitor.monitor_account_status()
    
    def shutdown(self):
        """关闭模拟器"""
        self.running = False
        logger_manager.log_info("员工离职流程日志模拟器已停止")
        logger_manager.log_info("=== 模拟器运行结束 ===")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger_manager.log_info("接收到停止信号，正在优雅关闭...")
        self.shutdown()
        sys.exit(0)

def main():
    """主函数"""
    simulator = LogSimulatorMain()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, simulator.signal_handler)
    signal.signal(signal.SIGTERM, simulator.signal_handler)
    
    # 运行模拟器
    simulator.run_simulation()

if __name__ == "__main__":
    main()