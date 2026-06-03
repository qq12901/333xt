#!/usr/bin/env python
"""
333交易系统 - 今日交易复盘
"""
import sys
from datetime import datetime
from pathlib import Path

project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from src.main import TradingSystem
from src.models.kline import KlineData


def main():
    print("=" * 80)
    print("📊 333交易系统 - 今日交易复盘")
    print("=" * 80)
    
    try:
        # 初始化系统
        system = TradingSystem(symbol="588200", initial_balance=100000.0)
        system.initialize(kline_count=2000)
        
        klines = system.klines.klines
        strategy = system.strategy
        
        # 找到今天的K线
        today_klines = []
        today_date = datetime.now().date()
        
        for kline in klines:
            kline_date = datetime.fromtimestamp(kline.timestamp / 1000).date()
            if kline_date == today_date:
                today_klines.append(kline)
        
        if not today_klines:
            print("❌ 未找到今天的K线数据")
            return
        
        print(f"\n📅 日期: {today_date.strftime('%Y年%m月%d日')}")
        print(f"📊 今日K线数量: {len(today_klines)} 根")
        
        # 计算今日统计
        opens = [k.open for k in today_klines]
        highs = [k.high for k in today_klines]
        lows = [k.low for k in today_klines]
        closes = [k.close for k in today_klines]
        volumes = [k.volume for k in today_klines]
        
        print(f"\n📈 今日行情概览:")
        print(f"   开盘价: {opens[0]:.3f}")
        print(f"   收盘价: {closes[-1]:.3f}")
        print(f"   最高价: {max(highs):.3f}")
        print(f"   最低价: {min(lows):.3f}")
        print(f"   振幅: {(max(highs) - min(lows))/opens[0]*100:.2f}%")
        print(f"   涨跌: {closes[-1] - opens[0]:.3f} ({(closes[-1] - opens[0])/opens[0]*100:.2f}%)")
        print(f"   总成交量: {sum(volumes):,}")
        
        # 分析MA30穿越
        print("\n" + "=" * 80)
        print("🎯 MA30穿越分析")
        print("-" * 80)
        
        # 重置策略并重新计算
        strategy.reset()
        
        # 先用历史数据初始化
        historical_klines_obj = KlineData()
        historical_klines_obj.add_batch(klines[:-len(today_klines)])
        
        # 计算MA30
        closes_all = [k.close for k in klines]
        ma_values = []
        for i in range(29, len(closes_all)):
            ma = sum(closes_all[i-29:i+1]) / 30
            ma_values.append(ma)
        
        # 找到今天对应的MA值
        today_start_idx = len(closes_all) - len(today_klines) - 29
        
        print(f"\n今日K线详情:")
        print("-" * 80)
        print(f"{'时间':<19} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8} {'MA30':>10} {'穿越':>8}")
        print("-" * 80)
        
        prev_price = None
        prev_ma = None
        cross_detected = False
        
        for i, kline in enumerate(today_klines):
            ma_idx = today_start_idx + i
            current_ma = ma_values[ma_idx] if ma_idx < len(ma_values) else None
            
            cross = ""
            if prev_price is not None and prev_ma is not None and current_ma is not None:
                threshold = current_ma * 0.005
                if prev_price <= prev_ma and kline.close > current_ma + threshold:
                    cross = "↑ 买入"
                    cross_detected = True
                elif prev_price >= prev_ma and kline.close < current_ma - threshold:
                    cross = "↓ 卖出"
            
            print(f"{kline.datetime_str:<19} {kline.open:>8.3f} {kline.high:>8.3f} {kline.low:>8.3f} {kline.close:>8.3f} {current_ma:>10.4f} {cross:>8}")
            
            prev_price = kline.close
            prev_ma = current_ma
        
        # 模拟交易回测
        print("\n" + "=" * 80)
        print("💹 今日交易模拟回测")
        print("-" * 80)
        
        # 重置系统
        system.strategy.reset()
        system.account.reset()
        system.klines.clear()
        
        # 添加历史数据
        system.klines.add_batch(klines[:-len(today_klines)])
        
        # 初始化策略MA
        system.strategy.update_indicators(system.klines)
        
        # 设置prev值
        last_historical = klines[-len(today_klines) - 1]
        system.strategy._prev_price = last_historical.close
        system.strategy._prev_ma = system.strategy.current_ma
        
        initial_balance = system.account.balance
        trades = []
        
        for i, kline in enumerate(today_klines):
            system.klines.add(kline)
            
            current_ma, _ = system.strategy.update_indicators(system.klines)
            system.account.update_position_profit(kline.close)
            
            signal = system.strategy.generate_signal(system.klines, system.account.position)
            
            if signal:
                if signal.signal_type.value == "BUY":
                    quantity = system._calculate_quantity(kline.close)
                    if quantity > 0 and system.account.can_buy(kline.close, quantity):
                        trade = system.account.execute_buy(
                            symbol=system.symbol,
                            price=kline.close,
                            quantity=quantity,
                            timestamp=kline.timestamp
                        )
                        if trade:
                            trades.append(trade)
                            print(f"✅ {kline.datetime_str} 买入 {quantity}股 @ {kline.close:.3f}")
                
                elif signal.signal_type.value == "SELL":
                    if system.account.position and system.account.position.quantity > 0:
                        trade = system.account.execute_sell(
                            symbol=system.symbol,
                            price=kline.close,
                            quantity=system.account.position.quantity,
                            timestamp=kline.timestamp,
                            notes="分手卖出"
                        )
                        if trade:
                            trades.append(trade)
                            print(f"❌ {kline.datetime_str} 卖出 {trade.quantity}股 @ {kline.close:.3f}")
        
        # 输出账户结果
        account_summary = system.account.get_account_summary()
        final_price = today_klines[-1].close
        
        print(f"\n📊 账户结果:")
        print(f"   初始资金: {initial_balance:.2f}")
        print(f"   当前资金: {account_summary['balance']:.2f}")
        print(f"   总盈利: {account_summary['total_profit']:.2f}")
        print(f"   收益率: {account_summary['profit_rate']*100:.2f}%")
        
        if system.account.position and not system.account.position.is_empty:
            pos = system.account.position
            unrealized_profit = (final_price - pos.entry_price) * pos.quantity
            print(f"\n📦 当前持仓:")
            print(f"   数量: {pos.quantity}股")
            print(f"   成本价: {pos.entry_price:.3f}")
            print(f"   当前价: {final_price:.3f}")
            print(f"   浮动盈亏: {unrealized_profit:.2f} ({(final_price - pos.entry_price)/pos.entry_price*100:.2f}%)")
        
        if trades:
            print(f"\n📜 今日交易记录 ({len(trades)}笔):")
            for i, trade in enumerate(trades):
                print(f"   {i+1}. {trade.datetime_str} {trade.action_name} {trade.quantity}股 @ {trade.price:.3f}")
        
        # 总结
        print("\n" + "=" * 80)
        print("📝 今日复盘总结")
        print("=" * 80)
        
        if cross_detected:
            print("✅ MA30穿越信号已触发")
            if trades:
                print("✅ 交易已执行")
            else:
                print("⚠️ 未执行交易（可能已有持仓）")
        else:
            print("📊 今日无MA30穿越信号")
        
        print(f"\n💡 下一交易日关注:")
        print(f"   - 当前MA30: {ma_values[-1]:.4f}")
        print(f"   - 当前价格: {closes[-1]:.3f}")
        print(f"   - 趋势方向: {'向上' if closes[-1] > ma_values[-1] else '向下'}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ 复盘失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
