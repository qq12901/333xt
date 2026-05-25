"""
333交易系统 - 移动平均线指标计算

实现MA30移动平均线的计算，支持增量计算和缓存优化
"""
from typing import List, Optional
from ..models.kline import Kline, KlineData


class MovingAverage:
    """移动平均线计算器"""
    
    def __init__(self, period: int = 30):
        """
        初始化移动平均线计算器
        
        Args:
            period: 移动平均周期，默认30
        """
        self.period = period
        self._cache = {}
    
    def calculate(self, closes: List[float]) -> List[float]:
        """
        计算移动平均线
        
        Args:
            closes: 收盘价列表
            
        Returns:
            移动平均线值列表
        """
        if len(closes) < self.period:
            return []
        
        result = []
        for i in range(self.period - 1, len(closes)):
            ma = sum(closes[i - self.period + 1:i + 1]) / self.period
            result.append(ma)
        
        return result
    
    def calculate_single(self, closes: List[float]) -> Optional[float]:
        """
        计算最新的移动平均线值
        
        Args:
            closes: 收盘价列表
            
        Returns:
            最新的MA值，如果数据不足返回None
        """
        if len(closes) < self.period:
            return None
        
        return sum(closes[-self.period:]) / self.period
    
    def incremental_calculate(self, closes: List[float], prev_ma: float) -> Optional[float]:
        """
        增量计算移动平均线（更高效）
        
        Args:
            closes: 收盘价列表（包含最新价格）
            prev_ma: 上一个MA值
            
        Returns:
            最新的MA值，如果数据不足返回None
        """
        if len(closes) < self.period:
            return None
        
        if len(closes) == self.period:
            return self.calculate_single(closes)
        
        prev_closes_sum = closes[-self.period - 1]
        new_closes_sum = closes[-1]
        
        new_ma = prev_ma + (new_closes_sum - prev_closes_sum) / self.period
        return new_ma
    
    def get_value(self, klines: KlineData) -> Optional[float]:
        """
        从K线数据获取MA值
        
        Args:
            klines: K线数据对象
            
        Returns:
            MA值
        """
        return self.calculate_single(klines.closes)
    
    def get_all_values(self, klines: KlineData) -> List[float]:
        """
        获取所有MA值
        
        Args:
            klines: K线数据对象
            
        Returns:
            MA值列表
        """
        return self.calculate(klines.closes)


class MAEngine:
    """MA指标引擎"""
    
    def __init__(self, period: int = 30):
        """
        初始化MA引擎
        
        Args:
            period: 移动平均周期
        """
        self.ma_calculator = MovingAverage(period)
        self.period = period
        self._current_ma: Optional[float] = None
        self._prev_ma: Optional[float] = None
    
    @property
    def current_ma(self) -> Optional[float]:
        """获取当前MA值"""
        return self._current_ma
    
    @property
    def prev_ma(self) -> Optional[float]:
        """获取前一个MA值"""
        return self._prev_ma
    
    def update(self, klines: KlineData) -> Optional[float]:
        """
        更新MA值
        
        Args:
            klines: K线数据
            
        Returns:
            最新的MA值
        """
        self._prev_ma = self._current_ma
        
        if self._current_ma is None:
            self._current_ma = self.ma_calculator.calculate_single(klines.closes)
        else:
            self._current_ma = self.ma_calculator.incremental_calculate(
                klines.closes, 
                self._current_ma
            )
        
        return self._current_ma
    
    def calculate_all(self, klines: KlineData) -> List[float]:
        """
        计算所有历史MA值
        
        Args:
            klines: K线数据
            
        Returns:
            MA值列表
        """
        return self.ma_calculator.calculate(klines.closes)
    
    def reset(self) -> None:
        """重置MA引擎"""
        self._current_ma = None
        self._prev_ma = None


def calculate_ma(closes: List[float], period: int = 30) -> List[float]:
    """
    便捷函数：计算移动平均线
    
    Args:
        closes: 收盘价列表
        period: 周期，默认30
        
    Returns:
        MA值列表
    """
    ma = MovingAverage(period)
    return ma.calculate(closes)


def calculate_ma_single(closes: List[float], period: int = 30) -> Optional[float]:
    """
    便捷函数：计算最新MA值
    
    Args:
        closes: 收盘价列表
        period: 周期，默认30
        
    Returns:
        最新MA值
    """
    ma = MovingAverage(period)
    return ma.calculate_single(closes)
