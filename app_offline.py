#!/usr/bin/env python
"""333xt - 纯离线演示版本（不依赖外部数据源）"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="333xt Demo",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 333xt - 333交易系统 (演示版)")
st.markdown("### 专业量化交易策略平台")

# 生成模拟数据
def generate_mock_data(n_points=100):
    """生成模拟K线数据"""
    base_price = 1.0
    data = []
    
    current_date = datetime.now() - timedelta(days=n_points)
    
    for i in range(n_points):
        price_change = random.uniform(-0.02, 0.02)
        open_price = base_price * (1 + random.uniform(-0.01, 0.01))
        close_price = open_price * (1 + price_change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
        
        data.append({
            'date': current_date.strftime("%Y-%m-%d %H:%M:%S"),
            'open': round(open_price, 4),
            'high': round(high_price, 4),
            'low': round(low_price, 4),
            'close': round(close_price, 4),
            'volume': random.randint(10000, 100000)
        })
        
        base_price = close_price
        current_date += timedelta(hours=1)
    
    return pd.DataFrame(data)

# 计算MA30
def calculate_ma(data, period=30):
    """计算移动平均线"""
    return data['close'].rolling(window=period).mean()

# 生成数据
df = generate_mock_data(200)
df['ma30'] = calculate_ma(df)

# 显示信息
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("K线数量", len(df))
with col2:
    st.metric("当前价格", f"¥{df['close'].iloc[-1]:.4f}")
with col3:
    ma30_value = df['ma30'].iloc[-1]
    st.metric("MA30", f"¥{ma30_value:.4f}" if pd.notna(ma30_value) else "计算中")

st.divider()

# 绘制K线图
st.subheader("📈 K线图 (模拟数据)")

fig = make_subplots(rows=1, cols=1, shared_xaxes=True)

fig.add_trace(
    go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='K线',
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444',
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=df['date'],
        y=df['ma30'],
        mode='lines',
        name='MA30',
        line=dict(color='#f59e0b', width=2, dash='dash')
    ),
    row=1, col=1
)

fig.update_layout(
    title='科创芯片ETF (588200) - 模拟数据',
    height=500,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

st.divider()
st.success("✅ 这个离线版本可以正常运行！")
st.info("如果这个版本能显示，说明问题在于数据源访问或网络连接。")
