"""
Data sources package for 333 Trading System
"""
from .base import DataSource
from .eastmoney import EastMoneyDataSource
from .sina import SinaDataSource
from .tencent import TencentDataSource
from .multi_source_manager import MultiDataSourceManager

__all__ = [
    "DataSource",
    "EastMoneyDataSource",
    "SinaDataSource",
    "TencentDataSource",
    "MultiDataSourceManager",
]
