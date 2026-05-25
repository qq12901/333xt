"""
333交易系统 - 模拟交易执行器

实现模拟账户和模拟成交处理
"""
from datetime import datetime
from typing import Optional
from ..models.position import Position, PositionStatus
from ..models.signal import Signal, SignalType
from ..models.trade import TradeRecord, Order, TradeAction, OrderStatus, TradeRecorder
import uuid


class SimulatedAccount:
    """模拟账户"""
    
    def __init__(self, initial_balance: float = 100000.0):
        """
        初始化模拟账户
        
        Args:
            initial_balance: 初始资金
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.frozen_balance = 0.0
        self.total_profit = 0.0
        self.total_commission = 0.0
        self.position: Optional[Position] = None
        self.trade_recorder = TradeRecorder()
    
    @property
    def available_balance(self) -> float:
        """可用资金"""
        return self.balance - self.frozen_balance
    
    @property
    def market_value(self) -> float:
        """持仓市值（向后兼容，使用入场价）"""
        if self.position and self.position.quantity > 0:
            return self.position.quantity * self.position.entry_price
        return 0.0
    
    def calculate_market_value(self, current_price: float) -> float:
        """
        计算持仓市值（使用当前价格）
        
        Args:
            current_price: 当前价格
            
        Returns:
            持仓市值
        """
        if self.position and self.position.quantity > 0:
            return self.position.quantity * current_price
        return 0.0
    
    @property
    def total_assets(self) -> float:
        """总资产"""
        return self.balance + self.market_value
    
    def can_buy(self, price: float, quantity: int) -> bool:
        """
        检查是否可以买入
        
        Args:
            price: 价格
            quantity: 数量
            
        Returns:
            是否可以买入
        """
        required_amount = price * quantity * (1 + 0.0003)
        return self.available_balance >= required_amount
    
    def execute_buy(
        self, 
        symbol: str, 
        price: float, 
        quantity: int,
        timestamp: int
    ) -> Optional[TradeRecord]:
        """
        执行买入
        
        Args:
            symbol: 标的代码
            price: 价格
            quantity: 数量
            timestamp: 时间戳
            
        Returns:
            交易记录
        """
        if not self.can_buy(price, quantity):
            return None
        
        commission = price * quantity * 0.0003
        amount = price * quantity
        
        order = Order(
            order_id=f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
            symbol=symbol,
            action=TradeAction.BUY,
            order_type="MARKET",
            price=price,
            quantity=quantity,
            status=OrderStatus.FILLED,
            timestamp=timestamp,
            filled_quantity=quantity,
            filled_price=price,
            filled_time=timestamp,
        )
        
        self.balance -= (amount + commission)
        self.total_commission += commission
        
        self.position = Position(
            symbol=symbol,
            status=PositionStatus.HOLDING,
            entry_price=price,
            entry_time=datetime.now(),
            quantity=quantity,
            stop_loss_stage=0,
        )
        
        trade_record = TradeRecord(
            trade_id=f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
            order_id=order.order_id,
            timestamp=timestamp,
            symbol=symbol,
            action=TradeAction.BUY,
            price=price,
            quantity=quantity,
            amount=amount,
            commission=commission,
            status=OrderStatus.FILLED,
            notes="牵手买入",
        )
        
        self.trade_recorder.add_record(trade_record)
        return trade_record
    
    def execute_sell(
        self, 
        symbol: str, 
        price: float, 
        quantity: int,
        timestamp: int,
        notes: str = "分手卖出"
    ) -> Optional[TradeRecord]:
        """
        执行卖出
        
        Args:
            symbol: 标的代码
            price: 价格
            quantity: 数量
            timestamp: 时间戳
            notes: 备注
            
        Returns:
            交易记录
        """
        if self.position is None or self.position.quantity < quantity:
            return None
        
        commission = price * quantity * 0.0003
        amount = price * quantity
        profit = (price - self.position.entry_price) * quantity - commission
        
        order = Order(
            order_id=f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
            symbol=symbol,
            action=TradeAction.SELL,
            order_type="MARKET",
            price=price,
            quantity=quantity,
            status=OrderStatus.FILLED,
            timestamp=timestamp,
            filled_quantity=quantity,
            filled_price=price,
            filled_time=timestamp,
        )
        
        self.balance += (amount - commission)
        self.total_commission += commission
        self.total_profit += profit
        
        remaining_quantity = self.position.quantity - quantity
        
        if remaining_quantity > 0:
            self.position.quantity = remaining_quantity
        else:
            self.position = None
        
        trade_record = TradeRecord(
            trade_id=f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
            order_id=order.order_id,
            timestamp=timestamp,
            symbol=symbol,
            action=TradeAction.SELL,
            price=price,
            quantity=quantity,
            amount=amount,
            commission=commission,
            status=OrderStatus.FILLED,
            profit=profit,
            notes=notes,
        )
        
        self.trade_recorder.add_record(trade_record)
        return trade_record
    
    def execute_take_profit(
        self,
        symbol: str,
        price: float,
        quantity: int,
        timestamp: int,
        profit: float
    ) -> Optional[TradeRecord]:
        """
        执行止盈卖出
        
        Args:
            symbol: 标的代码
            price: 价格
            quantity: 数量
            timestamp: 时间戳
            profit: 止盈金额
            
        Returns:
            交易记录
        """
        trade_record = self.execute_sell(
            symbol=symbol,
            price=price,
            quantity=quantity,
            timestamp=timestamp,
            notes=f"止盈卖出，盈利{profit:.2f}元"
        )
        
        if trade_record:
            self.total_profit += profit
        
        return trade_record
    
    def update_position_profit(self, current_price: float) -> None:
        """
        更新持仓盈亏
        
        Args:
            current_price: 当前价格
        """
        if self.position:
            self.position.update_profit(current_price)
    
    def get_position_summary(self, current_price: float = None) -> dict:
        """
        获取持仓摘要
        
        Args:
            current_price: 当前价格
            
        Returns:
            持仓摘要信息
        """
        if self.position is None:
            return {
                "has_position": False,
                "symbol": None,
                "quantity": 0,
                "entry_price": 0,
                "current_price": 0,
                "profit": 0,
                "profit_rate": 0,
            }
        
        if current_price is None:
            current_price = self.position.entry_price
        
        return {
            "has_position": True,
            "symbol": self.position.symbol,
            "quantity": self.position.quantity,
            "entry_price": self.position.entry_price,
            "current_price": current_price,
            "profit": self.position.calculate_profit(current_price),
            "profit_rate": self.position.current_profit_rate,
        }
    
    def get_account_summary(self, current_price: float = None) -> dict:
        """
        获取账户摘要
        
        Args:
            current_price: 当前价格
            
        Returns:
            账户摘要信息
        """
        market_value = self.calculate_market_value(current_price) if current_price is not None else self.market_value
        
        return {
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "frozen_balance": self.frozen_balance,
            "available_balance": self.available_balance,
            "market_value": market_value,
            "total_assets": self.balance + market_value,
            "total_profit": self.total_profit,
            "total_commission": self.total_commission,
            "profit_rate": (self.balance + market_value - self.initial_balance) / self.initial_balance,
        }
    
    def reset(self) -> None:
        """重置账户"""
        self.balance = self.initial_balance
        self.frozen_balance = 0.0
        self.total_profit = 0.0
        self.total_commission = 0.0
        self.position = None
        self.trade_recorder.clear()
