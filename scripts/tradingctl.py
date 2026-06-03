#!/usr/bin/env python
"""
333交易系统 - 命令行控制工具

提供服务管理、状态查询、日志查看等功能
"""
import os
import sys
import time
import json
from pathlib import Path

# 添加项目路径
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from src.daemon.service_manager import ServiceManager


class TradingCTL:
    """交易系统命令行控制器"""
    
    def __init__(self):
        self.pid_file = project_path / "run" / "trading_system.pid"
        self.log_file = project_path / "logs" / "trading_system.log"
        self.status_file = project_path / "run" / "trading_system.status"
    
    def _print_status(self, status):
        """打印状态信息"""
        print("\n📊 服务状态:")
        print("-" * 40)
        print(f"  状态: {status.get('status', 'unknown')}")
        print(f"  PID: {status.get('pid', 'N/A')}")
        print(f"  服务名: {status.get('service', 'trading_system')}")
        print("-" * 40)
    
    def cmd_start(self, daemon=False, symbol="588200", balance=100000.0):
        """启动服务"""
        print(f"🚀 启动333交易系统服务...")
        print(f"   标的: {symbol}")
        print(f"   初始资金: {balance}")
        print(f"   守护进程模式: {daemon}")
        print("")
        
        # 检查是否已运行
        if ServiceManager.send_command("ping").get("success", False):
            print("❌ 服务已在运行中")
            return
        
        # 使用子进程启动服务
        import subprocess
        
        cmd = [
            sys.executable, "-m", "src.daemon.trading_service",
            "start", "-s", symbol, "-b", str(balance)
        ]
        
        if daemon:
            cmd.append("-d")
        
        if daemon:
            # 守护进程模式，后台运行
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            
            # 检查是否启动成功
            result = ServiceManager.send_command("ping")
            if result["success"]:
                print("✅ 服务已启动 (守护进程模式)")
            else:
                print("❌ 服务启动失败")
        else:
            # 前台运行
            subprocess.run(cmd)
    
    def cmd_stop(self):
        """停止服务"""
        print("⏹️ 停止333交易系统服务...")
        result = ServiceManager.send_command("stop")
        
        if result["success"]:
            time.sleep(1)
            print("✅ 服务已停止")
        else:
            print(f"❌ {result['message']}")
    
    def cmd_restart(self):
        """重启服务"""
        print("🔄 重启333交易系统服务...")
        result = ServiceManager.send_command("restart")
        
        if result["success"]:
            time.sleep(2)
            print("✅ 服务已重启")
        else:
            print(f"❌ {result['message']}")
    
    def cmd_status(self):
        """查看状态"""
        print("📊 查询服务状态...")
        result = ServiceManager.send_command("status")
        
        if result["success"]:
            self._print_status(result["data"])
        else:
            print(f"❌ {result['message']}")
    
    def cmd_logs(self, lines=50):
        """查看日志"""
        print(f"📝 查看最近 {lines} 行日志...")
        print("-" * 60)
        
        if not self.log_file.exists():
            print("❌ 日志文件不存在")
            return
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                content = f.readlines()
                if len(content) <= lines:
                    print("".join(content))
                else:
                    print("".join(content[-lines:]))
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")
        
        print("-" * 60)
    
    def cmd_tail(self):
        """实时查看日志"""
        print("📝 实时查看日志 (按 Ctrl+C 退出)...")
        print("-" * 60)
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                f.seek(0, 2)  # 移到文件末尾
                while True:
                    line = f.readline()
                    if line:
                        print(line.strip())
                    else:
                        time.sleep(1)
        except KeyboardInterrupt:
            print("\n" + "-" * 60)
            print("✅ 已退出日志查看")
        except Exception as e:
            print(f"\n❌ 读取日志失败: {e}")
    
    def cmd_ping(self):
        """Ping服务"""
        result = ServiceManager.send_command("ping")
        if result["success"]:
            print("✅ 服务在线")
        else:
            print(f"❌ 服务离线: {result['message']}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="333交易系统命令行控制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命令示例:
  tradingctl start                    # 前台启动服务
  tradingctl start -d                 # 后台守护进程启动
  tradingctl stop                     # 停止服务
  tradingctl restart                  # 重启服务
  tradingctl status                   # 查看状态
  tradingctl logs                     # 查看最近50行日志
  tradingctl logs -n 100              # 查看最近100行日志
  tradingctl tail                     # 实时查看日志
  tradingctl ping                     # 检查服务是否在线
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # start
    start_parser = subparsers.add_parser("start", help="启动服务")
    start_parser.add_argument("-d", "--daemon", action="store_true", help="守护进程模式")
    start_parser.add_argument("-s", "--symbol", default="588200", help="交易标的")
    start_parser.add_argument("-b", "--balance", type=float, default=100000.0, help="初始资金")
    
    # stop
    subparsers.add_parser("stop", help="停止服务")
    
    # restart
    subparsers.add_parser("restart", help="重启服务")
    
    # status
    subparsers.add_parser("status", help="查看状态")
    
    # logs
    logs_parser = subparsers.add_parser("logs", help="查看日志")
    logs_parser.add_argument("-n", "--lines", type=int, default=50, help="日志行数")
    
    # tail
    subparsers.add_parser("tail", help="实时查看日志")
    
    # ping
    subparsers.add_parser("ping", help="检查服务是否在线")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    ctl = TradingCTL()
    
    if args.command == "start":
        ctl.cmd_start(daemon=args.daemon, symbol=args.symbol, balance=args.balance)
    elif args.command == "stop":
        ctl.cmd_stop()
    elif args.command == "restart":
        ctl.cmd_restart()
    elif args.command == "status":
        ctl.cmd_status()
    elif args.command == "logs":
        ctl.cmd_logs(lines=args.lines)
    elif args.command == "tail":
        ctl.cmd_tail()
    elif args.command == "ping":
        ctl.cmd_ping()


if __name__ == "__main__":
    main()
