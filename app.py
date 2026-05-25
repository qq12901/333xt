#!/usr/bin/env python
"""333交易系统 - Streamlit Cloud 专用"""
import sys
import os
from pathlib import Path

# ==============================================
# 路径设置 - 最简洁可靠的方式
# ==============================================
try:
    project_root = Path(__file__).parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except Exception as e:
    pass

# ==============================================
# 基础导入
# ==============================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ==============================================
# 设置页面配置
# ==============================================
st.set_page_config(
    page_title="333交易系统",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================
# 核心功能
# ==============================================
@st.cache_resource(ttl=3600)
def get_system_instance(kline_count=1000):
    """获取交易系统实例（带缓存）"""
    try:
        from src.main import TradingSystem
        system = TradingSystem(symbol="588200", initial_balance=100000.0)
        system.initialize(kline_count=kline_count)
        
        if system.strategy.current_ma is None:
            system.strategy.update_indicators(system.klines)
        
        return system
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def draw_chart(klines, current_ma):
    """绘制 K 线图"""
    klines_list = klines.klines
    if not klines_list or len(klines_list) < 2:
        return None
    
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []
    
    for k in klines_list:
        if hasattr(k, 'datetime_str'):
            dates.append(k.datetime_str)
        elif hasattr(k, 'timestamp'):
            dates.append(datetime.fromtimestamp(k.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S"))
        else:
            dates.append("")
        
        opens.append(getattr(k, 'open', 0))
        highs.append(getattr(k, 'high', 0))
        lows.append(getattr(k, 'low', 0))
        closes.append(getattr(k, 'close', 0))
    
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name='K线',
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444',
        ),
        row=1, col=1
    )
    
    if current_ma:
        fig.add_hline(
            y=current_ma,
            line_dash="dash",
            line_color="#f59e0b",
            line_width=2,
            annotation_text=f"MA30: ¥{current_ma:.3f}",
        )
    
    fig.update_layout(
        title='📈 科创芯片ETF (588200)',
        height=500,
        xaxis_rangeslider_visible=False,
        showlegend=False
    )
    
    return fig

# ==============================================
# 主界面
# ==============================================
st.title("🎯 333 交易系统")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")
    kline_count = st.slider("K 线数量", min_value=100, max_value=3000, value=1000, step=100)
    st.divider()
    st.info(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 获取系统
system = get_system_instance(kline_count=kline_count)

if system:
    klines = system.klines
    account = system.account
    account_summary = account.get_account_summary()
    position = account.position
    current_ma = system.strategy.current_ma
    current_price = klines.latest.close if klines.latest else 0
    
    # 状态栏
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        try:
            st.metric("数据源", system.data_source.current_data_source_name)
        except:
            st.metric("数据源", "未知")
    with col2:
        st.metric("K 线", f"{klines.count} 根")
    with col3:
        if current_ma:
            st.metric("MA30", f"¥{current_ma:.3f}")
        else:
            st.metric("MA30", "未计算")
    with col4:
        total_pnl = account_summary['balance'] - account_summary['initial_balance']
        pnl_pct = (total_pnl / account_summary['initial_balance'] * 100) if account_summary['initial_balance'] > 0 else 0
        st.metric("总盈亏", f"¥{total_pnl:.2f}", f"{pnl_pct:.2f}%")
    
    st.divider()
    
    # K 线图
    st.subheader("📈 K 线图")
    fig = draw_chart(klines, current_ma)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("暂无数据")
    
    st.divider()
    
    # 账户信息
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("初始资金", f"¥{account_summary['initial_balance']:.0f}")
    with col_b:
        st.metric("当前资金", f"¥{account_summary['balance']:.0f}")
    with col_c:
        trades = account.trade_recorder.get_records() if hasattr(account, 'trade_recorder') else []
        st.metric("交易次数", f"{len(trades)} 次")
    
    # 持仓信息
    if position and not position.is_empty:
        st.divider()
        st.subheader("📊 持仓")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric("持仓数量", f"{position.quantity} 股")
        with col_p2:
            st.metric("成本价", f"¥{position.entry_price:.3f}")
        with col_p3:
            st.metric("最新价", f"¥{current_price:.3f}")
        
        profit_rate = position.current_profit_rate if hasattr(position, 'current_profit_rate') else 0
        if profit_rate > 0:
            st.success(f"💰 当前盈利: +{profit_rate*100:.2f}%")
        elif profit_rate < 0:
            st.error(f"📉 当前亏损: {profit_rate*100:.2f}%")
        else:
            st.info("➖ 盈亏为0")
    
    # 历史交易记录
    if trades:
        st.divider()
        st.subheader("📜 历史交易")
        
        trade_data = []
        for i, trade in enumerate(trades):
            if hasattr(trade, 'datetime_str'):
                time_str = trade.datetime_str
            elif hasattr(trade, 'timestamp'):
                time_str = datetime.fromtimestamp(trade.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = ""
            
            action = getattr(trade, 'action', '')
            price = getattr(trade, 'price', 0)
            quantity = getattr(trade, 'quantity', 0)
            
            trade_data.append({
                '序号': i + 1,
                '时间': time_str,
                '操作': '🟢 买入' if action == 'BUY' else '🔴 卖出',
                '价格': f"¥{price:.3f}",
                '数量': quantity,
                '金额': f"¥{price * quantity:.2f}",
            })
        
        df = pd.DataFrame(trade_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
