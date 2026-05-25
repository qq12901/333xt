"""
333交易系统 - 主程序

整合所有模块，实现完整的交易系统
"""
from datetime import datetime
from typing import Optional
from .datasources.multi_source_manager import MultiDataSourceManager
from .indicators import MAEngine
from .models import KlineData, Position, PositionStatus
from .strategy import Strategy333
from .execution import SimulatedAccount
from .logging import TradingLogger, SignalLogger


class TradingSystem:
    """333交易系统主类"""
    
    def __init__(
        self,
        symbol: str = "588200",
        initial_balance: float = 100000.0,
        ma_period: int = 30
    ):
        """
        初始化交易系统
        
        Args:
            symbol: 交易标的代码
            initial_balance: 初始资金
            ma_period: MA周期
        """
        self.symbol = symbol
        self.ma_period = ma_period
        
        self.logger = TradingLogger(name=f"333_trading_{symbol}")
        self.signal_logger = SignalLogger()
        
        # 使用多数据源管理器
        print("📊 正在初始化多数据源管理器...")
        self.data_source = MultiDataSourceManager(symbol=symbol)
        if self.data_source.is_available():
            print(f"✅ 使用数据源: {self.data_source.current_data_source_name}({symbol})")
            print(f"   (支持自动切换: 东方财富 > 新浪 > 腾讯)")
        else:
            raise Exception("所有数据源都不可用")
        
        self.klines = KlineData()
        
        self.strategy = Strategy333(symbol=symbol, ma_period=ma_period)
        self.account = SimulatedAccount(initial_balance=initial_balance)
        
        self.is_running = False
        self.tick_count = 0
        
        self.logger.log_system("系统初始化", {
            "symbol": symbol,
            "initial_balance": initial_balance,
            "ma_period": ma_period
        })
    
    def initialize(self, kline_count: int = 2000) -> None:
        """
        初始化系统数据
        
        Args:
            kline_count: 初始K线数量（建议>=50以确保MA30计算）
        """
        self.logger.info(f"正在初始化系统数据，获取最近{kline_count}根K线...")
        
        klines = self.data_source.fetch_klines(count=kline_count)
        self.klines.add_batch(klines)
        
        if len(klines) < 30:
            error_msg = f"数据不足：获取到{len(klines)}根K线，至少需要30根才能计算MA30"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 关键修复：用获取的K线数据更新MA30计算
        self.strategy.update_indicators(self.klines)
        
        self.logger.log_system("数据初始化完成", {
            "kline_count": len(klines),
            "symbol": self.symbol,
            "ma_period": self.ma_period,
            "current_ma": self.strategy.current_ma
        })
    
    def tick(self) -> Optional[dict]:
        """
        执行一次交易tick
        
        Returns:
            交易结果信息
        """
        self.tick_count += 1
        
        current_quote = self.data_source.get_realtime_quote()
        if current_quote is None:
            return None
        
        current_price = current_quote['price']
        timestamp = current_quote['timestamp']
        
        new_kline = type('Kline', (), {
            'symbol': self.symbol,
            'timestamp': timestamp,
            'open': current_quote['open'],
            'high': current_quote['high'],
            'low': current_quote['low'],
            'close': current_price,
            'volume': current_quote['volume']
        })()
        
        self.klines.add(new_kline)
        
        ma30 = self.strategy.update_indicators(self.klines)[0]
        
        self.account.update_position_profit(current_price)
        
        signal = self.strategy.generate_signal(
            klines=self.klines,
            position=self.account.position
        )
        
        result = {
            "tick": self.tick_count,
            "timestamp": timestamp,
            "price": current_price,
            "ma30": ma30,
            "signal": None,
            "trade": None,
            "position": self.account.get_position_summary(current_price),
            "account": self.account.get_account_summary(current_price)
        }
        
        if signal:
            result["signal"] = signal.to_dict()
            self.logger.log_signal(signal.to_dict())
            self.signal_logger.log_signal(signal.to_dict())
            
            if signal.signal_type.value == "BUY":
                if self.account.can_buy(current_price, self._calculate_quantity(current_price)):
                    quantity = self._calculate_quantity(current_price)
                    trade = self.account.execute_buy(
                        symbol=self.symbol,
                        price=current_price,
                        quantity=quantity,
                        timestamp=timestamp
                    )
                    if trade:
                        result["trade"] = trade.to_dict()
                        self.logger.log_trade(trade.to_dict())
                        self.signal_logger.log_trade(trade.to_dict())
            
            elif signal.signal_type.value == "SELL":
                if self.account.position:
                    quantity = self.account.position.quantity
                    trade = self.account.execute_sell(
                        symbol=self.symbol,
                        price=current_price,
                        quantity=quantity,
                        timestamp=timestamp,
                        notes="分手卖出"
                    )
                    if trade:
                        result["trade"] = trade.to_dict()
                        self.logger.log_trade(trade.to_dict())
                        self.signal_logger.log_trade(trade.to_dict())
            
            elif signal.signal_type.value == "TAKE_PROFIT_1":
                if self.account.position:
                    quantity = int(self.account.position.quantity * 0.5)
                    if quantity > 0:
                        trade = self.account.execute_sell(
                            symbol=self.symbol,
                            price=current_price,
                            quantity=quantity,
                            timestamp=timestamp,
                            notes="一阶段止盈"
                        )
                        if trade:
                            self.account.position.stop_loss_stage = 1
                            result["trade"] = trade.to_dict()
                            self.logger.log_trade(trade.to_dict())
                            self.signal_logger.log_trade(trade.to_dict())
            
            elif signal.signal_type.value == "TAKE_PROFIT_2":
                if self.account.position:
                    quantity = int(self.account.position.quantity * 0.3)
                    if quantity > 0:
                        trade = self.account.execute_sell(
                            symbol=self.symbol,
                            price=current_price,
                            quantity=quantity,
                            timestamp=timestamp,
                            notes="二阶段止盈"
                        )
                        if trade:
                            self.account.position.stop_loss_stage = 2
                            result["trade"] = trade.to_dict()
                            self.logger.log_trade(trade.to_dict())
                            self.signal_logger.log_trade(trade.to_dict())
        
        return result
    
    def _calculate_quantity(self, price: float) -> int:
        """
        计算可买入数量
        
        Args:
            price: 价格
            
        Returns:
            可买入数量
        """
        available = self.account.available_balance
        max_quantity = int(available / (price * 1.0003))
        
        return (max_quantity // 100) * 100
    
    def start(self, ticks: int = 100) -> list[dict]:
        """
        启动系统运行
        
        Args:
            ticks: 运行tick数量
            
        Returns:
            运行结果列表
        """
        self.logger.log_system("系统启动", {"ticks": ticks})
        self.is_running = True
        
        results = []
        for i in range(ticks):
            result = self.tick()
            if result:
                results.append(result)
        
        self.is_running = False
        self.logger.log_system("系统停止", {"total_ticks": ticks})
        
        return results
    
    def get_status(self) -> dict:
        """
        获取系统状态
        
        Returns:
            系统状态信息
        """
        current_quote = self.data_source.get_realtime_quote()
        current_price = current_quote['price'] if current_quote else None
        
        return {
            "is_running": self.is_running,
            "symbol": self.symbol,
            "ma_period": self.ma_period,
            "tick_count": self.tick_count,
            "kline_count": self.klines.count,
            "current_ma": self.strategy.current_ma,
            "position": self.account.get_position_summary(current_price),
            "account": self.account.get_account_summary(current_price)
        }
    
    def reset(self) -> None:
        """重置系统"""
        self.logger.log_system("系统重置")
        self.strategy.reset()
        self.account.reset()
        self.klines.clear()
        self.tick_count = 0


def create_system(
    symbol: str = "588200",
    initial_balance: float = 100000.0,
    ma_period: int = 30,
    kline_count: int = 2000
) -> TradingSystem:
    """
    创建交易系统实例
    
    Args:
        symbol: 交易标的代码
        initial_balance: 初始资金
        ma_period: MA周期
        kline_count: 初始化K线数量
        
    Returns:
        交易系统实例
    """
    system = TradingSystem(
        symbol=symbol,
        initial_balance=initial_balance,
        ma_period=ma_period
    )
    system.initialize(kline_count=kline_count)
    return system


if __name__ == "__main__":
    print("=" * 60)
    print("333交易系统启动")
    print("=" * 60)
    
    # 配置参数
    symbol = "588200"
    initial_balance = 100000.0
    ticks = 100
    
    system = create_system(
        symbol=symbol,
        initial_balance=initial_balance
    )
    
    print(f"\n✅ 系统初始化完成")
    print(f"初始资金: {system.account.initial_balance}")
    print(f"交易标的: {system.symbol}")
    print(f"MA周期: {system.ma_period}")
    print(f"初始K线数量: {system.klines.count}")
    print(f"当前数据源: {system.data_source.current_data_source_name}")
    
    print("\n🚀 开始运行回测...")
    results = system.start(ticks=ticks)
    
    print(f"\n✅ 回测完成，共运行 {len(results)} 个tick")
    
    account_summary = system.account.get_account_summary()
    print(f"\n📊 账户摘要:")
    print(f"  最终资金: {account_summary['balance']:.2f}")
    print(f"  总资产: {account_summary['total_assets']:.2f}")
    print(f"  总盈利: {account_summary['total_profit']:.2f}")
    print(f"  收益率: {account_summary['profit_rate']*100:.2f}%")
    print(f"  总手续费: {account_summary['total_commission']:.2f}")
    
    trades = system.account.trade_recorder.get_records()
    print(f"\n📜 交易记录: 共 {len(trades)} 笔")
    for i, trade in enumerate(trades[:5], 1):
        print(f"  {i}. {trade.datetime_str} {trade.action_name} {trade.symbol} 价格:{trade.price} 数量:{trade.quantity}")
    
    print("\n" + "=" * 60)
    print("333交易系统运行结束")
    print("=" * 60)
