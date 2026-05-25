"""
333交易系统 - 真实数据使用示例
"""
import sys
from pathlib import Path

# 添加项目路径（相对于examples目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

print("=" * 70)
print("333交易系统 - 真实数据使用示例")
print("=" * 70)

try:
    from src.datasources import (
        EastMoneyDataSource,
        SinaDataSource,
        TencentDataSource,
        MultiDataSourceManager
    )
    from src.main import create_system
    
    symbol = "588200"
    
    print(f"\n[1/4] 使用多数据源管理器...")
    manager = MultiDataSourceManager(symbol)
    print(f"   ✅ 使用数据源: {manager.current_data_source_name}")
    
    print(f"\n[2/4] 获取K线数据...")
    klines = manager.fetch_klines(count=50)
    print(f"   ✅ 获取 {len(klines)} 根K线")
    if klines:
        print(f"   最新K线: {klines[-1].datetime_str}, 收盘价: {klines[-1].close}")
    
    print(f"\n[3/4] 获取实时行情...")
    quote = manager.get_realtime_quote()
    print(f"   ✅ 实时行情获取成功")
    if quote:
        print(f"   当前价格: {quote['price']}, 涨跌: {quote['change_pct']}%")
    
    print(f"\n[4/4] 创建交易系统...")
    system = create_system(symbol="588200", initial_balance=100000.0)
    print(f"   ✅ 交易系统创建成功")
    print(f"   K线数量: {system.klines.count}")
    
    print("\n" + "=" * 70)
    print("✅ 示例运行完成")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 示例运行失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
