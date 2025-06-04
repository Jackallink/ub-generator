#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工离职流程日志模拟器 - 主程序（v1.0.0 增强关联性版本）
"""

import sys
import time
import schedule
import argparse
import traceback
from datetime import datetime
from pathlib import Path

# 导入版本信息
from version import __version__, print_banner, get_version_info, get_system_info

# 导入核心模块
from simulators.hr_system import HRSystemSimulator
from simulators.access_monitor import AccessMonitorSimulator
from simulators.data_sync import DataSyncSimulator
from utils.logger import logger_manager
from config import PERFORMANCE_CONFIG, SIMULATION_CONFIG

class EnhancedResignationLogSimulator:
    """增强的员工离职流程日志模拟器 v1.0.0 - 确保真实关联性"""
    
    def __init__(self, config=None):
        """
        初始化模拟器
        
        Args:
            config: 可选的配置参数覆盖
        """
        self.version = __version__
        self.start_time = datetime.now()
        self.config = config or {}
        
        # 记录版本信息
        version_info = get_version_info()
        logger_manager.log_info(f"=== 员工离职流程日志模拟器 v{self.version} 启动 ===")
        logger_manager.log_info(f"版本信息: {version_info}")
        logger_manager.log_info(f"系统信息: {get_system_info()}")
        
        # 初始化各个子系统（确保正确的依赖顺序）
        try:
            self._initialize_subsystems()
            self._verify_system_consistency()
            logger_manager.log_info("✅ 所有子系统初始化完成")
        except Exception as e:
            logger_manager.log_error("系统初始化", f"初始化失败: {str(e)}")
            raise
    
    def _initialize_subsystems(self):
        """初始化各个子系统"""
        logger_manager.log_info("🔧 开始初始化子系统...")
        
        # Step 1: 初始化HR系统（核心数据源）
        logger_manager.log_info("初始化HR系统模拟器...")
        self.hr_system = HRSystemSimulator()
        
        # Step 2: 初始化访问监控（依赖HR系统）
        logger_manager.log_info("初始化访问监控模拟器...")
        self.access_monitor = AccessMonitorSimulator(self.hr_system)
        
        # Step 3: 初始化数据同步（依赖前两个系统）
        logger_manager.log_info("初始化数据同步模拟器...")
        self.data_sync = DataSyncSimulator(self.hr_system, self.access_monitor)
        
        logger_manager.log_info("✅ 子系统初始化完成")
    
    def _verify_system_consistency(self):
        """验证系统间的关联性和一致性"""
        logger_manager.log_info("🔍 开始系统关联性验证...")
        
        try:
            # 验证员工ID在所有系统中的一致性
            hr_employee_ids = set(self.hr_system.employees.keys())
            
            # 生成一些初始访问日志来测试关联性
            test_employees = list(hr_employee_ids)[:min(10, len(hr_employee_ids))]
            for employee_id in test_employees:
                employee = self.hr_system.employees[employee_id]
                if employee.status == "在职":
                    # 为测试员工生成少量访问日志
                    self.access_monitor.generate_daily_access_logs()
                    break
            
            # 验证访问日志中的用户ID是否都能在HR系统中找到对应员工
            all_employee_ids = hr_employee_ids | set(self.hr_system.resigned_employees.keys())
            orphaned_logs = 0
            total_logs = len(self.access_monitor.access_logs)
            
            for log in self.access_monitor.access_logs:
                if log.user_id not in all_employee_ids:
                    orphaned_logs += 1
            
            # 验证结果
            if orphaned_logs == 0:
                logger_manager.log_info("✅ 用户ID关联性验证通过")
            else:
                logger_manager.log_error("关联性验证", f"发现 {orphaned_logs}/{total_logs} 条孤立的访问日志")
            
            # 验证账号移交记录的关联性
            transfer_consistency = True
            for record in self.hr_system.transfer_records:
                if record.employee_id not in all_employee_ids:
                    transfer_consistency = False
                    break
            
            if transfer_consistency:
                logger_manager.log_info("✅ 账号移交记录关联性验证通过")
            else:
                logger_manager.log_error("关联性验证", "账号移交记录存在关联性问题")
            
            logger_manager.log_info("✅ 系统关联性验证完成")
            
        except Exception as e:
            logger_manager.log_error("关联性验证", f"验证过程出错: {str(e)}")
            raise
    
    def run_daily_simulation(self):
        """运行每日模拟流程 - 确保时间顺序逻辑"""
        start_time = time.time()
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        logger_manager.log_info(f"=== 开始每日模拟流程 {current_date} ===")
        
        try:
            results = {}
            
            # 1. 早晨：处理新的离职申请（最早发生的事件）
            logger_manager.log_info("📋 步骤 1/6: 处理新离职申请")
            results['resignations'] = self.hr_system.process_daily_resignations()
            
            # 2. 上午：生成在职员工的正常工作访问日志
            logger_manager.log_info("💻 步骤 2/6: 生成员工工作访问日志")
            results['access_logs'] = self.access_monitor.generate_daily_access_logs()
            
            # 3. 中午：处理离职完成流程（在申请提交后的某个时间点）
            logger_manager.log_info("✅ 步骤 3/6: 处理离职完成流程")
            results['completions'] = self.hr_system.process_resignation_completions()
            
            # 4. 下午：监控账号状态合规性（在离职处理后进行）
            logger_manager.log_info("🔒 步骤 4/6: 执行合规性检查")
            compliance_issues = self.access_monitor.monitor_account_status()
            results['compliance_issues'] = len(compliance_issues) if compliance_issues else 0
            
            # 5. 傍晚：执行增量数据同步（汇总一天的变化）
            logger_manager.log_info("🔄 步骤 5/6: 执行增量数据同步")
            sync_rows, sync_duration, sync_success = self.data_sync.perform_incremental_sync()
            results.update({
                'sync_data_rows': sync_rows,
                'sync_duration': sync_duration,
                'sync_success': sync_success
            })
            
            # 6. 晚上：生成每日摘要报告
            logger_manager.log_info("📊 步骤 6/6: 生成每日摘要报告")
            
            # 生成每日摘要报告
            daily_summary = {
                "date": current_date,
                "version": self.version,
                "execution_time": time.time() - start_time,
                **results
            }
            
            logger_manager.log_info(f"✅ 每日模拟完成: {daily_summary}")
            return daily_summary
            
        except Exception as e:
            logger_manager.log_error("每日模拟", f"执行失败: {str(e)}")
            logger_manager.log_error("错误详情", traceback.format_exc())
            raise
    
    def run_weekly_full_extract(self):
        """运行每周全量数据提取"""
        logger_manager.log_info("=== 开始每周全量数据提取 ===")
        
        try:
            start_time = time.time()
            
            # 执行全量数据提取
            total_rows, duration, success = self.data_sync.perform_full_extract()
            
            # 性能评估
            target_time = PERFORMANCE_CONFIG['full_extract_time_limit']
            performance_ratio = duration / target_time
            
            if success:
                logger_manager.log_info(f"✅ 全量数据提取成功完成")
                logger_manager.log_info(f"  - 提取数据: {total_rows:,} 行")
                logger_manager.log_info(f"  - 耗时: {duration:.2f} 秒")
                logger_manager.log_info(f"  - 性能比率: {performance_ratio:.2f}")
            else:
                logger_manager.log_error("全量数据提取", f"提取超时，耗时 {duration:.2f} 秒，超过限制 {target_time} 秒")
            
            return {
                "success": success,
                "total_rows": total_rows,
                "duration": duration,
                "performance_ratio": performance_ratio,
                "target_time": target_time
            }
            
        except Exception as e:
            logger_manager.log_error("全量数据提取", f"执行失败: {str(e)}")
            raise
    
    def monitor_system_health(self):
        """监控系统健康状态"""
        logger_manager.log_info("=== 系统健康检查 ===")
        
        try:
            # 1. HR系统统计
            hr_stats = self.hr_system.get_statistics()
            logger_manager.log_info(f"HR系统状态: {hr_stats}")
            
            # 2. 访问监控统计
            violation_stats = self.access_monitor.get_violation_statistics()
            logger_manager.log_info(f"访问监控状态: {violation_stats}")
            
            # 3. 数据同步统计
            sync_stats = self.data_sync.get_sync_statistics()
            logger_manager.log_info(f"数据同步状态: {sync_stats}")
            
            # 4. 关联性健康检查
            relationship_issues = self._check_data_relationships()
            
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "version": self.version,
                "uptime": str(datetime.now() - self.start_time),
                "hr_system": hr_stats,
                "access_monitoring": violation_stats,
                "data_sync": sync_stats,
                "relationship_issues": len(relationship_issues)
            }
            
            return health_report
            
        except Exception as e:
            logger_manager.log_error("系统健康检查", f"执行失败: {str(e)}")
            raise
    
    def _check_data_relationships(self):
        """检查数据关联关系的健康状态"""
        logger_manager.log_info("🔍 检查数据关联关系")
        
        issues = []
        
        try:
            # 检查是否有访问日志对应不到有效员工
            all_employee_ids = set(self.hr_system.employees.keys()) | set(self.hr_system.resigned_employees.keys())
            
            orphaned_logs = 0
            recent_logs = self.access_monitor.access_logs[-min(1000, len(self.access_monitor.access_logs)):]
            
            for log in recent_logs:
                if log.user_id not in all_employee_ids:
                    orphaned_logs += 1
            
            if orphaned_logs > 0:
                issues.append(f"发现 {orphaned_logs} 条无法关联到员工的访问日志")
            
            # 检查离职员工是否有对应的移交记录
            resigned_without_transfer = 0
            for employee_id, employee in self.hr_system.resigned_employees.items():
                employee_transfers = [r for r in self.hr_system.transfer_records if r.employee_id == employee_id]
                expected_transfers = len(employee.accounts)
                if len(employee_transfers) < expected_transfers:
                    resigned_without_transfer += 1
            
            if resigned_without_transfer > 0:
                issues.append(f"发现 {resigned_without_transfer} 名离职员工缺少完整的移交记录")
            
            # 检查时间序列的逻辑性
            timeline_issues = 0
            for employee in self.hr_system.resigned_employees.values():
                if employee.resignation_date and employee.last_work_date:
                    if employee.resignation_date > employee.last_work_date:
                        timeline_issues += 1
            
            if timeline_issues > 0:
                issues.append(f"发现 {timeline_issues} 名员工的时间序列存在逻辑错误")
            
            if issues:
                for issue in issues:
                    logger_manager.log_error("数据关联性", issue)
            else:
                logger_manager.log_info("✅ 数据关联关系健康")
            
            return issues
            
        except Exception as e:
            logger_manager.log_error("关联性检查", f"检查过程出错: {str(e)}")
            return [f"关联性检查异常: {str(e)}"]
    
    def generate_compliance_report(self):
        """生成合规性报告"""
        logger_manager.log_info("=== 生成合规性报告 ===")
        
        try:
            report = {
                "report_date": datetime.now().isoformat(),
                "version": self.version,
                "summary": {},
                "findings": [],
                "recommendations": []
            }
            
            # 1. 统计离职员工账号处理情况
            total_resigned = len(self.hr_system.resigned_employees)
            accounts_properly_disabled = 0
            accounts_with_violations = 0
            
            for employee in self.hr_system.resigned_employees.values():
                properly_disabled = all(acc['status'] == 'disabled' for acc in employee.accounts.values())
                if properly_disabled:
                    accounts_properly_disabled += 1
                
                # 检查是否有离职后访问
                post_resignation_access = any(
                    log.user_id == employee.employee_id and 
                    log.timestamp > employee.last_work_date
                    for log in self.access_monitor.access_logs
                    if employee.last_work_date
                )
                
                if post_resignation_access:
                    accounts_with_violations += 1
            
            report["summary"] = {
                "total_resigned_employees": total_resigned,
                "accounts_properly_disabled": accounts_properly_disabled,
                "accounts_with_violations": accounts_with_violations,
                "compliance_rate": f"{(accounts_properly_disabled / max(1, total_resigned) * 100):.2f}%"
            }
            
            # 2. 具体发现
            if accounts_with_violations > 0:
                report["findings"].append({
                    "type": "离职后违规访问",
                    "severity": "高",
                    "count": accounts_with_violations,
                    "description": "发现离职员工在离职后仍能访问公司系统"
                })
            
            pending_transfers = len([r for r in self.hr_system.transfer_records if r.transfer_status == "待移交"])
            if pending_transfers > 0:
                report["findings"].append({
                    "type": "账号移交延迟",
                    "severity": "中",
                    "count": pending_transfers,
                    "description": "部分账号移交记录仍处于待处理状态"
                })
            
            # 3. 改进建议
            if accounts_with_violations > 0:
                report["recommendations"].append("建议加强离职员工账号的实时监控和自动禁用机制")
            
            if pending_transfers > 0:
                report["recommendations"].append("建议优化账号移交流程，设置自动提醒和超时处理")
            
            logger_manager.log_compliance_check(
                "员工离职合规检查",
                "通过" if not report["findings"] else "发现问题",
                report["findings"],
                report["recommendations"]
            )
            
            return report
            
        except Exception as e:
            logger_manager.log_error("合规性报告", f"生成失败: {str(e)}")
            raise
    
    def start_monitoring(self):
        """启动持续监控"""
        logger_manager.log_info("=== 启动持续监控模式 ===")
        
        try:
            # 安排定时任务
            schedule.every().day.at("09:00").do(self.run_daily_simulation)
            schedule.every().week.at("02:00").do(self.run_weekly_full_extract)
            schedule.every().hour.do(self.monitor_system_health)
            schedule.every().day.at("23:00").do(self.generate_compliance_report)
            
            # 启动数据同步定时器
            self.data_sync.start_scheduled_sync()
            
            logger_manager.log_info("⏰ 定时任务已设置:")
            logger_manager.log_info("- 每日模拟: 09:00")
            logger_manager.log_info("- 每周全量提取: 周一 02:00")
            logger_manager.log_info("- 系统健康检查: 每小时")
            logger_manager.log_info("- 合规性报告: 23:00")
            logger_manager.log_info("- 增量同步: 每10分钟")
            
            # 持续运行
            logger_manager.log_info("🚀 系统进入持续监控模式...")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # 每分钟检查一次
            except KeyboardInterrupt:
                logger_manager.log_info("⛔ 收到停止信号，正在优雅关闭...")
                logger_manager.log_info("📊 生成最终统计报告...")
                
                final_report = self.monitor_system_health()
                logger_manager.log_info(f"最终统计: {final_report}")
                
                logger_manager.log_info("✅ 监控程序已安全停止")
                
        except Exception as e:
            logger_manager.log_error("持续监控", f"运行失败: {str(e)}")
            raise

def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description=f"员工离职流程日志模拟器 v{__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 运行演示模式
  python main.py --monitor          # 启动持续监控
  python main.py --daily            # 仅运行每日模拟
  python main.py --extract          # 仅运行全量提取
  python main.py --health           # 仅检查系统健康
  python main.py --version          # 显示版本信息
  python main.py --verbose          # 详细输出模式
        """
    )
    
    parser.add_argument('--version', action='version', version=f'v{__version__}')
    parser.add_argument('--monitor', action='store_true', help='启动持续监控模式')
    parser.add_argument('--daily', action='store_true', help='仅运行每日模拟')
    parser.add_argument('--extract', action='store_true', help='仅运行全量数据提取')
    parser.add_argument('--health', action='store_true', help='仅检查系统健康状态')
    parser.add_argument('--compliance', action='store_true', help='仅生成合规性报告')
    parser.add_argument('--verify', action='store_true', help='运行关联性验证')
    parser.add_argument('--verbose', action='store_true', help='详细输出模式')
    parser.add_argument('--config', type=str, help='指定配置文件路径')
    
    return parser

