"""
333交易系统 V2.0 - K线图表组件

基于Plotly的K线蜡烛图和MA30均线可视化组件
"""
import sys
from pathlib import Path

# 添加项目路径
project_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_path))

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List

# 尝试导入系统模块
try:
    from src.models.kline import Kline, KlineData
except ImportError:
    Kline = None
    KlineData = None


def create_kline_chart(klines: list, ma30_values: list = None, show_volume: bool = True) -> go.Figure:
    """
    创建K线蜡烛图（带MA30均线）
    
    Args:
        klines: K线数据列表
        ma30_values: MA30均线值列表（可选）
        show_volume: 是否显示成交量
        
    Returns:
        Plotly图形对象
    """
    if not klines or len(klines) == 0:
        return None
    
    # 创建子图
    if show_volume:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('K线 + MA30', '成交量')
        )
    else:
        fig = make_subplots(rows=1, cols=1)
    
    # 准备数据
    dates = [k.datetime_str for k in klines]
    opens = [k.open for k in klines]
    highs = [k.high for k in klines]
    lows = [k.low for k in klines]
    closes = [k.close for k in klines]
    volumes = [k.volume for k in klines]
    
    # 颜色设置
    colors = ['#26A69A' if close >= open_ else '#EF5350' for close, open_ in zip(closes, opens)]
    
    # 添加K线蜡烛图
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name='K线',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350'
        ),
        row=1, col=1
    )
    
    # 添加MA30均线
    if ma30_values and len(ma30_values) > 0:
        # MA30从第30根K线开始
        ma_start_idx = 29
        if len(ma30_values) >= ma_start_idx + 1:
            ma_dates = dates[ma_start_idx:]
            ma_values = ma30_values[ma_start_idx:]
            
            fig.add_trace(
                go.Scatter(
                    x=ma_dates,
                    y=ma_values,
                    mode='lines',
                    name='MA30',
                    line=dict(color='#9C27B0', width=2)
                ),
                row=1, col=1
            )
    
    # 添加成交量柱状图
    if show_volume:
        volume_colors = ['#26A69A' if close >= open_ else '#EF5350' 
                        for close, open_ in zip(closes, opens)]
        
        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                name='成交量',
                marker_color=volume_colors,
                opacity=0.5
            ),
            row=2, col=1
        )
    
    # 更新布局
    fig.update_layout(
        title=dict(
            text=f'<b>K线走势与MA30均线</b>',
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white',
        height=600 if show_volume else 500
    )
    
    # 更新Y轴标签
    fig.update_yaxes(title_text="价格", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="成交量", row=2, col=1)
    
    return fig


def create_simple_line_chart(klines: KlineData, title: str = "价格走势") -> go.Figure:
    """
    创建简单的价格折线图
    
    Args:
        klines: KlineData对象
        title: 图表标题
        
    Returns:
        Plotly图形对象
    """
    if not klines or klines.count == 0:
        return None
    
    kline_list = klines.klines
    dates = [k.datetime_str for k in kline_list]
    closes = [k.close for k in kline_list]
    
    fig = go.Figure()
    
    # 添加收盘价折线
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=closes,
            mode='lines+markers',
            name='收盘价',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=4)
        )
    )
    
    # 计算并添加MA30
    if klines.count >= 30:
        closes_list = klines.closes
        ma30 = []
        ma_dates = []
        
        for i in range(29, len(closes_list)):
            ma_value = sum(closes_list[i-29:i+1]) / 30
            ma30.append(ma_value)
            ma_dates.append(dates[i])
        
        fig.add_trace(
            go.Scatter(
                x=ma_dates,
                y=ma30,
                mode='lines',
                name='MA30',
                line=dict(color='#9C27B0', width=2)
            )
        )
    
    # 更新布局
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b>',
            x=0.5,
            font=dict(size=16)
        ),
        xaxis_title='时间',
        yaxis_title='价格',
        template='plotly_white',
        hovermode='x unified',
        height=400
    )
    
    return fig


def render_kline_html(klines: list, ma30_values: list = None) -> str:
    """
    渲染K线图为HTML字符串（用于静态展示）
    
    Args:
        klines: K线数据列表
        ma30_values: MA30均线值列表
        
    Returns:
        HTML字符串
    """
    fig = create_kline_chart(klines, ma30_values)
    if fig:
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    return ""


if __name__ == "__main__":
    # 测试代码
    print("K线图表组件测试")
    print("使用示例:")
    print("```python")
    print("from src.web.components.kline_chart import create_kline_chart")
    print("from src.models import KlineData")
    print("")
    print("# 获取K线数据")
    print("klines = system.klines")
    print("")
    print("# 创建图表")
    print("fig = create_kline_chart(klines.klines)")
    print("")
    print("# 在Streamlit中显示")
    print("import streamlit as st")
    print("st.plotly_chart(fig)")
    print("```")
