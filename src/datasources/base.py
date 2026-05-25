"""
333交易系统 - 数据源接口基类

定义数据源抽象接口，用于支持多种数据源
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.kline import Kline, KlineData


class DataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, symbol: str):
        """
        初始化数据源
        
        Args:
            symbol: 交易标的代码
        """
        self.symbol = symbol
        self._klines = KlineData()
    
    @abstractmethod
    def fetch_klines(self, count: int = 100) -> List[Kline]:
        """
        获取K线数据
        
        Args:
            count: 获取数量
            
        Returns:
            K线数据列表
        """
        pass
    
    @abstractmethod
    def fetch_history(self, start_time: int, end_time: int) -> List[Kline]:
        """
        获取历史K线数据
        
        Args:
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            
        Returns:
            K线数据列表
        """
        pass
    
    @abstractmethod
    def get_realtime_quote(self) -> Optional[dict]:
        """
        获取实时行情
        
        Returns:
            实时行情数据
        """
        pass
    
    def get_cached_klines(self) -> KlineData:
        """
        获取缓存的K线数据
        
        Returns:
            K线数据集合
        """
        return self._klines
    
    def update_cache(self, klines: List[Kline]) -> None:
        """
        更新缓存的K线数据
        
        Args:
            klines: K线数据列表
        """
        self._klines.add_batch(klines)
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._klines.clear()
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查数据源是否可用
        
        Returns:
            是否可用
        """
        pass
    
    def validate_kline(self, kline: Kline) -> bool:
        """
        验证K线数据是否有效
        
        Args:
            kline: K线数据
            
        Returns:
            是否有效
        """
        if kline.high < kline.low:
            return False
        if kline.high < kline.close or kline.high < kline.open:
            return False
        if kline.low > kline.close or kline.low > kline.open:
            return False
        if kline.close <= 0 or kline.open <= 0:
            return False
        return True
