# 333交易系统

专业量化交易策略平台 - 基于MA30均线交叉策略

## 项目结构

```
333xt/
├── src/                    # 源代码
│   ├── main.py            # 主程序入口
│   ├── realtime.py        # 实时数据管理
│   ├── api/               # API接口
│   ├── datasources/       # 数据源管理
│   │   ├── base.py
│   │   ├── eastmoney.py   # 东方财富数据源
│   │   ├── sina.py       # 新浪财经数据源
│   │   ├── tencent.py     # 腾讯财经数据源
│   │   └── multi_source_manager.py  # 多数据源管理器
│   ├── execution/         # 交易执行
│   │   └── simulated.py   # 模拟账户
│   ├── indicators/        # 技术指标
│   │   └── ma.py         # 移动平均线
│   ├── logging/           # 日志记录
│   │   └── logger.py
│   ├── models/            # 数据模型
│   │   ├── kline.py      # K线数据
│   │   ├── position.py   # 持仓
│   │   ├── signal.py     # 交易信号
│   │   └── trade.py      # 交易记录
│   ├── strategy/          # 交易策略
│   │   └── strategy_333.py  # 333策略
│   └── web/               # Web界面
│       ├── app.py         # 主应用
│       ├── components/    # UI组件
│       └── __init__.py
├── config/                # 配置文件
│   ├── settings.py
│   ├── strategies.py
│   └── __init__.py
├── tests/                 # 测试脚本
│   ├── check_system.py    # 系统检查
│   └── test_backtest.py  # 回测测试
├── examples/              # 示例代码
│   ├── example_real_data.py   # 真实数据示例
│   └── live_analysis.py       # 实盘分析
├── scripts/               # 辅助脚本
│   ├── run_web.py         # 启动Web
│   ├── run_realtime.py    # 实时运行
│   └── start_system.py    # 启动系统
├── logs/                  # 日志文件
└── README.md              # 项目说明
```

## 核心功能

### 1. 333交易策略
- **MA30均线交叉**: 基于30分钟K线的移动平均线
- **阶梯止盈**: 1%和3%两档止盈策略
- **趋势判断**: 自动识别趋势方向

### 2. 多数据源支持
- 腾讯财经 (优先)
- 东方财富
- 新浪财经
- 自动切换和容错

### 3. Web界面
- 交互式K线图表 (Plotly)
- 实时状态监控
- 回测功能
- 交易记录查看

## 快速开始

### 启动Web界面

```bash
streamlit run src/web/app.py
```

或使用快捷脚本：

```bash
python scripts/run_web.py
```

### 运行回测

```bash
python tests/test_backtest.py
```

### 系统检查

```bash
python tests/check_system.py
```

## 策略说明

### 买入信号 (牵手)
- 当前一根K线收盘价在MA30下方
- 当前K线收盘价在MA30上方
- 收盘价与MA30形成金叉

### 卖出信号 (分手)
- 当前一根K线收盘价在MA30上方
- 当前K线收盘价在MA30下方
- 收盘价与MA30形成死叉

### 止盈策略
- **一阶止盈**: 盈利达到1%，卖出50%持仓
- **二阶止盈**: 盈利达到3%，卖出剩余30%持仓

## 技术栈

- Python 3.8+
- Streamlit - Web框架
- Plotly - 交互式图表
- Pandas - 数据处理
- Requests - HTTP请求

## 注意事项

1. 本系统仅供学习和研究使用
2. 实盘交易前请充分测试
3. 市场有风险，投资需谨慎
4. 策略逻辑保持不变，不添加额外因子

## 版本历史

### V3.0
- 全新Web界面 (Plotly)
- 支持2000根K线数据
- 专业UI设计
- 实时数据更新
- 回测功能

### V2.0
- 多数据源支持
- 自动切换机制
- MA30计算优化

### V1.0
- 基础框架
- 333策略实现

## 联系方式

如有问题，请查看项目文档或提交Issue。

---

**⚠️ 免责声明**: 本项目仅供教育目的，不构成投资建议。使用本系统造成的任何损失，作者不承担责任。
