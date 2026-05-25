"""
333交易系统 - 交易记录模型

定义交易记录数据结构，用于记录所有交易行为
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json
import uuid


class TradeAction(Enum):
    """交易动作枚举"""
    BUY = "BUY"
    SELL = "SELL"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


@dataclass
class TradeRecord:
    """交易记录数据模型"""
    
    trade_id: str
    order_id: str
    timestamp: int
    symbol: str
    action: TradeAction
    price: float
    quantity: int
    amount: float
    commission: float = 0.0
    status: OrderStatus = OrderStatus.FILLED
    order_type: str = "MARKET"
    profit: float = 0.0
    notes: str = ""
    
    @property
    def datetime(self) -> datetime:
        """将时间戳转换为datetime对象"""
        return datetime.fromtimestamp(self.timestamp / 1000)
    
    @property
    def datetime_str(self) -> str:
        """返回完整的日期时间字符串"""
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def action_name(self) -> str:
        """获取交易动作名称"""
        names = {
            TradeAction.BUY: "买入",
            TradeAction.SELL: "卖出",
            TradeAction.TAKE_PROFIT: "止盈",
        }
        return names.get(self.action, "未知")
    
    @property
    def status_name(self) -> str:
        """获取订单状态名称"""
        names = {
            OrderStatus.PENDING: "待处理",
            OrderStatus.SUBMITTED: "已提交",
            OrderStatus.FILLED: "已成交",
            OrderStatus.PARTIAL_FILLED: "部分成交",
            OrderStatus.CANCELLED: "已撤销",
            OrderStatus.REJECTED: "已拒绝",
            OrderStatus.FAILED: "失败",
        }
        return names.get(self.status, "未知")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "timestamp": self.timestamp,
            "datetime": self.datetime_str,
            "symbol": self.symbol,
            "action": self.action.value,
            "action_name": self.action_name,
            "price": round(self.price, 4),
            "quantity": self.quantity,
            "amount": round(self.amount, 2),
            "commission": round(self.commission, 2),
            "status": self.status.value,
            "status_name": self.status_name,
            "order_type": self.order_type,
            "profit": round(self.profit, 2) if self.profit else 0,
            "notes": self.notes,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "TradeRecord":
        """从字典创建TradeRecord对象"""
        return cls(
            trade_id=data["trade_id"],
            order_id=data["order_id"],
            timestamp=data["timestamp"],
            symbol=data["symbol"],
            action=TradeAction(data["action"]),
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            amount=float(data["amount"]),
            commission=float(data.get("commission", 0)),
            status=OrderStatus(data.get("status", "FILLED")),
            order_type=data.get("order_type", "MARKET"),
            profit=float(data.get("profit", 0)),
            notes=data.get("notes", ""),
        )
    
    def __str__(self) -> str:
        return f"TradeRecord({self.action_name}, {self.symbol}, 价格:{self.price}, 数量:{self.quantity}, 状态:{self.status_name})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Order:
    """订单数据模型"""
    
    order_id: str = field(default_factory=lambda: f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}")
    symbol: str = ""
    action: TradeAction = TradeAction.BUY
    order_type: str = "MARKET"
    price: float = 0.0
    quantity: int = 0
    status: OrderStatus = OrderStatus.PENDING
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    filled_quantity: int = 0
    filled_price: float = 0.0
    filled_time: Optional[int] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "action": self.action.value,
            "order_type": self.order_type,
            "price": self.price,
            "quantity": self.quantity,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "filled_quantity": self.filled_quantity,
            "filled_price": self.filled_price,
            "filled_time": self.filled_time,
        }
    
    def __str__(self) -> str:
        return f"Order({self.order_id}, {self.action.value}, {self.symbol}, 数量:{self.quantity}, 状态:{self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class TradeRecorder:
    """交易记录器"""
    
    def __init__(self):
        self._records: list[TradeRecord] = []
    
    def add_record(self, record: TradeRecord) -> None:
        """添加交易记录"""
        self._records.append(record)
    
    def get_records(self) -> list[TradeRecord]:
        """获取所有交易记录"""
        return self._records.copy()
    
    def get_records_by_symbol(self, symbol: str) -> list[TradeRecord]:
        """获取指定标的的交易记录"""
        return [r for r in self._records if r.symbol == symbol]
    
    def get_latest_record(self, symbol: str) -> Optional[TradeRecord]:
        """获取指定标的的最新交易记录"""
        records = self.get_records_by_symbol(symbol)
        return records[-1] if records else None
    
    def clear(self) -> None:
        """清空所有交易记录"""
        self._records.clear()
    
    def __len__(self) -> int:
        return len(self._records)
