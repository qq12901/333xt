"""
333 Trading System - Strategy Configuration
"""
from .settings import (
    SYSTEM_CONFIG,
    DATA_CONFIG,
    TRADING_CONFIG,
    API_CONFIG,
    NOTIFICATION_CONFIG,
)

SYMBOL = "588200"

STRATEGY_CONFIG = {
    "name": "333 Trend Following Strategy",
    "symbol": SYMBOL,
    "ma_period": 30,
    "timeframe": "30min",
    "profit_target_1": 0.01,
    "profit_target_2": 0.03,
}

POSITION_CONFIG = {
    "max_positions": 1,
    "position_size_type": "full",
    "allow_increasing": False,
}

RISK_CONFIG = {
    "max_daily_trades": 10,
    "max_drawdown_pct": 0.10,
    "stop_loss_enabled": True,
    "emergency_stop_enabled": True,
}

__all__ = [
    "SYSTEM_CONFIG",
    "DATA_CONFIG",
    "TRADING_CONFIG",
    "API_CONFIG",
    "NOTIFICATION_CONFIG",
    "STRATEGY_CONFIG",
    "POSITION_CONFIG",
    "RISK_CONFIG",
]
