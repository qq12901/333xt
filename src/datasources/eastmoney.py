"""
333交易系统 - 东方财富数据源（已修复价格单位）

使用东方财富免费API获取ETF实时行情和K线数据
支持30分钟K线、实时报价等
"""
import time
import json
import requests
from datetime import datetime, timedelta
from typing import List, Optional
from .base import DataSource
from ..models.kline import Kline


class EastMoneyDataSource(DataSource):
    """东方财富数据源"""
    
    def __init__(self, symbol: str):
        """
        初始化东方财富数据源
        
        Args:
            symbol: 交易标的代码，如588200
        """
        super().__init__(symbol)
        self.base_url = "https://push2.eastmoney.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _convert_symbol(self, symbol: str) -> str:
        """
        转换标的代码格式
        
        东方财富格式：
        - 沪市基金：1.588200
        - 深市基金：0.588200
        
        Args:
            symbol: 原始代码
            
        Returns:
            东方财富格式代码
        """
        if symbol.startswith('5'):
            return f"1.{symbol}"
        elif symbol.startswith('1') or symbol.startswith('15'):
            return f"0.{symbol}"
        else:
            return f"1.{symbol}"
    
    def fetch_klines(self, count: int = 100) -> List[Kline]:
        """
        获取30分钟K线数据
        
        Args:
            count: 获取数量，默认100根
            
        Returns:
            K线数据列表
        """
        try:
            code = self._convert_symbol(self.symbol)
            
            # 东方财富API - 获取K线数据
            end_date = datetime.now().strftime('%Y%m%d')
            begin_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            url = f"{self.base_url}/api/qt/stock/kline/get"
            params = {
                'secid': code,
                'klt': '109',  # 109=30分钟
                'fqt': '1',    # 前复权
                'beg': begin_date,
                'end': end_date,
                '_': str(int(time.time() * 1000))
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('klines'):
                klines_data = data['data']['klines']
                
                # 取最近count根
                klines_data = klines_data[-count:]
                
                klines = []
                for kline_str in klines_data:
                    kline_parts = kline_str.split(',')
                    if len(kline_parts) >= 6:
                        date_str = kline_parts[0]
                        # 东方财富价格单位是分，需要除以1000
                        open_price = float(kline_parts[1]) / 1000
                        close_price = float(kline_parts[2]) / 1000
                        low_price = float(kline_parts[3]) / 1000
                        high_price = float(kline_parts[4]) / 1000
                        volume = int(float(kline_parts[5]))
                        
                        # 解析日期时间
                        try:
                            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                        except ValueError:
                            try:
                                dt = datetime.strptime(date_str, '%Y-%m-%d')
                            except ValueError:
                                continue
                        
                        timestamp = int(dt.timestamp() * 1000)
                        
                        kline = Kline(
                            symbol=self.symbol,
                            timestamp=timestamp,
                            open=round(open_price, 3),
                            high=round(high_price, 3),
                            low=round(low_price, 3),
                            close=round(close_price, 3),
                            volume=volume
                        )
                        
                        if self.validate_kline(kline):
                            klines.append(kline)
                
                self.update_cache(klines)
                return klines
            
            return []
            
        except Exception as e:
            print(f"获取东方财富K线数据失败: {e}")
            return []
    
    def fetch_history(self, start_time: int, end_time: int) -> List[Kline]:
        """
        获取历史K线数据
        
        Args:
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            
        Returns:
            K线数据列表
        """
        try:
            start_dt = datetime.fromtimestamp(start_time / 1000)
            end_dt = datetime.fromtimestamp(end_time / 1000)
            
            # 计算需要多少根K线
            total_minutes = int((end_dt - start_dt).total_seconds() / 60)
            count = total_minutes // 30 + 1
            
            # 调用fetch_klines获取数据
            all_klines = self.fetch_klines(count * 2)
            
            # 筛选时间范围
            filtered_klines = []
            for kline in all_klines:
                if start_time <= kline.timestamp <= end_time:
                    filtered_klines.append(kline)
            
            return filtered_klines
            
        except Exception as e:
            print(f"获取东方财富历史K线数据失败: {e}")
            return []
    
    def get_realtime_quote(self) -> Optional[dict]:
        """
        获取实时行情
        
        Returns:
            实时行情数据
        """
        try:
            code = self._convert_symbol(self.symbol)
            
            # 东方财富API - 获取实时报价
            url = f"{self.base_url}/api/qt/stock/get"
            params = {
                'secid': code,
                'fields': 'f43,f44,f45,f46,f47,f60,f111,f107,f48',
                '_': str(int(time.time() * 1000))
            }
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                quote_data = data['data']
                
                # 字段说明：
                # f43: 最新价
                # f44: 最高
                # f45: 最低
                # f46: 今开
                # f47: 成交量
                # f60: 昨收
                # 价格单位是分，需要除以1000
                
                current_price = float(quote_data.get('f43', 0)) / 1000
                open_price = float(quote_data.get('f46', 0)) / 1000
                high_price = float(quote_data.get('f44', 0)) / 1000
                low_price = float(quote_data.get('f45', 0)) / 1000
                close_price = float(quote_data.get('f60', 0)) / 1000  # 昨收
                volume = int(float(quote_data.get('f47', 0)))
                
                # 计算涨跌幅
                if close_price > 0:
                    change_pct = round((current_price - close_price) / close_price * 100, 2)
                else:
                    change_pct = 0
                
                return {
                    "symbol": self.symbol,
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "price": round(current_price, 3),
                    "open": round(open_price, 3),
                    "high": round(high_price, 3),
                    "low": round(low_price, 3),
                    "close": round(close_price, 3),
                    "volume": volume,
                    "change_pct": change_pct
                }
            
            return None
            
        except Exception as e:
            print(f"获取东方财富实时行情失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        检查东方财富数据源是否可用
        
        Returns:
            是否可用
        """
        try:
            # 测试连接
            quote = self.get_realtime_quote()
            return quote is not None
        except Exception:
            return False
