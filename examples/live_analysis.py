"""
333交易系统 - 实盘分析示例
588200 科创芯片ETF 实时分析
"""
import sys
from pathlib import Path

# 添加项目路径（相对于examples目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from src.datasources import TencentDataSource
from src.indicators.ma import MovingAverage
from datetime import datetime

print("\n" + "="*70)
print("333交易系统 - 588200 科创芯片ETF 实盘分析")
print("="*70)
print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

symbol = "588200"

# 获取数据
print("\n[1/5] 📊 获取实时行情...")
try:
    ds = TencentDataSource(symbol)
    quote = ds.get_realtime_quote()
    
    if quote:
        print(f"   ✅ 获取成功!")
        print(f"\n   📈 实时行情数据:")
        print(f"      最新价格: {quote['price']:.3f}")
        print(f"      今开: {quote['open']:.3f}")
        print(f"      最高: {quote['high']:.3f}")
        print(f"      最低: {quote['low']:.3f}")
        print(f"      成交量: {quote['volume']:,} 股")
        print(f"      昨收: {quote['close']:.3f}")
        print(f"      涨跌: {quote['change_pct']:+.2f}%")
    else:
        print("   ❌ 无法获取实时行情")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ 获取失败: {e}")
    sys.exit(1)

# 获取K线数据
print("\n[2/5] 📉 获取30分钟K线数据...")
try:
    klines = ds.fetch_klines(count=50)
    print(f"   ✅ 获取 {len(klines)} 根K线")
except Exception as e:
    print(f"   ❌ 获取失败: {e}")
    sys.exit(1)

# 计算MA30
print("\n[3/5] 📐 计算MA30移动平均线...")
if klines:
    closes = [k.close for k in klines]
    ma_engine = MovingAverage(period=30)
    ma30_values = ma_engine.calculate(closes)
    
    if ma30_values:
        latest_ma30 = ma30_values[-1]
        print(f"   ✅ MA30: {latest_ma30:.3f}")
    else:
        print("   ❌ MA30计算失败")
        sys.exit(1)
else:
    print("   ❌ 无K线数据")
    sys.exit(1)

# 趋势分析
print("\n[4/5] 📊 趋势分析...")
current_price = quote['price']
price_vs_ma30_pct = (current_price / latest_ma30 - 1) * 100

if current_price > latest_ma30:
    trend = "📈 均线多头排列"
else:
    trend = "📉 均线空头排列"

print(f"   趋势: {trend}")
print(f"   价格偏离MA30: {price_vs_ma30_pct:+.2f}%")

# 策略信号判断
print("\n[5/5] 🎯 333策略信号...")
if klines and len(klines) >= 2:
    latest_kline = klines[-1]
    prev_kline = klines[-2]
    
    if prev_kline.close < latest_ma30 and latest_kline.close > latest_ma30:
        signal = "✅ 牵手买入信号!"
        action = "考虑买入"
    elif prev_kline.close > latest_ma30 and latest_kline.close < latest_ma30:
        signal = "🔴 分手卖出信号!"
        action = "考虑卖出"
    else:
        signal = "⚪ 持仓观望" if current_price > latest_ma30 else "⚪ 空仓观望"
        action = "持有或观望" if current_price > latest_ma30 else "保持空仓"
    
    print(f"   {signal}")
    print(f"   建议: {action}")

print("\n" + "="*70)
print("✅ 实盘分析完成")
print("="*70)
