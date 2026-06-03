"""
333交易系统 - 后台交易服务

将交易系统与服务管理器集成，实现后台运行
"""
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_path))

from .service_manager import ServiceManager, ServiceStatus
from src.main import TradingSystem


class TradingService:
    """交易服务"""
    
    def __init__(self, symbol: str = "588200", initial_balance: float = 100000.0):
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.system: Optional[TradingSystem] = None
        
        # 创建服务管理器
        self.service_manager = ServiceManager(service_name="trading_system")
        self.service_manager.on_start = self._on_start
        self.service_manager.on_stop = self._on_stop
        self.service_manager.on_tick = self._on_tick
        
        # 状态统计
        self.tick_count = 0
        self.last_trade_time = None
        self.last_price = None
    
    def _on_start(self):
        """服务启动回调"""
        self.service_manager._log("初始化交易系统...")
        try:
            self.system = TradingSystem(
                symbol=self.symbol,
                initial_balance=self.initial_balance
            )
            self.system.initialize(kline_count=2000)
            self.service_manager._log(f"交易系统初始化完成")
            self.service_manager._log(f"  - 交易标的: {self.system.symbol}")
            self.service_manager._log(f"  - K线数量: {self.system.klines.count}")
            self.service_manager._log(f"  - 当前MA30: {self.system.strategy.current_ma}")
        except Exception as e:
            self.service_manager._log(f"交易系统初始化失败: {e}", "CRITICAL")
            raise
    
    def _on_stop(self):
        """服务停止回调"""
        self.service_manager._log("停止交易系统...")
        if self.system:
            self.system.reset()
            self.system = None
        self.service_manager._log("交易系统已停止")
    
    def _on_tick(self):
        """服务tick回调"""
        self.tick_count += 1
        
        try:
            if self.system and self.system.is_running:
                result = self.system.tick()
                
                if result:
                    self.last_price = result.get("price")
                    
                    if result.get("trade"):
                        trade = result["trade"]
                        self.last_trade_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.service_manager._log(
                            f"交易执行: {trade['action']} {trade['quantity']}股 @ {trade['price']}"
                        )
            
            # 每分钟记录一次状态
            if self.tick_count % 60 == 0:
                self._log_status()
                
        except Exception as e:
            self.service_manager._log(f"tick执行错误: {e}", "ERROR")
    
    def _log_status(self):
        """记录状态"""
        if self.system:
            account_summary = self.system.account.get_account_summary()
            self.service_manager._log(
                f"状态: 资金={account_summary['balance']:.2f}, "
                f"持仓市值={account_summary['market_value']:.2f}, "
                f"总盈利={account_summary['total_profit']:.2f}, "
                f"收益率={account_summary['profit_rate']*100:.2f}%"
            )
    
    def start(self, daemon: bool = False):
        """启动服务"""
        self.service_manager.start(daemon=daemon)
    
    def stop(self):
        """停止服务"""
        self.service_manager.stop()
    
    def get_status(self) -> dict:
        """获取服务状态"""
        status = self.service_manager.status
        
        result = {
            "status": status,
            "is_running": self.service_manager.is_running(),
            "tick_count": self.tick_count,
            "last_trade_time": self.last_trade_time,
            "last_price": self.last_price,
            "symbol": self.symbol
        }
        
        if self.system:
            result.update({
                "kline_count": self.system.klines.count,
                "current_ma": self.system.strategy.current_ma,
                "account": self.system.account.get_account_summary()
            })
        
        return result
    
    def send_command(self, action: str) -> dict:
        """发送命令到服务"""
        return self.service_manager.send_command(action)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="333交易系统后台服务")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], help="操作")
    parser.add_argument("--daemon", "-d", action="store_true", help="守护进程模式")
    parser.add_argument("--symbol", "-s", default="588200", help="交易标的")
    parser.add_argument("--balance", "-b", type=float, default=100000.0, help="初始资金")
    
    args = parser.parse_args()
    
    service = TradingService(symbol=args.symbol, initial_balance=args.balance)
    
    if args.action == "start":
        print(f"🚀 启动交易服务...")
        print(f"   标的: {args.symbol}")
        print(f"   初始资金: {args.balance}")
        print(f"   守护进程模式: {args.daemon}")
        print("")
        service.start(daemon=args.daemon)
    
    elif args.action == "stop":
        result = service.send_command("stop")
        if result["success"]:
            print("✅ 服务已停止")
        else:
            print(f"❌ {result['message']}")
    
    elif args.action == "restart":
        result = service.send_command("restart")
        if result["success"]:
            print("✅ 服务已重启")
        else:
            print(f"❌ {result['message']}")
    
    elif args.action == "status":
        result = service.send_command("status")
        if result["success"]:
            status = result["data"]
            print("📊 服务状态:")
            print(f"   状态: {status['status']}")
            print(f"   PID: {status['pid']}")
            print(f"   服务名: {status['service']}")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()
