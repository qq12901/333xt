# 333交易系统

专业量化交易策略平台 - 基于MA30均线交叉策略

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy)

## 📁 项目结构

```
333交易系统/
├── .github/
│   └── workflows/
│       └── python-app.yml   # GitHub CI工作流程
├── .streamlit/
│   └── config.toml         # Streamlit配置文件
├── config/                     # 配置文件
├── examples/                   # 示例代码
├── scripts/                    # 辅助脚本
│   ├── run_web.bat         # Windows一键启动
│   ├── run_web.sh         # Linux/Mac一键启动
│   ├── run_web.py          # Python启动脚本
│   ├── run_realtime.py     # 实时运行
│   └── start_system.py      # 启动系统
├── src/                        # 核心代码
│   ├── datasources/          # 数据源管理
│   ├── execution/           # 交易执行
│   ├── indicators/          # 技术指标
│   ├── logging/            # 日志记录
│   ├── models/             # 数据模型
│   ├── strategy/           # 交易策略
│   ├── web/                # Web界面
│   ├── main.py
│   └── realtime.py
├── tests/                      # 测试脚本
├── .gitignore
├── app.py                      # ⭐ Streamlit Cloud入口文件
├── README.md
└── requirements.txt
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

## 🚀 快速体验

### 1️⃣ 在线部署到Streamlit Cloud

点击下方按钮一键部署（免费）：

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy)

**部署步骤：**
1. 点击上面的按钮
2. 登录您的GitHub账号
3. 填写部署信息：
   - **Repository**: 选择您的333交易系统仓库
   - **Branch**: `main`
   - **Main file path**: **`app.py`** (⚠️ 关键！不要填其他路径)
4. 点击 **Deploy!** 按钮
5. 等待约1-2分钟，即可获得永久在线访问地址！

### 2️⃣ 本地运行

#### 一键启动

```bash
# Windows
scripts\run_web.bat

# Linux/Mac
bash scripts/run_web.sh
```

#### 或手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动Web界面
streamlit run app.py
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
