#!/usr/bin/env python
"""用今天的K线数据进行正确的回测 - 已修复"""
import sys
from pathlib import Path
from datetime import datetime

project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from src.main import TradingSystem
from src.models.kline import KlineData, Kline

print("=" * 80)
print("333交易系统 - 用今天的K线数据进行回测 (已修复)")
print("=" * 80)

try:
    # 初始化系统
    system = TradingSystem(symbol="588200", initial_balance=100000.0)
    system.initialize(kline_count=2000)
    
    # 获取历史K线数据
    klines = system.klines.klines
    
    # 找到今天的K线
    today_start_idx = None
    for i, kline in enumerate(klines):
        kline_date = datetime.fromtimestamp(kline.timestamp / 1000).date()
        if kline_date == datetime.now().date():
            today_start_idx = i
            break
    
    if today_start_idx is None:
        print("❌ 没有找到今天的K线数据")
        sys.exit(1)
    
    # 准备数据
    historical_klines = klines[:today_start_idx]
    test_klines = klines[today_start_idx - 30:]  # 带前30根来计算MA
    
    # 重置策略和账户
    strategy = system.strategy
    account = system.account
    
    strategy.reset()
    account.reset()
    
    # 创建临时K线数据，初始化MA
    temp_klines = KlineData()
    temp_klines.add_batch(test_klines[:30])
    
    # 初始化策略MA
    strategy.update_indicators(temp_klines)
    
    # 关键！设置prev_price和prev_ma
    strategy._prev_price = temp_klines.klines[-1].close
    strategy._prev_ma = strategy.current_ma
    
    print(f"\n✅ 系统初始化完成")
    print(f"📊 历史K线: {len(historical_klines)} 根")
    print(f"📊 回测K线: {len(test_klines) - 30} 根")
    print(f"📈 初始MA: {strategy.current_ma:.4f}")
    print(f"💰 初始资金: {account.initial_balance:.2f}")
    
    print("\n" + "=" * 80)
    print("开始回测:")
    print("-" * 80)
    
    for i, kline in enumerate(test_klines[30:]):
        temp_klines.add(kline)
        
        # 更新指标
        current_ma, _ = strategy.update_indicators(temp_klines)
        account.update_position_profit(kline.close)
        
        # 生成信号
        signal = strategy.generate_signal(
            klines=temp_klines,
            position=account.position
        )
        
        is_today = datetime.fromtimestamp(kline.timestamp / 1000).date() == datetime.now().date()
        today_mark = " [今日]" if is_today else ""
        
        trade_result = None
        if signal:
            print(f"{i+1}. {kline.datetime_str} O:{kline.open} C:{kline.close} MA:{current_ma:.4f} {today_mark}")
            print(f"   📊 信号: {signal.signal_type.value}")
            
            if signal.signal_type.value == "BUY":
                quantity = system._calculate_quantity(kline.close)
                if quantity > 0 and account.can_buy(kline.close, quantity):
                    trade = account.execute_buy(
                        symbol=system.symbol,
                        price=kline.close,
                        quantity=quantity,
                        timestamp=kline.timestamp
                    )
                    if trade:
                        trade_result = trade
                        print(f"   ✅ 买入 {quantity} 股 @ {kline.close:.3f}")
                        
            elif signal.signal_type.value == "SELL":
                if account.position and account.position.quantity > 0:
                    trade = account.execute_sell(
                        symbol=system.symbol,
                        price=kline.close,
                        quantity=account.position.quantity,
                        timestamp=kline.timestamp,
                        notes="分手卖出"
                    )
                    if trade:
                        trade_result = trade
                        print(f"   ✅ 卖出 {trade.quantity} 股 @ {kline.close:.3f}")
        
        if trade_result is None and signal is None and i % 3 == 0:
            print(f"{i+1}. {kline.datetime_str} O:{kline.open} C:{kline.close} MA:{current_ma:.4f} {today_mark}")
    
    print("\n" + "=" * 80)
    print("回测结束:")
    print("-" * 80)
    
    # 打印账户信息
    account_summary = account.get_account_summary()
    print(f"🏦 初始资金: {account_summary['initial_balance']:.2f}")
    print(f"💰 当前资金: {account_summary['balance']:.2f}")
    print(f"📈 总盈利: {account_summary['total_profit']:.2f}")
    print(f"📊 收益率: {account_summary['profit_rate']*100:.2f}%")
    
    # 打印持仓
    if account.position and not account.position.is_empty:
        pos = account.position
        print(f"\n📦 当前持仓:")
        print(f"   数量: {pos.quantity} 股")
        print(f"   成本价: {pos.entry_price:.3f}")
        current_price = klines[-1].close
        print(f"   当前价: {current_price:.3f}")
        profit = (current_price - pos.entry_price) * pos.quantity
        print(f"   浮动盈利: {profit:.2f}")
        print(f"   浮动盈利率: {(current_price - pos.entry_price)/pos.entry_price*100:.2f}%")
    
    # 打印交易记录
    trades = account.trade_recorder.get_records()
    if trades:
        print(f"\n📜 交易记录 (共 {len(trades)} 笔):")
        for i, trade in enumerate(trades):
            print(f"   {i+1}. {trade.datetime_str} {trade.action_name} {trade.quantity}股 @ {trade.price:.3f} 金额:{trade.amount:.2f}")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
