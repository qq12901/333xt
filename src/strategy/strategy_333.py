"""
333交易系统 - 333策略核心逻辑

实现333趋势跟踪策略的完整交易逻辑
"""
from typing import Optional, Tuple
from ..models.kline import KlineData
from ..models.position import Position, PositionStatus
from ..models.signal import Signal, SignalType, SignalTrigger, SignalGenerator
from ..indicators.ma import MAEngine


class Strategy333:
    """333趋势跟踪策略"""
    
    def __init__(self, symbol: str, ma_period: int = 30):
        """
        初始化333策略
        
        Args:
            symbol: 交易标的代码
            ma_period: MA周期，默认30
        """
        self.symbol = symbol
        self.ma_period = ma_period
        
        self.ma_engine = MAEngine(period=ma_period)
        self.signal_generator = SignalGenerator(symbol=symbol)
        
        self.profit_target_1 = 0.01
        self.profit_target_2 = 0.03
        
        self._prev_price: Optional[float] = None
        self._prev_ma: Optional[float] = None
        self.cross_confirm_threshold = 0.005
    
    @property
    def current_ma(self) -> Optional[float]:
        """获取当前MA30值"""
        return self.ma_engine.current_ma
    
    def update_indicators(self, klines: KlineData) -> Tuple[Optional[float], Optional[float]]:
        """
        更新指标计算
        
        Args:
            klines: K线数据
            
        Returns:
            (当前MA值, 前一MA值)
        """
        self._prev_ma = self.ma_engine.current_ma
        current_ma = self.ma_engine.update(klines)
        return current_ma, self._prev_ma
    
    def check_trend(self, price: float) -> str:
        """
        检查趋势方向
        
        Args:
            price: 当前价格
            
        Returns:
            趋势方向 ('up', 'down', 'neutral')
        """
        current_ma = self.current_ma
        if current_ma is None:
            return 'neutral'
        
        if price > current_ma:
            return 'up'
        elif price < current_ma:
            return 'down'
        else:
            return 'neutral'
    
    def check_cross(self, price: float) -> Optional[str]:
        """
        检查价格是否穿越MA30
        
        增加确认机制：价格需要明显穿越MA30 0.5%以上才算有效穿越
        
        Args:
            price: 当前价格
            
        Returns:
            穿越方向 ('above', 'below') 或 None（无穿越）
        """
        if self._prev_price is None or self._prev_ma is None:
            self._prev_price = price
            return None
        
        current_ma = self.current_ma
        if current_ma is None:
            return None
        
        threshold = current_ma * self.cross_confirm_threshold
        
        if self._prev_price <= self._prev_ma and price > current_ma + threshold:
            self._prev_price = price
            return 'above'
        
        elif self._prev_price >= self._prev_ma and price < current_ma - threshold:
            self._prev_price = price
            return 'below'
        
        self._prev_price = price
        return None
    
    def calculate_profit_rate(self, current_price: float, entry_price: float) -> float:
        """
        计算盈亏率
        
        Args:
            current_price: 当前价格
            entry_price: 买入价格
            
        Returns:
            盈亏率
        """
        if entry_price == 0:
            return 0.0
        return (current_price - entry_price) / entry_price
    
    def generate_signal(
        self, 
        klines: KlineData, 
        position: Optional[Position]
    ) -> Optional[Signal]:
        """
        生成交易信号
        
        Args:
            klines: K线数据
            position: 当前持仓状态
            
        Returns:
            交易信号或None
        """
        if klines.latest is None:
            return None
        
        current_price = klines.latest.close
        current_ma = self.update_indicators(klines)[0]
        
        if current_ma is None:
            return None
        
        cross = self.check_cross(current_price)
        
        if position is None or position.is_empty:
            if cross == 'above':
                return self.signal_generator.generate_buy_signal(
                    price=current_price,
                    ma30=current_ma,
                    timestamp=klines.latest.timestamp
                )
        
        elif position.is_holding:
            if cross == 'below':
                return self.signal_generator.generate_sell_signal(
                    price=current_price,
                    ma30=current_ma,
                    timestamp=klines.latest.timestamp
                )
            
            profit_rate = self.calculate_profit_rate(
                current_price=current_price,
                entry_price=position.entry_price
            )
            
            if profit_rate >= self.profit_target_1 and position.stop_loss_stage == 0:
                return self.signal_generator.generate_take_profit_1_signal(
                    price=current_price,
                    entry_price=position.entry_price,
                    ma30=current_ma,
                    timestamp=klines.latest.timestamp
                )
            
            if profit_rate >= self.profit_target_2 and position.stop_loss_stage == 0:
                return self.signal_generator.generate_take_profit_2_signal(
                    price=current_price,
                    entry_price=position.entry_price,
                    ma30=current_ma,
                    timestamp=klines.latest.timestamp
                )
        
        self._prev_price = current_price
        return None
    
    def should_buy(self, price: float) -> bool:
        """
        判断是否应该买入
        
        Args:
            price: 当前价格
            
        Returns:
            是否应该买入
        """
        return self.check_trend(price) == 'up' and self.check_cross(price) == 'above'
    
    def should_sell(self, price: float) -> bool:
        """
        判断是否应该卖出
        
        Args:
            price: 当前价格
            
        Returns:
            是否应该卖出
        """
        return self.check_trend(price) == 'down' and self.check_cross(price) == 'below'
    
    def should_take_profit_1(self, current_price: float, entry_price: float) -> bool:
        """
        判断是否应该一阶段止盈
        
        Args:
            current_price: 当前价格
            entry_price: 买入价格
            
        Returns:
            是否应该止盈
        """
        profit_rate = self.calculate_profit_rate(current_price, entry_price)
        return profit_rate >= self.profit_target_1
    
    def should_take_profit_2(self, current_price: float, entry_price: float) -> bool:
        """
        判断是否应该二阶段止盈
        
        Args:
            current_price: 当前价格
            entry_price: 买入价格
            
        Returns:
            是否应该止盈
        """
        profit_rate = self.calculate_profit_rate(current_price, entry_price)
        return profit_rate >= self.profit_target_2
    
    def reset(self) -> None:
        """重置策略状态"""
        self.ma_engine.reset()
        self._prev_price = None
        self._prev_ma = None
