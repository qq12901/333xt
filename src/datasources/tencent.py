"""
333交易系统 - 腾讯财经数据源

使用腾讯财经免费API获取ETF实时行情和K线数据
支持30分钟K线、实时报价等
"""
import time
import json
import requests
from datetime import datetime, timedelta
from typing import List, Optional
from .base import DataSource
from ..models.kline import Kline


class TencentDataSource(DataSource):
    """腾讯财经数据源"""
    
    def __init__(self, symbol: str):
        """
        初始化腾讯财经数据源
        
        Args:
            symbol: 交易标的代码，如588200
        """
        super().__init__(symbol)
        self.base_url = "https://qt.gtimg.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _convert_symbol(self, symbol: str) -> str:
        """
        转换标的代码格式
        
        腾讯格式：
        - 沪市基金：sh588200
        - 深市基金：sz159995
        
        Args:
            symbol: 原始代码
            
        Returns:
            腾讯格式代码
        """
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
            
            # 腾讯财经API - 获取K线数据
            # 使用新浪财经API作为替代方案（腾讯财经K线API经常变化）
            url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': code,
                'scale': '30',  # 30分钟
                'ma': 'no',
                'datalen': str(count * 2)  # 多取一些以便筛选
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析数据
            data_text = response.text
            if data_text.startswith('null'):
                return []
            
            klines_data = json.loads(data_text)
            
            klines = []
            for item in klines_data:
                try:
                    date_str = item.get('day', '')
                    open_price = float(item.get('open', 0))
                    close_price = float(item.get('close', 0))
                    low_price = float(item.get('low', 0))
                    high_price = float(item.get('high', 0))
                    volume = int(float(item.get('volume', 0)))
                    
                    # 解析日期时间
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
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
                except Exception:
                    continue
            
            # 取最近count根
            klines = klines[-count:]
            
            self.update_cache(klines)
            return klines
            
        except Exception as e:
            print(f"获取新浪财经K线数据失败: {e}")
            # 尝试备用方案
            return self._fetch_klines_backup(count)
    
    def _fetch_klines_backup(self, count: int = 100) -> List[Kline]:
        """
        获取K线数据的备用方案（使用腾讯财经另一个API）
        
        Args:
            count: 获取数量
            
        Returns:
            K线数据列表
        """
        try:
            code = self._convert_symbol(self.symbol)
            
            # 腾讯财经API - 获取K线数据（备用方案）
            # 最多获取1024根，但我们按count来限制
            max_data = min(count * 2, 1024)
            url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            params = {
                '_var': 'kline_day',
                'param': f'{code},m30,{max_data}',
                'r': str(int(time.time()))
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data_text = response.text
            
            # 解析数据
            if 'kline_day' in data_text:
                json_str = data_text.split('kline_day=')[1]
                data = json.loads(json_str)
                
                if data.get('code') == 0:
                    klines_data = data.get('data', {}).get(code, {}).get('m30', [])
                    
                    klines = []
                    for item in klines_data:
                        try:
                            date_str = item[0]
                            open_price = float(item[1])
                            close_price = float(item[2])
                            high_price = float(item[3])
                            low_price = float(item[4])
                            volume = int(float(item[5])) if len(item) > 5 else 0
                            
                            # 解析日期时间
                            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
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
                        except Exception:
                            continue
                    
                    # 取最近count根
                    klines = klines[-count:]
                    
                    self.update_cache(klines)
                    return klines
            
            return []
            
        except Exception as e:
            print(f"获取腾讯财经K线数据（备用方案）失败: {e}")
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
            print(f"获取腾讯财经历史K线数据失败: {e}")
            return []
    
    def get_realtime_quote(self) -> Optional[dict]:
        """
        获取实时行情
        
        Returns:
            实时行情数据
        """
        try:
            code = self._convert_symbol(self.symbol)
            
            # 腾讯财经API - 获取实时报价
            url = f"{self.base_url}/q={code}"
            
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            # 解析数据
            data_text = response.text
            if 'v_pv_none_match' in data_text:
                return None
            
            # 解析格式: v_sh588200="1~588200~科创50ETF~..."
            parts = data_text.split('=')[1].strip('"').split('~')
            
            if len(parts) < 40:
                return None
            
            # 字段说明（部分）：
            # 0: 市场
            # 1: 代码
            # 2: 名称
            # 3: 最新价
            # 4: 昨收
            # 5: 今开
            # 6: 成交量
            # 7: 外盘
            # 8: 内盘
            # 9: 买一
            # 10: 买一量
            # 11: 买二
            # 12: 买二量
            # 13: 买三
            # 14: 买三量
            # 15: 买四
            # 16: 买四量
            # 17: 买五
            # 18: 买五量
            # 19: 卖一
            # 20: 卖一量
            # 21: 卖二
            # 22: 卖二量
            # 23: 卖三
            # 24: 卖三量
            # 25: 卖四
            # 26: 卖四量
            # 27: 卖五
            # 28: 卖五量
            # 29: 最新价(小数)
            # 30: 涨跌额
            # 31: 涨跌幅
            # 32: 最高
            # 33: 最低
            # 34: 成交额
            # 35: 换手率
            # 36: 市盈率
            # 37: 振幅
            # 38: 流通市值
            # 39: 总市值
            
            current_price = float(parts[3]) if parts[3] else 0.0
            open_price = float(parts[5]) if parts[5] else 0.0
            high_price = float(parts[32]) if parts[32] else 0.0
            low_price = float(parts[33]) if parts[33] else 0.0
            close_price = float(parts[4]) if parts[4] else 0.0
            volume = int(float(parts[6])) if parts[6] else 0
            change_pct = float(parts[31]) if parts[31] else 0.0
            
            return {
                "symbol": self.symbol,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "price": round(current_price, 3),
                "open": round(open_price, 3),
                "high": round(high_price, 3),
                "low": round(low_price, 3),
                "close": round(close_price, 3),
                "volume": volume,
                "change_pct": round(change_pct, 2)
            }
            
        except Exception as e:
            print(f"获取腾讯财经实时行情失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        检查腾讯财经数据源是否可用
        
        Returns:
            是否可用
        """
        try:
            # 测试连接
            quote = self.get_realtime_quote()
            return quote is not None
        except Exception:
            return False