def main():
    """主函数 v1.0.0"""
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 显示启动横幅
    if not any([args.daily, args.extract, args.health, args.compliance, args.verify]):
        print_banner()
    
    try:
        # 创建日志目录
        Path("logs").mkdir(exist_ok=True)
        
        # 创建模拟器实例
        logger_manager.log_info("🚀 创建模拟器实例...")
        simulator = EnhancedResignationLogSimulator()
        
        # 根据命令行参数执行相应操作
        if args.monitor:
            # 持续监控模式
            simulator.start_monitoring()
        
        elif args.daily:
            # 仅运行每日模拟
            result = simulator.run_daily_simulation()
            print(f"✅ 每日模拟完成: {result}")
        
        elif args.extract:
            # 仅运行全量提取
            result = simulator.run_weekly_full_extract()
            print(f"✅ 全量提取完成: {result}")
        
        elif args.health:
            # 仅检查系统健康
            result = simulator.monitor_system_health()
            print(f"✅ 系统健康检查完成: {result}")
        
        elif args.compliance:
            # 仅生成合规性报告
            result = simulator.generate_compliance_report()
            print(f"✅ 合规性报告生成完成: {result}")
        
        elif args.verify:
            # 运行关联性验证
            print("🔍 运行关联性验证...")
            import subprocess
            result = subprocess.run([sys.executable, "verify_relationships.py"], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"⚠️ 验证警告: {result.stderr}")
        
        else:
            # 默认演示模式
            logger_manager.log_info("=== 运行演示模式 ===")
            
            # 1. 执行一次完整的每日模拟
            daily_result = simulator.run_daily_simulation()
            
            # 2. 执行一次全量数据提取
            extract_result = simulator.run_weekly_full_extract()
            
            # 3. 生成系统健康报告
            health_report = simulator.monitor_system_health()
            
            # 4. 生成合规性报告
            compliance_report = simulator.generate_compliance_report()
            
            logger_manager.log_info("=== 演示模式完成 ===")
            logger_manager.log_info("🎯 系统已准备就绪，可选择启动持续监控模式")
            logger_manager.log_info("💡 使用 --help 查看更多运行选项")
            
            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           演示运行结果总览                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 📋 每日模拟结果: {str(daily_result['sync_success']):50} ║
║ 🔄 全量提取结果: {str(extract_result['success']):50} ║
║ ❤️  系统健康状态: 良好{' ':58} ║
║ 📊 合规检查结果: {str(len(compliance_report['findings']) == 0):50} ║
╚══════════════════════════════════════════════════════════════════════════════╝

💡 提示: 
   - 使用 'python main.py --monitor' 启动持续监控
   - 使用 'python verify_relationships.py' 验证数据关联性
   - 查看 logs/ 目录中的详细日志文件
            """)
        
        return simulator
        
    except KeyboardInterrupt:
        logger_manager.log_info("⛔ 用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger_manager.log_error("主程序", f"运行出错: {str(e)}")
        if args.verbose:
            logger_manager.log_error("错误详情", traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    simulator = main()