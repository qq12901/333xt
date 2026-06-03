#!/usr/bin/env python
"""调试策略的穿越检测"""
import sys
from pathlib import Path
from datetime import datetime

project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from src.main import TradingSystem
from src.models.kline import KlineData, Kline

print("=" * 80)
print("调试策略的穿越检测")
print("=" * 80)

try:
    # 初始化系统
    system = TradingSystem(symbol="588200", initial_balance=100000.0)
    system.initialize(kline_count=2000)
    
    # 获取K线数据
    klines = system.klines.klines
    
    # 手动遍历每一根K线，调试策略
    strategy = system.strategy
    
    # 重置策略
    strategy.reset()
    strategy._prev_price = None
    strategy._prev_ma = None
    
    print(f"\n📊 总K线: {len(klines)} 根")
    print(f"📈 策略初始状态:")
    print(f"   _prev_price: {strategy._prev_price}")
    print(f"   _prev_ma: {strategy._prev_ma}")
    
    # 找到今天的K线索引
    today_start_idx = None
    for i, kline in enumerate(klines):
        kline_date = datetime.fromtimestamp(kline.timestamp / 1000).date()
        if kline_date == datetime.now().date():
            today_start_idx = i
            break
    
    if today_start_idx is not None:
        print(f"\n📍 找到今天第一根K线索引: {today_start_idx}")
        
        # 先用历史数据初始化MA
        historical_klines = klines[:today_start_idx]
        test_klines = klines[today_start_idx - 30:]  # 带前30根来计算MA
        
        # 创建临时KlineData
        temp_klines = KlineData()
        temp_klines.add_batch(test_klines[:30])
        
        # 初始化策略MA
        strategy.update_indicators(temp_klines)
        
        # 手动设置第一个prev值
        strategy._prev_price = temp_klines.klines[-1].close
        strategy._prev_ma = strategy.current_ma
        
        print(f"\n✅ 策略初始化完成，准备遍历今天的K线...")
        print(f"   当前MA: {strategy.current_ma}")
        print(f"   _prev_price: {strategy._prev_price}")
        print(f"   _prev_ma: {strategy._prev_ma}")
        
        print(f"\n" + "=" * 80)
        print("开始遍历今天的K线:")
        print("-" * 80)
        
        for i, kline in enumerate(test_klines[30:]):
            temp_klines.add(kline)
            
            # 先保存之前的状态
            old_prev_price = strategy._prev_price
            old_prev_ma = strategy._prev_ma
            
            # 更新指标
            current_ma, prev_ma = strategy.update_indicators(temp_klines)
            
            # 手动检查穿越
            cross_result = None
            threshold = current_ma * 0.005 if current_ma else 0
            
            if old_prev_price is not None and old_prev_ma is not None and current_ma is not None:
                if old_prev_price <= old_prev_ma and kline.close > current_ma + threshold:
                    cross_result = "UP"
                elif old_prev_price >= old_prev_ma and kline.close < current_ma - threshold:
                    cross_result = "DOWN"
            
            print(f"{i+1}. {kline.datetime_str} O:{kline.open} C:{kline.close}")
            print(f"   MA_prev: {old_prev_ma:.4f}" if old_prev_ma is not None else "   MA_prev: None", f", MA_now: {current_ma:.4f}")
            print(f"   Price_prev: {old_prev_price:.4f}" if old_prev_price is not None else "   Price_prev: None", f", Price_now: {kline.close:.4f}")
            
            if cross_result:
                print(f"   ✅ 触发信号: {'向上穿越' if cross_result == 'UP' else '向下穿越'}!")
            
            # 生成信号
            signal = strategy.generate_signal(temp_klines, None)
            if signal:
                print(f"   📊 策略生成信号: {signal.signal_type.value}")
            
            print("")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
