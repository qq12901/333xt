"""
333交易系统 - 交易信号模型

定义交易信号数据结构，用于表示买入、卖出和止盈信号
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json
import uuid


class SignalType(Enum):
    """信号类型枚举"""
    BUY = "BUY"
    SELL = "SELL"
    TAKE_PROFIT_1 = "TAKE_PROFIT_1"
    TAKE_PROFIT_2 = "TAKE_PROFIT_2"
    HOLD = "HOLD"


class SignalTrigger(Enum):
    """信号触发原因枚举"""
    PRICE_ABOVE_MA30 = "PRICE_ABOVE_MA30"
    PRICE_BELOW_MA30 = "PRICE_BELOW_MA30"
    PROFIT_TARGET_1 = "PROFIT_TARGET_1"
    PROFIT_TARGET_2 = "PROFIT_TARGET_2"
    MANUAL = "MANUAL"
    STOP_LOSS = "STOP_LOSS"


@dataclass
class Signal:
    """交易信号数据模型"""
    
    signal_type: SignalType
    symbol: str
    timestamp: int
    price: float
    trigger: SignalTrigger
    reason: str
    ma30: float = 0.0
    profit_rate: float = 0.0
    signal_id: str = field(default_factory=lambda: f"SIG_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}")
    is_valid: bool = True
    executed: bool = False
    
    @property
    def datetime(self) -> datetime:
        """将时间戳转换为datetime对象"""
        return datetime.fromtimestamp(self.timestamp / 1000)
    
    @property
    def datetime_str(self) -> str:
        """返回完整的日期时间字符串"""
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def signal_name(self) -> str:
        """获取信号类型名称"""
        names = {
            SignalType.BUY: "买入",
            SignalType.SELL: "卖出",
            SignalType.TAKE_PROFIT_1: "一阶段止盈",
            SignalType.TAKE_PROFIT_2: "二阶段止盈",
            SignalType.HOLD: "持有",
        }
        return names.get(self.signal_type, "未知")
    
    @property
    def trigger_name(self) -> str:
        """获取触发原因名称"""
        names = {
            SignalTrigger.PRICE_ABOVE_MA30: "价格上穿MA30",
            SignalTrigger.PRICE_BELOW_MA30: "价格下穿MA30",
            SignalTrigger.PROFIT_TARGET_1: "盈利达到1%",
            SignalTrigger.PROFIT_TARGET_2: "盈利达到3%",
            SignalTrigger.MANUAL: "手动触发",
            SignalTrigger.STOP_LOSS: "止损",
        }
        return names.get(self.trigger, "未知")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "signal_name": self.signal_name,
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "datetime": self.datetime_str,
            "price": self.price,
            "trigger": self.trigger.value,
            "trigger_name": self.trigger_name,
            "reason": self.reason,
            "ma30": round(self.ma30, 4) if self.ma30 else 0,
            "profit_rate": round(self.profit_rate, 4) if self.profit_rate else 0,
            "is_valid": self.is_valid,
            "executed": self.executed,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Signal":
        """从字典创建Signal对象"""
        return cls(
            signal_type=SignalType(data["signal_type"]),
            symbol=data["symbol"],
            timestamp=data["timestamp"],
            price=float(data["price"]),
            trigger=SignalTrigger(data["trigger"]),
            reason=data["reason"],
            ma30=float(data.get("ma30", 0)),
            profit_rate=float(data.get("profit_rate", 0)),
            signal_id=data.get("signal_id", f"SIG_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"),
            is_valid=data.get("is_valid", True),
            executed=data.get("executed", False),
        )
    
    def mark_executed(self) -> None:
        """标记为已执行"""
        self.executed = True
    
    def invalidate(self) -> None:
        """使信号失效"""
        self.is_valid = False
    
    def __str__(self) -> str:
        return f"Signal({self.signal_name}, {self.symbol}, 价格:{self.price}, {self.trigger_name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class SignalGenerator:
    """信号生成器"""
    
    def __init__(self, symbol: str):
        self._symbol = symbol
        self._last_signal: Optional[Signal] = None
    
    @property
    def last_signal(self) -> Optional[Signal]:
        """获取上一个信号"""
        return self._last_signal
    
    def generate_buy_signal(self, price: float, ma30: float, timestamp: int) -> Signal:
        """生成买入信号"""
        signal = Signal(
            signal_type=SignalType.BUY,
            symbol=self._symbol,
            timestamp=timestamp,
            price=price,
            trigger=SignalTrigger.PRICE_ABOVE_MA30,
            reason=f"价格({price})上穿MA30({ma30:.4f})，触发牵手买入信号",
            ma30=ma30,
        )
        self._last_signal = signal
        return signal
    
    def generate_sell_signal(self, price: float, ma30: float, timestamp: int) -> Signal:
        """生成卖出信号"""
        signal = Signal(
            signal_type=SignalType.SELL,
            symbol=self._symbol,
            timestamp=timestamp,
            price=price,
            trigger=SignalTrigger.PRICE_BELOW_MA30,
            reason=f"价格({price})下穿MA30({ma30:.4f})，触发分手卖出信号",
            ma30=ma30,
        )
        self._last_signal = signal
        return signal
    
    def generate_take_profit_1_signal(self, price: float, entry_price: float, ma30: float, timestamp: int) -> Signal:
        """生成一阶段止盈信号"""
        profit_rate = (price - entry_price) / entry_price
        signal = Signal(
            signal_type=SignalType.TAKE_PROFIT_1,
            symbol=self._symbol,
            timestamp=timestamp,
            price=price,
            trigger=SignalTrigger.PROFIT_TARGET_1,
            reason=f"盈利达到{profit_rate*100:.2f}%，触发一阶段止盈信号",
            ma30=ma30,
            profit_rate=profit_rate,
        )
        self._last_signal = signal
        return signal
    
    def generate_take_profit_2_signal(self, price: float, entry_price: float, ma30: float, timestamp: int) -> Signal:
        """生成二阶段止盈信号"""
        profit_rate = (price - entry_price) / entry_price
        signal = Signal(
            signal_type=SignalType.TAKE_PROFIT_2,
            symbol=self._symbol,
            timestamp=timestamp,
            price=price,
            trigger=SignalTrigger.PROFIT_TARGET_2,
            reason=f"盈利达到{profit_rate*100:.2f}%，触发二阶段止盈信号",
            ma30=ma30,
            profit_rate=profit_rate,
        )
        self._last_signal = signal
        return signal
    
    def generate_hold_signal(self) -> Optional[Signal]:
        """生成持有信号"""
        return Signal(
            signal_type=SignalType.HOLD,
            symbol=self._symbol,
            timestamp=int(datetime.now().timestamp() * 1000),
            price=0,
            trigger=SignalTrigger.MANUAL,
            reason="当前无有效信号，维持现有状态",
        )
