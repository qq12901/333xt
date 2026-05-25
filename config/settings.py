"""
System-wide configuration settings for 333 Trading System
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATABASE_PATH = DATA_DIR / "trading_system.db"

SYSTEM_CONFIG = {
    "system_name": "333 Trading System",
    "version": "1.0.0",
    "author": "333 Trading Team",
    "log_level": "INFO",
    "log_rotation": "daily",
    "log_retention_days": 30,
}

DATA_CONFIG = {
    "data_dir": str(DATA_DIR),
    "refresh_interval_seconds": 30,
    "cache_enabled": True,
    "cache_ttl_seconds": 60,
}

TRADING_CONFIG = {
    "trading_enabled": False,
    "simulated_trading": True,
    "max_position_size": 10000,
    "min_trade_amount": 100,
    "commission_rate": 0.0003,
    "slippage": 0.001,
}

API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "enable_websocket": True,
}

NOTIFICATION_CONFIG = {
    "console_enabled": True,
    "file_enabled": True,
    "websocket_enabled": False,
    "email_enabled": False,
}
