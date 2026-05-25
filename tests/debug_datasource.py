"""
调试数据源 - 检查K线数据获取
"""
import sys
from pathlib import Path

# 添加项目路径（相对于tests目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from src.datasources import EastMoneyDataSource, SinaDataSource, TencentDataSource

print("=" * 70)
print("333交易系统 - 数据源调试")
print("=" * 70)

symbol = "588200"

print(f"\n[1/3] 测试东方财富数据源 ({symbol})...")
try:
    ds_em = EastMoneyDataSource(symbol)
    print("   ✅ 数据源初始化成功")
    
    klines_em = ds_em.fetch_klines(count=50)
    print(f"   📊 获取K线: {len(klines_em)} 条")
    
    quote_em = ds_em.get_realtime_quote()
    print(f"   💹 实时行情: {quote_em}")
    
except Exception as e:
    print(f"   ❌ 失败: {e}")

print(f"\n[2/3] 测试新浪财经数据源 ({symbol})...")
try:
    ds_sina = SinaDataSource(symbol)
    print("   ✅ 数据源初始化成功")
    
    klines_sina = ds_sina.fetch_klines(count=50)
    print(f"   📊 获取K线: {len(klines_sina)} 条")
    
except Exception as e:
    print(f"   ❌ 失败: {e}")

print(f"\n[3/3] 测试腾讯财经数据源 ({symbol})...")
try:
    ds_tencent = TencentDataSource(symbol)
    print("   ✅ 数据源初始化成功")
    
    klines_tencent = ds_tencent.fetch_klines(count=50)
    print(f"   📊 获取K线: {len(klines_tencent)} 条")
    
    quote_tencent = ds_tencent.get_realtime_quote()
    print(f"   💹 实时行情: {quote_tencent}")
    
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n" + "=" * 70)
print("调试完成")
print("=" * 70)
