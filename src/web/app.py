#!/usr/bin/env python
"""333 交易系统 - 专业版"""
import sys
from pathlib import Path

# 智能设置项目路径 - 兼容本地和Streamlit Cloud部署
def setup_project_path():
    """设置正确的项目路径"""
    try:
        # 方式1: 尝试从当前文件位置查找
        current_file = Path(__file__).resolve()
        
        # 向上查找项目根目录（寻找requirements.txt作为标记）
        for parent in [current_file, *current_file.parents]:
            if (parent / "requirements.txt").exists():
                project_root = parent
                break
        else:
            # 方式2: 回退到相对路径
            project_root = Path(__file__).parent.parent.parent
        
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
    except Exception as e:
        # 如果所有方式都失败，尝试最简单的方式
        try:
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
        except:
            pass

setup_project_path()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="333交易系统",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
    <style>
        /* 全局样式 */
        .main {
            background-color: #f8fafc;
        }
        
        /* 标题样式 */
        h1 {
            color: #1e293b;
            font-weight: 700;
            padding-bottom: 1rem;
        }
        
        /* 卡片样式 */
        div[data-testid="stMetricValue"] {
            font-size: 24px;
            font-weight: 700;
        }
        
        /* 侧边栏样式 */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        /* 按钮样式 */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 成功按钮 */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #10b981, #059669);
            border: none;
        }
        
        /* 数据框样式 */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* 分隔线 */
        hr {
            border-color: #e2e8f0;
            margin: 1.5rem 0;
        }
        
        /* 信息框 */
        .stAlert {
            border-radius: 8px;
        }
        
        /* 滑块 */
        .stSlider > div > div > div > div {
            background: linear-gradient(90deg, #10b981, #3b82f6);
        }
        
        /* 切换开关 */
        .stToggle > label > div {
            background: linear-gradient(135deg, #10b981, #059669);
        }
    </style>
""", unsafe_allow_html=True)

def get_system(kline_count=2000):
    """获取系统实例"""
    try:
        with st.spinner("🚀 正在初始化交易系统..."):
            from src.main import TradingSystem
            system = TradingSystem(
                symbol="588200",
                initial_balance=100000.0
            )
            system.initialize(kline_count=kline_count)
        
        if system.strategy.current_ma is None:
            system.strategy.update_indicators(system.klines)
        
        return system
    except Exception as e:
        st.error(f"❌ 初始化失败: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def draw_interactive_kline(klines, current_ma, trades=None):
    """绘制专业K线图表"""
    klines_list = klines.klines
    if not klines_list or len(klines_list) < 2:
        return None
    
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []
    
    for k in klines_list:
        # 安全获取日期字符串
        if hasattr(k, 'datetime_str'):
            dates.append(k.datetime_str)
        elif hasattr(k, 'timestamp'):
            dates.append(datetime.fromtimestamp(k.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S"))
        else:
            dates.append(str(getattr(k, 'timestamp', '')))
        
        opens.append(getattr(k, 'open', 0))
        highs.append(getattr(k, 'high', 0))
        lows.append(getattr(k, 'low', 0))
        closes.append(getattr(k, 'close', 0))
    
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[1.0]
    )
    
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
            increasing_fillcolor='#10b981',
            decreasing_fillcolor='#ef4444',
            text=[f"📅 {d}<br>📈 开盘: ¥{o:.3f}<br>🚀 最高: ¥{h:.3f}<br>📉 最低: ¥{l:.3f}<br>💰 收盘: ¥{c:.3f}" 
                  for d, o, h, l, c in zip(dates, opens, highs, lows, closes)],
            hoverinfo='text'
        ),
        row=1, col=1
    )
    
    if current_ma:
        fig.add_hline(
            y=current_ma,
            line_dash="dash",
            line_color="#f59e0b",
            line_width=2.5,
            annotation_text=f"MA30: ¥{current_ma:.3f}",
            annotation_position="top right",
            annotation_font_color="#f59e0b",
            annotation_font_size=14
        )
    
    if trades:
        buy_x, buy_y, sell_x, sell_y = [], [], [], []
        
        for trade in trades:
            # 安全获取日期字符串
            if hasattr(trade, 'datetime_str'):
                dt_str = trade.datetime_str
            elif hasattr(trade, 'timestamp'):
                dt_str = datetime.fromtimestamp(trade.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                dt_str = str(getattr(trade, 'timestamp', ''))
            
            if not dt_str:
                continue
            
            # 安全获取价格和操作
            price = getattr(trade, 'price', 0)
            action = getattr(trade, 'action', '')
            
            if action == 'BUY':
                buy_x.append(dt_str)
                buy_y.append(price)
            else:
                sell_x.append(dt_str)
                sell_y.append(price)
        
        if buy_x:
            fig.add_trace(
                go.Scatter(
                    x=buy_x,
                    y=buy_y,
                    mode='markers',
                    marker=dict(size=14, color='#10b981', symbol='triangle-up', line=dict(width=2, color='#059669')),
                    name='🟢 买入',
                    showlegend=True
                ),
                row=1, col=1
            )
        
        if sell_x:
            fig.add_trace(
                go.Scatter(
                    x=sell_x,
                    y=sell_y,
                    mode='markers',
                    marker=dict(size=14, color='#ef4444', symbol='triangle-down', line=dict(width=2, color='#dc2626')),
                    name='🔴 卖出',
                    showlegend=True
                ),
                row=1, col=1
            )
    
    if closes:
        last_close = closes[-1]
        color = '#10b981' if last_close >= (opens[-1] if opens else last_close) else '#ef4444'
        fig.add_trace(
            go.Scatter(
                x=[dates[-1]],
                y=[last_close],
                mode='markers+text',
                marker=dict(size=18, color=color, symbol='star', line=dict(width=2, color='white')),
                text=[f'¥{last_close:.3f}'],
                textposition='top center',
                textfont=dict(size=14, color=color, weight='bold'),
                name='⭐ 当前价格',
                showlegend=True
            ),
            row=1, col=1
        )
    
    fig.update_layout(
        title='📈 科创芯片ETF (588200) K线图 + MA30均线',
        title_font=dict(size=20, color='#1e293b'),
        title_x=0.5,
        height=550,
        dragmode='pan',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e2e8f0',
            borderwidth=1
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            showspikes=True,
            spikethickness=1,
            spikedash='dot',
            spikecolor='#94a3b8'
        ),
        yaxis=dict(
            showspikes=True,
            spikethickness=1,
            spikedash='dot',
            spikecolor='#94a3b8',
            title=dict(text='价格 (¥)', font=dict(size=14))
        ),
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#ffffff',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', zeroline=False)
    
    return fig

def run_backtest(system, num_ticks):
    """运行回测"""
    try:
        results = system.start(ticks=num_ticks)
        return results, system
    except Exception as e:
        st.error(f"回测失败: {e}")
        return None, system

def main():
    # 主标题
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🎯 333交易系统 Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-top: 0; margin-bottom: 2rem;'>专业量化交易策略平台</p>", unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("<h2 style='color: #1e293b; margin-bottom: 1rem;'>⚙️ 控制面板</h2>", unsafe_allow_html=True)
        st.divider()
        
        # K线数量选择
        st.markdown("### 📊 数据设置")
        kline_count = st.slider("初始 K 线数量", min_value=100, max_value=3000, value=2000, step=100)
        
        # 自动刷新
        st.divider()
        st.markdown("### 🔄 实时更新")
        auto_refresh = st.toggle("开启自动刷新", value=False)
        refresh_interval = st.slider("刷新间隔 (秒)", min_value=5, max_value=60, value=15, step=5) if auto_refresh else None
        
        # 回测设置
        st.divider()
        st.markdown("### 🚀 策略回测")
        num_ticks = st.number_input("回测 tick 数", min_value=10, max_value=1000, value=100, step=10)
        if st.button("▶️ 运行回测", type="primary", use_container_width=True):
            st.session_state.run_backtest = True
            st.session_state.backtest_ticks = num_ticks
        
        st.divider()
        
        # 刷新按钮
        if st.button("🔄 手动刷新数据", use_container_width=True):
            st.session_state.refresh = True
            st.rerun()
        
        st.divider()
        st.info(f"🕐 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 自动刷新
    if auto_refresh and refresh_interval:
        import time
        time.sleep(refresh_interval)
        st.rerun()
    
    # 获取系统
    if 'system' not in st.session_state or st.session_state.get('refresh', False):
        system = get_system(kline_count=kline_count)
        st.session_state.system = system
        st.session_state.refresh = False
    else:
        system = st.session_state.system
    
    if system is None:
        st.stop()
    
    # 运行回测
    if st.session_state.get('run_backtest', False):
        with st.spinner("🚀 正在运行回测..."):
            results, system = run_backtest(system, st.session_state.backtest_ticks)
            st.session_state.system = system
            st.session_state.backtest_results = results
            st.session_state.run_backtest = False
            st.success(f"✅ 回测完成！共 {len(results) if results else 0} 个 tick")
    
    klines = system.klines
    account = system.account
    position = account.position
    account_summary = account.get_account_summary()
    trades = account.trade_recorder.get_records() if hasattr(account, 'trade_recorder') else []
    
    current_price = klines.latest.close if klines.latest else 0
    current_ma = system.strategy.current_ma
    trend = system.strategy.check_trend(current_price) if current_ma else 'neutral'
    
    profit_rate = 0
    if position and not position.is_empty:
        profit_rate = position.current_profit_rate
    
    # 状态栏 - 使用卡片式布局
    st.markdown("<div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        try:
            st.metric("📡 数据源", system.data_source.current_data_source_name)
        except:
            st.metric("📡 数据源", "未知")
    with col2:
        st.metric("📊 K线数量", f"{klines.count} 根")
    with col3:
        if current_ma:
            st.metric("📈 MA30", f"¥{current_ma:.3f}")
        else:
            st.metric("📈 MA30", "未计算")
    with col4:
        total_pnl = account_summary['balance'] - account_summary['initial_balance']
        pnl_delta = f"{total_pnl/account_summary['initial_balance']*100:.2f}%"
        st.metric("💰 总盈亏", f"¥{total_pnl:.2f}", pnl_delta)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 操作建议 - 更好的布局
    st.markdown("<div style='background: linear-gradient(135deg, #f0fdf4, #f0f9ff); padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    action = ""
    suggestion = ""
    color = "gray"
    
    if position and not position.is_empty:
        if profit_rate >= 0.03:
            action = "💰 二阶止盈"
            suggestion = "盈利3%，建议止盈"
        elif profit_rate >= 0.01:
            action = "🎯 一阶止盈"
            suggestion = "盈利1%，建议止盈"
        else:
            action = "✅ 持仓观望"
            suggestion = "继续持有"
    else:
        if trend == 'up':
            action = "⏸️ 观望等待"
            suggestion = "趋势向上，等待买入"
        else:
            action = "📉 空仓观望"
            suggestion = "趋势向下，保持空仓"
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("<h3 style='margin-top: 0;'>🎯 核心状态</h3>", unsafe_allow_html=True)
        st.info(action, icon="ℹ️")
    with col_b:
        st.markdown("<h3 style='margin-top: 0;'>💡 策略建议</h3>", unsafe_allow_html=True)
        st.success(suggestion, icon="✅")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # K线图区域
    st.markdown("<div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top: 0;'>📈 K线图 + MA30</h2>", unsafe_allow_html=True)
    st.info(f"💡 **提示**: 鼠标悬停在 K 线上可以查看详细数据，拖拽可以平移，滚轮可以缩放；显示全部 {len(klines.klines)} 根 K 线", icon="💡")
    
    fig = draw_interactive_kline(klines, current_ma, trades)
    if fig:
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'scrollZoom': True,
            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        })
    else:
        st.warning("无K线数据")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 账户信息卡片
    st.markdown("<div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top: 0;'>💰 账户信息</h2>", unsafe_allow_html=True)
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("🏦 初始资金", f"¥{account_summary['initial_balance']:.0f}")
    with col_info2:
        st.metric("💳 当前资金", f"¥{account_summary['balance']:.0f}")
    with col_info3:
        st.metric("📝 交易次数", f"{len(trades)} 次")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 持仓信息卡片
    st.markdown("<div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top: 0;'>📊 当前持仓</h2>", unsafe_allow_html=True)
    if position and not position.is_empty:
        col_pos1, col_pos2, col_pos3 = st.columns(3)
        with col_pos1:
            st.metric("📦 持仓数量", f"{position.quantity} 股")
        with col_pos2:
            st.metric("💸 成本价", f"¥{position.entry_price:.3f}")
        with col_pos3:
            st.metric("📈 最新价", f"¥{current_price:.3f}")
        
        if profit_rate > 0:
            st.success(f"💰 当前盈利: +{profit_rate*100:.2f}%", icon="✅")
        elif profit_rate < 0:
            st.error(f"📉 当前亏损: {profit_rate*100:.2f}%", icon="❌")
        else:
            st.info("➖ 盈亏为0", icon="ℹ️")
    else:
        st.info("暂无持仓", icon="📭")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 历史交易记录卡片
    st.markdown("<div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top: 0;'>📜 历史交易记录</h2>", unsafe_allow_html=True)
    if trades:
        trade_data = []
        for i, trade in enumerate(trades):
            # 安全获取时间
            if hasattr(trade, 'datetime_str'):
                time_str = trade.datetime_str
            elif hasattr(trade, 'timestamp'):
                time_str = datetime.fromtimestamp(trade.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = str(getattr(trade, 'timestamp', 'N/A'))
            
            # 安全获取其他属性
            action = getattr(trade, 'action', '')
            price = getattr(trade, 'price', 0)
            quantity = getattr(trade, 'quantity', 0)
            
            trade_dict = {
                '序号': i + 1,
                '时间': time_str,
                '操作': '🟢 买入' if action == 'BUY' else '🔴 卖出',
                '价格': f"¥{price:.3f}",
                '数量': quantity,
                '金额': f"¥{price * quantity:.2f}",
                '备注': getattr(trade, 'notes', '')
            }
            trade_data.append(trade_dict)
        
        df = pd.DataFrame(trade_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无交易记录", icon="📭")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
