"""
333交易系统 - 持仓状态模型

定义持仓状态数据结构，用于跟踪和管理交易持仓
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json
import uuid


class PositionStatus(Enum):
    """持仓状态枚举"""
    EMPTY = "EMPTY"
    HOLDING = "HOLDING"
    PROFIT_TAKING_1 = "PROFIT_TAKING_1"
    PROFIT_TAKING_2 = "PROFIT_TAKING_2"


@dataclass
class Position:
    """持仓状态数据模型"""
    
    symbol: str
    status: PositionStatus = PositionStatus.EMPTY
    entry_price: float = 0.0
    entry_time: Optional[datetime] = None
    quantity: int = 0
    current_profit_rate: float = 0.0
    withdrawn_profit: float = 0.0
    stop_loss_stage: int = 0
    position_id: str = field(default_factory=lambda: f"POS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}")
    
    @property
    def is_empty(self) -> bool:
        """是否为空仓"""
        return self.status == PositionStatus.EMPTY
    
    @property
    def is_holding(self) -> bool:
        """是否在持仓中"""
        return self.status in [PositionStatus.HOLDING, PositionStatus.PROFIT_TAKING_1, PositionStatus.PROFIT_TAKING_2]
    
    @property
    def has_position(self) -> bool:
        """是否有持仓"""
        return self.quantity > 0
    
    @property
    def cost_basis(self) -> float:
        """持仓成本"""
        return self.entry_price * self.quantity
    
    def calculate_profit_rate(self, current_price: float) -> float:
        """计算当前盈亏率"""
        if self.entry_price == 0 or self.quantity == 0:
            return 0.0
        return (current_price - self.entry_price) / self.entry_price
    
    def calculate_profit(self, current_price: float) -> float:
        """计算当前盈亏金额"""
        return (current_price - self.entry_price) * self.quantity
    
    def update_profit(self, current_price: float) -> None:
        """更新当前盈亏"""
        self.current_profit_rate = self.calculate_profit_rate(current_price)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "status": self.status.value,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.strftime("%Y-%m-%d %H:%M:%S") if self.entry_time else None,
            "quantity": self.quantity,
            "current_profit_rate": round(self.current_profit_rate, 4),
            "withdrawn_profit": round(self.withdrawn_profit, 2),
            "stop_loss_stage": self.stop_loss_stage,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        """从字典创建Position对象"""
        entry_time = None
        if data.get("entry_time"):
            entry_time = datetime.strptime(data["entry_time"], "%Y-%m-%d %H:%M:%S")
        
        return cls(
            symbol=data["symbol"],
            status=PositionStatus(data["status"]),
            entry_price=float(data["entry_price"]),
            entry_time=entry_time,
            quantity=int(data["quantity"]),
            current_profit_rate=float(data.get("current_profit_rate", 0)),
            withdrawn_profit=float(data.get("withdrawn_profit", 0)),
            stop_loss_stage=int(data.get("stop_loss_stage", 0)),
            position_id=data.get("position_id", f"POS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"),
        )
    
    def __str__(self) -> str:
        status_name = {
            PositionStatus.EMPTY: "空仓",
            PositionStatus.HOLDING: "持仓中",
            PositionStatus.PROFIT_TAKING_1: "一阶段止盈",
            PositionStatus.PROFIT_TAKING_2: "二阶段止盈",
        }
        profit_pct = f"{self.current_profit_rate * 100:.2f}%" if self.current_profit_rate else "0.00%"
        return f"Position({self.symbol}, {status_name.get(self.status, '未知')}, 入场:{self.entry_price}, 数量:{self.quantity}, 盈亏:{profit_pct})"
    
    def __repr__(self) -> str:
        return self.__str__()


class PositionManager:
    """持仓管理器"""
    
    def __init__(self):
        self._positions: dict[str, Position] = {}
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取指定标的的持仓"""
        return self._positions.get(symbol)
    
    def create_position(self, symbol: str, entry_price: float, quantity: int) -> Position:
        """创建新持仓"""
        position = Position(
            symbol=symbol,
            status=PositionStatus.HOLDING,
            entry_price=entry_price,
            entry_time=datetime.now(),
            quantity=quantity,
            stop_loss_stage=0,
        )
        self._positions[symbol] = position
        return position
    
    def close_position(self, symbol: str) -> None:
        """平仓"""
        if symbol in self._positions:
            del self._positions[symbol]
    
    def update_all_profits(self, prices: dict[str, float]) -> None:
        """更新所有持仓的盈亏"""
        for symbol, position in self._positions.items():
            if symbol in prices:
                position.update_profit(prices[symbol])
    
    def get_all_positions(self) -> list[Position]:
        """获取所有持仓"""
        return list(self._positions.values())
    
    def clear(self) -> None:
        """清空所有持仓"""
        self._positions.clear()
