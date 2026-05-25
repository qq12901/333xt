"""
333交易系统 - 实时监控运行脚本
"""
import sys
from pathlib import Path

# 添加项目路径（相对于scripts目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from src.realtime import create_realtime_manager

print("=" * 70)
print("333交易系统 - 实时监控")
print("=" * 70)
print("交易标的: 588200 (科创芯片ETF)")
print("=" * 70)

try:
    # 创建实时数据管理器
    manager = create_realtime_manager(symbol="588200")
    
    # 设置新K线回调
    def on_new_kline(kline):
        print(f"\n📊 新K线: {kline.datetime_str}")
        print(f"   开盘: {kline.open}, 收盘: {kline.close}")
        print(f"   最高: {kline.high}, 最低: {kline.low}")
    
    manager.on_new_kline = on_new_kline
    
    # 启动实时监控
    print("\n🚀 启动实时监控...")
    manager.start(interval_seconds=30)
    
    print("\n监控运行中，按 Ctrl+C 停止...")
    while True:
        try:
            # 获取实时价格
            price = manager.get_current_price()
            if price:
                print(f"\r当前价格: {price:.3f}", end="")
            
            # 获取K线数量
            kline_count = manager.get_klines().count
            print(f" | K线: {kline_count}", end="")
            
            sys.stdout.flush()
            sys.stdin.read(1)
        except KeyboardInterrupt:
            print("\n\n⏹️ 停止监控...")
            manager.stop()
            break
            
except Exception as e:
    print(f"\n❌ 实时监控启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
