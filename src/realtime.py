"""
333交易系统 - 实时行情模块

提供定时轮询、实时监控等功能
"""
import sys
from pathlib import Path
if __name__ != "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import threading
from datetime import datetime
from typing import Optional, Callable
from .datasources.base import DataSource
from .datasources.multi_source_manager import MultiDataSourceManager
from .models.kline import KlineData
from config.settings import DATA_CONFIG


class RealTimeDataManager:
    """实时行情管理器"""
    
    def __init__(self, symbol: str, data_source: Optional[DataSource] = None):
        """
        初始化实时行情管理器
        
        Args:
            symbol: 交易标的代码
            data_source: 数据源，默认使用多数据源管理器
        """
        self.symbol = symbol
        self.klines = KlineData()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.on_new_kline: Optional[Callable] = None
        
        # 使用指定的数据源或默认多数据源管理器
        if data_source:
            self.data_source = data_source
        else:
            # 使用多数据源管理器
            print("📊 正在初始化多数据源管理器...")
            self.data_source = MultiDataSourceManager(symbol)
            if self.data_source.is_available():
                print(f"✅ 使用数据源: {self.data_source.current_data_source_name}({symbol})")
                print(f"   (支持自动切换: 东方财富 > 新浪 > 腾讯)")
            else:
                raise Exception("所有数据源都不可用")
    
    def start(self, interval_seconds: int = 30):
        """
        启动实时数据监控
        
        Args:
            interval_seconds: 轮询间隔（秒），默认30秒
        """
        if self.running:
            print("⚠️ 实时数据监控已在运行中")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval_seconds,), daemon=True)
        self.thread.start()
        print(f"🚀 实时数据监控已启动，轮询间隔: {interval_seconds}秒")
    
    def stop(self):
        """
        停止实时数据监控
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⏹️ 实时数据监控已停止")
    
    def _monitor_loop(self, interval_seconds: int):
        """
        监控循环
        
        Args:
            interval_seconds: 轮询间隔
        """
        # 先初始化数据
        self._fetch_initial_data()
        
        while self.running:
            try:
                # 尝试获取最新K线
                new_klines = self.data_source.fetch_klines(count=1)
                
                if new_klines:
                    latest_kline = new_klines[-1]
                    
                    # 检查是否有新K线
                    if self.klines.latest is None or latest_kline.timestamp > self.klines.latest.timestamp:
                        self.klines.add(latest_kline)
                        print(f"📊 新K线数据: {latest_kline.datetime_str}, 收盘价: {latest_kline.close}")
                        
                        # 触发回调
                        if self.on_new_kline:
                            self.on_new_kline(latest_kline)
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                print(f"❌ 监控循环出错: {e}")
                time.sleep(interval_seconds)
    
    def _fetch_initial_data(self, count: int = 100):
        """
        获取初始数据
        
        Args:
            count: K线数量
        """
        print(f"📥 正在获取初始K线数据 ({count}根)...")
        klines = self.data_source.fetch_klines(count)
        
        if klines:
            self.klines.add_batch(klines)
            print(f"✅ 已加载 {len(klines)} 根K线数据")
            if klines:
                print(f"   最新: {klines[-1].datetime_str}, 收盘价: {klines[-1].close}")
        else:
            print("⚠️ 未获取到K线数据")
    
    def get_current_price(self) -> Optional[float]:
        """
        获取当前价格
        
        Returns:
            当前价格
        """
        quote = self.data_source.get_realtime_quote()
        if quote:
            return quote.get('price')
        return None
    
    def get_klines(self) -> KlineData:
        """
        获取当前K线数据
        
        Returns:
            K线数据集合
        """
        return self.klines


def create_realtime_manager(symbol: str) -> RealTimeDataManager:
    """
    便捷函数：创建实时数据管理器
    
    Args:
        symbol: 交易标的代码
        
    Returns:
        实时数据管理器实例
    """
    return RealTimeDataManager(symbol)
