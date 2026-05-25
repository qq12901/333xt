"""
333交易系统 - 新浪财经数据源

使用新浪财经免费API获取ETF实时行情和K线数据
支持30分钟K线、实时报价等
"""
import time
import re
import requests
from datetime import datetime
from typing import List, Optional
from .base import DataSource
from ..models.kline import Kline


class SinaDataSource(DataSource):
    """新浪财经数据源"""
    
    def __init__(self, symbol: str):
        """
        初始化新浪财经数据源
        
        Args:
            symbol: 交易标的代码，如588200
        """
        super().__init__(symbol)
        self.base_url = "http://hq.sinajs.cn"
        self.klines_base_url = "https://finance.sina.com.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _convert_symbol(self, symbol: str) -> str:
        """
        转换标的代码格式
        
        新浪格式：
        - 沪市：sh588200
        - 深市：sz159995
        
        Args:
            symbol: 原始代码
            
        Returns:
            新浪格式代码
        """
        symbol = str(symbol)
        if symbol.startswith('5'):
            return f"sh{symbol}"
        elif symbol.startswith('1') or symbol.startswith('15'):
            return f"sz{symbol}"
        else:
            return f"sh{symbol}"
    
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
            sina_code = code.replace('sh', '').replace('sz', '')  # 去掉前缀
            market = 1 if code.startswith('sh') else 0  # 1=沪市, 0=深市
            
            klines = []
            
            # 尝试使用新浪股票K线API
            # 新浪K线API地址示例: https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData
            url = "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': f"{market}{sina_code}",
                'scale': '30',  # 30分钟
                'ma': 'no',
                'datalen': str(count * 2)  # 多取一些，后面筛选
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and isinstance(data, list):
                for kline_data in data[-count:]:  # 取最近count根
                    # 解析K线数据
                    # 数据格式通常包含: day, open, high, low, close, volume
                    try:
                        # 解析日期时间
                        day_str = kline_data.get('day', '')
                        if not day_str:
                            continue
                        
                        # 处理日期格式，新浪返回的格式通常是 "YYYY-MM-DD HH:MM:SS" 或 "YYYYMMDDHHMM"
                        if len(day_str) == 19:  # "YYYY-MM-DD HH:MM:SS"
                            dt = datetime.strptime(day_str, '%Y-%m-%d %H:%M:%S')
                        elif len(day_str) == 10:  # "YYYY-MM-DD"
                            dt = datetime.strptime(day_str, '%Y-%m-%d')
                        else:
                            # 其他格式尝试处理
                            continue
                        
                        open_price = float(kline_data.get('open', 0))
                        high_price = float(kline_data.get('high', 0))
                        low_price = float(kline_data.get('low', 0))
                        close_price = float(kline_data.get('close', 0))
                        volume = int(float(kline_data.get('volume', 0)))
                        
                        if open_price <= 0 or close_price <= 0:
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
                    except Exception as e:
                        continue
            
            # 如果没有获取到K线数据，尝试备用方案
            if not klines:
                realtime_quote = self.get_realtime_quote()
                if realtime_quote:
                    latest_kline = Kline(
                        symbol=self.symbol,
                        timestamp=realtime_quote['timestamp'],
                        open=realtime_quote['open'],
                        high=realtime_quote['high'],
                        low=realtime_quote['low'],
                        close=realtime_quote['price'],
                        volume=realtime_quote['volume']
                    )
                    klines.append(latest_kline)
            
            self.update_cache(klines)
            return klines
            
        except Exception as e:
            print(f"获取新浪财经K线数据失败: {e}")
            # 备用方案：尝试获取实时行情
            try:
                klines = []
                realtime_quote = self.get_realtime_quote()
                if realtime_quote:
                    latest_kline = Kline(
                        symbol=self.symbol,
                        timestamp=realtime_quote['timestamp'],
                        open=realtime_quote['open'],
                        high=realtime_quote['high'],
                        low=realtime_quote['low'],
                        close=realtime_quote['price'],
                        volume=realtime_quote['volume']
                    )
                    klines.append(latest_kline)
                self.update_cache(klines)
                return klines
            except Exception:
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
            # 新浪财经的历史K线API需要更复杂的实现
            # 这里先返回fetch_klines的结果，实际项目中可以根据需要完善
            
            all_klines = self.fetch_klines(200)
            
            # 筛选时间范围
            filtered_klines = []
            for kline in all_klines:
                if start_time <= kline.timestamp <= end_time:
                    filtered_klines.append(kline)
            
            return filtered_klines
            
        except Exception as e:
            print(f"获取新浪财经历史K线数据失败: {e}")
            return []
    
    def get_realtime_quote(self) -> Optional[dict]:
        """
        获取实时行情
        
        Returns:
            实时行情数据
        """
        try:
            code = self._convert_symbol(self.symbol)
            
            # 新浪实时行情API
            url = f"{self.base_url}/list={code}"
            
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            response.encoding = 'gbk'  # 新浪使用GBK编码
            
            # 解析返回的JavaScript数据
            # 格式: var hq_str_sh588200="名称,今开,昨收,最新,最高,最低,...";
            content = response.text
            
            # 使用正则表达式提取数据
            match = re.search(r'hq_str_[^=]+="([^"]+)"', content)
            if not match:
                return None
            
            data_str = match.group(1)
            data_parts = data_str.split(',')
            
            if len(data_parts) < 32:
                return None
            
            # 数据字段说明（股票格式）：
            # 0: 名称
            # 1: 今开
            # 2: 昨收
            # 3: 最新价
            # 4: 最高
            # 5: 最低
            # 6: 买一
            # 7: 卖一
            # 8: 成交量
            # 9: 成交额
            # ...
            
            name = data_parts[0]
            open_price = float(data_parts[1])
            pre_close = float(data_parts[2])
            current_price = float(data_parts[3])
            high_price = float(data_parts[4])
            low_price = float(data_parts[5])
            volume = int(float(data_parts[8]))
            
            # 计算涨跌幅
            if pre_close > 0:
                change_pct = round((current_price - pre_close) / pre_close * 100, 2)
            else:
                change_pct = 0
            
            return {
                "symbol": self.symbol,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "price": round(current_price, 3),
                "open": round(open_price, 3),
                "high": round(high_price, 3),
                "low": round(low_price, 3),
                "close": round(pre_close, 3),
                "volume": volume,
                "change_pct": change_pct,
                "name": name
            }
            
        except Exception as e:
            print(f"获取新浪财经实时行情失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        检查新浪财经数据源是否可用
        
        Returns:
            是否可用
        """
        try:
            # 测试连接
            quote = self.get_realtime_quote()
            return quote is not None
        except Exception:
            return False
