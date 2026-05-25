"""
333交易系统 - 快速启动脚本
"""
import sys
from pathlib import Path

# 添加项目路径（相对于scripts目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

print("=" * 70)
print("333交易系统 - 科创芯片ETF (588200)")
print("=" * 70)
print("\n正在初始化系统...")
print("-" * 70)

try:
    from src.main import create_system
    
    print("\n[1/3] 创建交易系统实例...")
    system = create_system(symbol="588200", initial_balance=100000.0)
    print("   ✅ 系统初始化成功")
    
    print(f"\n[2/3] 系统状态:")
    print(f"   交易标的: {system.symbol}")
    print(f"   初始资金: {system.account.initial_balance}")
    print(f"   MA周期: {system.ma_period}")
    print(f"   K线数量: {system.klines.count}")
    
    if system.klines.latest:
        print(f"   最新价格: {system.klines.latest.close}")
    
    print("\n[3/3] 运行简单回测 (10个tick)...")
    results = system.start(ticks=10)
    print(f"   ✅ 回测完成，运行了 {len(results)} 个tick")
    
    print("\n" + "=" * 70)
    print("📊 回测结果")
    print("=" * 70)
    
    account_summary = system.account.get_account_summary()
    print(f"\n账户状态:")
    print(f"   可用资金: {account_summary['available_balance']:.2f}")
    print(f"   总市值: {account_summary['total_assets']:.2f}")
    print(f"   总盈亏: {account_summary['total_profit']:.2f}")
    print(f"   收益率: {account_summary['profit_rate']*100:.2f}%")
    
    trades = system.account.trade_recorder.get_records()
    print(f"\n交易记录:")
    if trades:
        print(f"   共 {len(trades)} 笔交易")
        for i, trade in enumerate(trades, 1):
            print(f"   {i}. {trade.datetime_str} - {trade.action_name}")
            print(f"      价格: {trade.price}, 数量: {trade.quantity}, 金额: {trade.amount:.2f}")
    else:
        print("   暂无交易记录")
    
    print("\n" + "=" * 70)
    print("✅ 系统运行完成")
    print("=" * 70)
    print("\n下一步:")
    print("   1. 运行 python scripts/run_realtime.py 进行实时监控")
    print("   2. 运行 python examples/live_analysis.py 进行实盘分析")
    print("   3. 运行 python tests/check_system.py 检查系统")
    print("   4. 查看 README.md 了解更多使用方法")
    
except Exception as e:
    print(f"\n❌ 系统启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
