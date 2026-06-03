#!/usr/bin/env python
"""检查今天的K线数据和策略触发情况"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from src.main import TradingSystem

print("=" * 80)
print("检查今天的K线数据和MA30穿越")
print("=" * 80)

try:
    # 初始化系统
    system = TradingSystem(symbol="588200", initial_balance=100000.0)
    system.initialize(kline_count=2000)
    
    klines = system.klines
    strategy = system.strategy
    
    print(f"\n✅ 系统初始化完成")
    print(f"📊 获取到 {len(klines.klines)} 根K线")
    print(f"📈 当前MA30: {strategy.current_ma}")
    
    # 打印最近的K线数据（今天的）
    print("\n" + "=" * 80)
    print("最近20根K线数据：")
    print("-" * 80)
    
    for i, kline in enumerate(reversed(klines.klines[-20:])):
        is_today = datetime.fromtimestamp(kline.timestamp / 1000).date() == datetime.now().date()
        today_mark = " [今日]" if is_today else ""
        print(f"{19 - i}. {kline.datetime_str} O:{kline.open} H:{kline.high} L:{kline.low} C:{kline.close}{today_mark}")
    
    # 检查穿越情况
    print("\n" + "=" * 80)
    print("检查MA30穿越：")
    print("-" * 80)
    
    strategy._prev_price = None
    strategy._prev_ma = None
    
    # 重新计算MA30并检查穿越
    closes = []
    for i, kline in enumerate(klines.klines):
        closes.append(kline.close)
        
        if i >= 29:  # 从第30根K线开始计算MA30
            current_ma = sum(closes[-30:]) / 30
            current_price = kline.close
            
            if strategy._prev_price is not None and strategy._prev_ma is not None:
                # 检查穿越
                threshold = current_ma * 0.005  # 0.5%
                
                if strategy._prev_price <= strategy._prev_ma and current_price > current_ma + threshold:
                    print(f"✅ 向上穿越! {kline.datetime_str}")
                    print(f"   前一价格: {strategy._prev_price}, 前一MA: {strategy._prev_ma}")
                    print(f"   当前价格: {current_price}, 当前MA: {current_ma}")
                    print(f"   穿越幅度: {(current_price - current_ma)/current_ma*100:.3f}%")
                    
                elif strategy._prev_price >= strategy._prev_ma and current_price < current_ma - threshold:
                    print(f"❌ 向下穿越! {kline.datetime_str}")
                    print(f"   前一价格: {strategy._prev_price}, 前一MA: {strategy._prev_ma}")
                    print(f"   当前价格: {current_price}, 当前MA: {current_ma}")
                    print(f"   穿越幅度: {(current_price - current_ma)/current_ma*100:.3f}%")
            
            strategy._prev_price = current_price
            strategy._prev_ma = current_ma
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
