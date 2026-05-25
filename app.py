#!/usr/bin/env python
"""333xt - 333交易系统"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="333xt",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 333xt - 333交易系统")
st.markdown("### 专业量化交易策略平台 - 基于MA30均线交叉策略")

# 生成模拟数据
def generate_mock_data(n_points=200):
    """生成模拟K线数据"""
    base_price = 1.2
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

# 侧边栏设置
with st.sidebar:
    st.header("⚙️ 设置")
    n_points = st.slider("K线数量", min_value=50, max_value=500, value=200, step=50)
    st.divider()
    st.info("💡 这是演示版本，使用模拟数据")

# 生成数据
df = generate_mock_data(n_points)
df['ma30'] = calculate_ma(df)

# 状态栏
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("数据源", "模拟数据")
with col2:
    st.metric("K线数量", len(df))
with col3:
    current_price = df['close'].iloc[-1]
    st.metric("当前价格", f"¥{current_price:.4f}")
with col4:
    ma30_value = df['ma30'].iloc[-1]
    st.metric("MA30", f"¥{ma30_value:.4f}" if pd.notna(ma30_value) else "计算中")

st.divider()

# 趋势判断
trend = "📈 趋势向上" if current_price > ma30_value else "📉 趋势向下" if current_price < ma30_value else "➖ 震荡"
suggestion = "等待买入机会" if trend == "📈 趋势向上" else "保持空仓" if trend == "📉 趋势向下" else "观望"

st.markdown(f"### {trend}")
st.success(f"💡 策略建议: {suggestion}")

st.divider()

# 绘制K线图
st.subheader("📈 K线图 + MA30")

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
        increasing_fillcolor='#10b981',
        decreasing_fillcolor='#ef4444',
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
    title_font=dict(size=18),
    height=500,
    xaxis_rangeslider_visible=False,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# 账户信息
st.subheader("💰 账户信息")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("初始资金", "¥100,000.00")
with col_b:
    st.metric("当前资金", "¥102,350.00")
with col_c:
    st.metric("总盈亏", "+¥2,350.00", "+2.35%")

st.divider()
st.success("✅ 应用运行成功！")
st.info("📝 完整功能版本需要连接真实数据源，本地运行效果更佳。")
