#!/usr/bin/env python
"""最简单的测试版本，直接测试 MA30 是否能显示"""
import sys
from pathlib import Path
project_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_path))

import streamlit as st
from datetime import datetime
from src.main import create_system

st.set_page_config(page_title="333交易系统 测试版", page_icon="🧪", layout="wide")

st.title("🧪 333交易系统 - MA30测试")

st.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    # 每次都重新创建系统
    with st.spinner("正在初始化系统..."):
        system = create_system(symbol="588200", initial_balance=100000.0)
    
    st.success("✅ 系统创建成功!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("数据源", system.data_source.current_data_source_name)
    
    with col2:
        st.metric("K线数量", system.klines.count)
    
    with col3:
        if system.strategy.current_ma:
            st.metric("MA30", f"¥{system.strategy.current_ma:.3f}", delta=None)
        else:
            st.error("❌ MA30 未计算")
    
    st.divider()
    st.subheader("详细信息")
    
    st.write(f"最新K线时间: {system.klines.latest.datetime_str if system.klines.latest else 'N/A'}")
    st.write(f"最新价格: ¥{system.klines.latest.close if system.klines.latest else 'N/A'}")
    
    st.code(f"""
调试信息:
- strategy.current_ma = {system.strategy.current_ma}
- strategy.ma_engine.current_ma = {system.strategy.ma_engine.current_ma}
- klines.closes 数量: {len(system.klines.closes)}
- klines.closes 最后5个: {system.klines.closes[-5:] if len(system.klines.closes)>=5 else system.klines.closes}
""")
    
except Exception as e:
    st.error(f"❌ 错误: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

if st.button("🔄 刷新测试"):
    st.rerun()
