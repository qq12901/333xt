"""
333交易系统 - K线数据模型

定义30分钟K线数据结构，用于存储和传输K线数据
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json


@dataclass
class Kline:
    """30分钟K线数据模型"""
    
    symbol: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    @property
    def datetime(self) -> datetime:
        """将时间戳转换为datetime对象"""
        return datetime.fromtimestamp(self.timestamp / 1000)
    
    @property
    def date_str(self) -> str:
        """返回日期字符串 YYYY-MM-DD"""
        return self.datetime.strftime("%Y-%m-%d")
    
    @property
    def time_str(self) -> str:
        """返回时间字符串 HH:MM:SS"""
        return self.datetime.strftime("%H:%M:%S")
    
    @property
    def datetime_str(self) -> str:
        """返回完整的日期时间字符串"""
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def is_bullish(self) -> bool:
        """判断是否为阳线（收盘价 >= 开盘价）"""
        return self.close >= self.open
    
    @property
    def is_bearish(self) -> bool:
        """判断是否为阴线（收盘价 < 开盘价）"""
        return self.close < self.open
    
    @property
    def body(self) -> float:
        """K线实体大小（收盘价 - 开盘价）"""
        return self.close - self.open
    
    @property
    def body_pct(self) -> float:
        """K线实体百分比"""
        if self.open == 0:
            return 0.0
        return (self.close - self.open) / self.open * 100
    
    @property
    def upper_shadow(self) -> float:
        """上影线长度"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_shadow(self) -> float:
        """下影线长度"""
        return min(self.open, self.close) - self.low
    
    @property
    def amplitude(self) -> float:
        """振幅（最高价 - 最低价）"""
        return self.high - self.low
    
    @property
    def amplitude_pct(self) -> float:
        """振幅百分比"""
        if self.low == 0:
            return 0.0
        return (self.high - self.low) / self.low * 100
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "datetime": self.datetime_str,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Kline":
        """从字典创建Kline对象"""
        return cls(
            symbol=data["symbol"],
            timestamp=data["timestamp"],
            open=float(data["open"]),
            high=float(data["high"]),
            low=float(data["low"]),
            close=float(data["close"]),
            volume=int(data["volume"]),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Kline":
        """从JSON字符串创建Kline对象"""
        return cls.from_dict(json.loads(json_str))
    
    def __str__(self) -> str:
        return f"Kline({self.symbol}, {self.datetime_str}, O:{self.open}, H:{self.high}, L:{self.low}, C:{self.close}, V:{self.volume})"
    
    def __repr__(self) -> str:
        return self.__str__()


class KlineData:
    """K线数据集合管理类"""
    
    def __init__(self):
        self._klines: list[Kline] = []
        self._symbol: Optional[str] = None
    
    @property
    def klines(self) -> list[Kline]:
        """获取所有K线数据"""
        return self._klines.copy()
    
    @property
    def symbol(self) -> Optional[str]:
        """获取交易标的"""
        return self._symbol
    
    @property
    def count(self) -> int:
        """获取K线数量"""
        return len(self._klines)
    
    @property
    def closes(self) -> list[float]:
        """获取所有收盘价"""
        return [k.close for k in self._klines]
    
    @property
    def latest(self) -> Optional[Kline]:
        """获取最后一根K线"""
        return self._klines[-1] if self._klines else None
    
    @property
    def first(self) -> Optional[Kline]:
        """获取第一根K线"""
        return self._klines[0] if self._klines else None
    
    def add(self, kline: Kline) -> None:
        """添加一根K线"""
        if self._symbol is None:
            self._symbol = kline.symbol
        elif self._symbol != kline.symbol:
            raise ValueError(f"Symbol mismatch: expected {self._symbol}, got {kline.symbol}")
        self._klines.append(kline)
    
    def add_batch(self, klines: list[Kline]) -> None:
        """批量添加K线"""
        for kline in klines:
            self.add(kline)
    
    def get_by_index(self, index: int) -> Optional[Kline]:
        """根据索引获取K线（支持负索引）"""
        if -len(self._klines) <= index < len(self._klines):
            return self._klines[index]
        return None
    
    def get_by_timestamp(self, timestamp: int) -> Optional[Kline]:
        """根据时间戳获取K线"""
        for kline in self._klines:
            if kline.timestamp == timestamp:
                return kline
        return None
    
    def get_range(self, start: int, end: int) -> list[Kline]:
        """获取指定范围的K线（索引）"""
        return self._klines[start:end]
    
    def get_latest_n(self, n: int) -> list[Kline]:
        """获取最近N根K线"""
        if n >= len(self._klines):
            return self._klines.copy()
        return self._klines[-n:]
    
    def clear(self) -> None:
        """清空所有K线数据"""
        self._klines.clear()
        self._symbol = None
    
    def to_list(self) -> list[dict]:
        """转换为字典列表"""
        return [k.to_dict() for k in self._klines]
    
    def __len__(self) -> int:
        return self.count
    
    def __iter__(self):
        return iter(self._klines)
    
    def __getitem__(self, index):
        """支持切片和单个索引访问"""
        if isinstance(index, slice):
            return self._klines[index]
        return self.get_by_index(index)
