"""
333交易系统 - 回测测试
"""
import sys
from pathlib import Path

# 添加项目路径（相对于tests目录）
project_path = Path(__file__).parent.parent
sys.path.insert(0, str(project_path))

from src.main import create_system

print("\n" + "="*60)
print("333交易系统 - 完整策略回测 (50个tick)")
print("="*60)

system = create_system(symbol='588200', initial_balance=100000.0)
results = system.start(ticks=50)

print(f"\n回测完成！执行了 {len(results)} 个信号")
print(f"\n账户总结:")
account_summary = system.account.get_account_summary()
for key, value in account_summary.items():
    print(f'  {key}: {value}')

print(f"\n交易记录:")
trades = system.account.trade_recorder.get_records()
print(f'  共有 {len(trades)} 笔交易')
for i, trade in enumerate(trades):
    print(f'  [{i+1}] {trade.datetime_str} {trade.action_name} {trade.quantity}股 @ {trade.price}')
