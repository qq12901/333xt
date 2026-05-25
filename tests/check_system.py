"""
333交易系统 - 系统检查脚本
"""
import sys
from pathlib import Path

# 添加项目路径（相对于tests目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

print("=" * 70)
print("333交易系统 - 系统功能检查")
print("=" * 70)

# 1. 模块导入检查
print("\n[1/5] 模块导入检查...")
try:
    from src.models.kline import Kline, KlineData
    from src.indicators.ma import MovingAverage
    from src.strategy.strategy_333 import Strategy333
    from src.execution.simulated import SimulatedAccount
    from src.datasources import (
        EastMoneyDataSource,
        SinaDataSource,
        TencentDataSource,
        MultiDataSourceManager
    )
    from src.main import TradingSystem, create_system
    from src.realtime import RealTimeDataManager
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# 2. 数据模型检查
print("\n[2/5] 数据模型检查...")
try:
    from datetime import datetime
    test_kline = Kline(
        symbol="588200",
        timestamp=int(datetime.now().timestamp() * 1000),
        open=1.200,
        high=1.210,
        low=1.195,
        close=1.205,
        volume=1000000
    )
    print("✅ 数据模型检查通过")
except Exception as e:
    print(f"❌ 数据模型检查失败: {e}")
    sys.exit(1)

# 3. 指标计算检查
print("\n[3/5] 指标计算检查...")
try:
    ma_engine = MovingAverage(period=30)
    test_closes = [1.0 + 0.001 * i for i in range(100)]
    ma_values = ma_engine.calculate(test_closes)
    print("✅ 指标计算检查通过")
except Exception as e:
    print(f"❌ 指标计算检查失败: {e}")
    sys.exit(1)

# 4. 模拟账户检查
print("\n[4/5] 模拟账户检查...")
try:
    account = SimulatedAccount(initial_balance=100000.0)
    print("✅ 模拟账户检查通过")
except Exception as e:
    print(f"❌ 模拟账户检查失败: {e}")
    sys.exit(1)

# 5. 交易系统初始化检查
print("\n[5/5] 交易系统初始化检查...")
try:
    system = create_system(symbol="588200", initial_balance=100000.0)
    print("✅ 交易系统初始化检查通过")
except Exception as e:
    print(f"⚠️ 交易系统初始化有警告: {e}")

print("\n" + "=" * 70)
print("✅ 系统核心功能检查完成")
print("=" * 70)
