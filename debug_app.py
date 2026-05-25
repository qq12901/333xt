#!/usr/bin/env python
"""调试用的简单应用，显示具体错误信息"""
import sys
from pathlib import Path

print("=" * 60)
print("开始调试")
print("=" * 60)

# 检查项目路径
print("\n1. 检查项目路径:")
print(f"   __file__: {__file__}")
project_root = Path(__file__).parent.resolve()
print(f"   项目根目录: {project_root}")
sys.path.insert(0, str(project_root))
print(f"   sys.path: {sys.path[:3]}")

# 检查 src 目录
print("\n2. 检查 src 目录内容:")
src_dir = project_root / "src"
print(f"   src 目录存在: {src_dir.exists()}")
if src_dir.exists():
    print(f"   src 目录内容: {list(src_dir.iterdir())}")

# 尝试导入 streamlit
print("\n3. 尝试导入依赖:")
try:
    import streamlit as st
    print("   ✅ streamlit 导入成功")
except Exception as e:
    print(f"   ❌ streamlit 导入失败: {e}")
    import traceback
    print(traceback.format_exc())

try:
    import pandas as pd
    print("   ✅ pandas 导入成功")
except Exception as e:
    print(f"   ❌ pandas 导入失败: {e}")

try:
    import plotly
    print("   ✅ plotly 导入成功")
except Exception as e:
    print(f"   ❌ plotly 导入失败: {e}")

# 尝试导入 src.main
print("\n4. 尝试导入 src.main:")
try:
    print("   正在导入...")
    from src.main import TradingSystem
    print("   ✅ TradingSystem 导入成功")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    import traceback
    print("\n详细错误信息:")
    print(traceback.format_exc())

print("\n" + "=" * 60)
print("调试结束")
print("=" * 60)
