#!/usr/bin/env python
"""333xt - 最小可运行版本"""
import streamlit as st
import sys
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="333xt",
    page_icon="🎯",
    layout="wide"
)

# 标题
st.title("🎯 333xt - 333交易系统")
st.markdown("### 专业量化交易策略平台")

# 调试信息
with st.expander("🔍 调试信息", expanded=True):
    st.write("Python 版本:", sys.version)
    st.write("当前工作目录:", str(Path.cwd()))
    st.write("文件路径:", __file__)
    st.write("sys.path 前3项:", sys.path[:3])

    # 检查目录
    project_root = Path(__file__).parent.resolve()
    st.write("项目根目录:", str(project_root))
    st.write("根目录内容:", [p.name for p in project_root.iterdir() if not p.name.startswith('.')])
    
    src_dir = project_root / "src"
    if src_dir.exists():
        st.write("src 目录内容:", [p.name for p in src_dir.iterdir()])

# 测试基础导入
try:
    st.success("✅ Streamlit 运行正常！")
    
    # 测试 pandas
    import pandas as pd
    st.success("✅ Pandas 导入成功")
    
    # 测试 plotly
    import plotly
    st.success("✅ Plotly 导入成功")
    
except Exception as e:
    st.error(f"❌ 导入错误: {e}")
    import traceback
    st.code(traceback.format_exc())

st.divider()

# 尝试导入我们的模块
try:
    project_root = Path(__file__).parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    st.info("正在尝试导入 src.main...")
    
    from src.main import TradingSystem
    st.success("✅ TradingSystem 导入成功！")
    
    # 尝试创建系统
    with st.spinner("正在初始化系统..."):
        system = TradingSystem(symbol="588200", initial_balance=100000.0)
        system.initialize(kline_count=100)
    
    st.success("✅ 系统初始化成功！")
    st.metric("K线数量", system.klines.count)
    st.metric("MA30", f"¥{system.strategy.current_ma:.3f}" if system.strategy.current_ma else "未计算")
    
except Exception as e:
    st.error(f"❌ 系统错误: {e}")
    import traceback
    st.code(traceback.format_exc())

st.divider()
st.markdown("---")
st.info("如果看到这个页面，说明 Streamlit 正在运行！")
