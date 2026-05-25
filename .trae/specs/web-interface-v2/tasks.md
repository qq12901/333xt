# 333交易系统 V2.0 - Web界面实施计划

## [ ] Task 1: 项目结构与依赖安装
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 `src/web/` 目录结构
  - 创建 `src/web/components/` 子目录
  - 创建必要的 `__init__.py` 文件
  - 创建 Web 启动脚本 `scripts/run_web.py`
- **Acceptance Criteria Addressed**: 基础架构建立
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构正确创建
  - `programmatic` TR-1.2: Streamlit应用可以启动
- **Notes**: 先搭建基础架构，确保Streamlit可以正常运行

---

## [ ] Task 2: K线图表组件开发
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 开发 `src/web/components/kline_chart.py`
  - 实现K线蜡烛图绘制（复用Kline模型）
  - 实现MA30均线叠加显示
  - 配置Plotly图表样式（阳线绿色、阴线红色）
  - 添加图表交互功能（缩放、平移、悬停提示）
- **Acceptance Criteria Addressed**: Requirement - K线图表展示
- **Test Requirements**:
  - `human-judgement` TR-2.1: K线蜡烛图正确显示，颜色区分正确
  - `human-judgement` TR-2.2: MA30均线正确叠加显示
  - `human-judgement` TR-2.3: 图表交互功能正常
- **Notes**: 核心组件，优先实现，确保复用现有KlineData数据结构

---

## [ ] Task 3: 账户面板组件开发
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 开发 `src/web/components/account_panel.py`
  - 实现账户余额展示（复用SimulatedAccount模型）
  - 实现持仓状态卡片
  - 实现盈亏统计展示
  - 添加实时刷新功能
- **Acceptance Criteria Addressed**: Requirement - 账户状态展示
- **Test Requirements**:
  - `human-judgement` TR-3.1: 账户余额正确显示
  - `human-judgement` TR-3.2: 持仓信息完整展示
  - `human-judgement` TR-3.3: 盈亏计算正确
- **Notes**: 复用现有SimulatedAccount的账户摘要接口

---

## [ ] Task 4: 信号监控组件开发
- **Priority**: P0
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 开发 `src/web/components/signal_monitor.py`
  - 实现当前趋势状态显示（多头/空头）
  - 实现MA30数值实时展示
  - 实现最新信号类型和详情
  - 实现信号历史记录列表
  - 信号触发时高亮提醒
- **Acceptance Criteria Addressed**: Requirement - 信号监控面板
- **Test Requirements**:
  - `human-judgement` TR-4.1: 趋势状态正确显示
  - `human-judgement` TR-4.2: MA30数值实时更新
  - `human-judgement` TR-4.3: 信号记录完整展示
- **Notes**: 复用现有Signal模型和Strategy333信号生成逻辑

---

## [ ] Task 5: 交易记录组件开发
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 开发 `src/web/components/trade_history.py`
  - 实现交易记录表格展示（复用TradeRecorder）
  - 实现按日期筛选功能
  - 实现交易统计摘要
  - 实现交易记录导出功能
- **Acceptance Criteria Addressed**: Requirement - 交易记录展示
- **Test Requirements**:
  - `human-judgement` TR-5.1: 交易记录表格正常显示
  - `human-judgement` TR-5.2: 日期筛选功能正常
  - `programmatic` TR-5.3: 数据正确读取自TradeRecorder
- **Notes**: 复用现有TradeRecorder的数据记录功能

---

## [ ] Task 6: 系统状态组件开发
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 开发系统状态展示区域
  - 实现数据源状态指示
  - 实现K线数据条数显示
  - 实现最后更新时间显示
  - 实现刷新按钮
- **Acceptance Criteria Addressed**: Requirement - 系统状态监控
- **Test Requirements**:
  - `human-judgement` TR-6.1: 数据源状态正确显示
  - `human-judgement` TR-6.2: 刷新功能正常
- **Notes**: 复用现有MultiDataSourceManager的状态查询

---

## [ ] Task 7: Streamlit主应用集成
- **Priority**: P0
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**: 
  - 开发 `src/web/app.py` 主应用
  - 整合所有组件到完整页面
  - 实现侧边栏配置
  - 实现页面布局和样式
  - 实现多标签页切换
- **Acceptance Criteria Addressed**: UI整合
- **Test Requirements**:
  - `human-judgement` TR-7.1: 页面布局合理美观
  - `human-judgement` TR-7.2: 标签页切换正常
  - `programmatic` TR-7.3: 所有组件正常加载
- **Notes**: 将所有组件整合成完整的Web应用

---

## [ ] Task 8: 启动脚本和文档
- **Priority**: P1
- **Depends On**: Task 7
- **Description**: 
  - 创建 `scripts/run_web.py` 启动脚本
  - 更新 `README.md` 添加Web界面使用说明
  - 创建Web界面演示示例
- **Acceptance Criteria Addressed**: 文档完善
- **Test Requirements**:
  - `programmatic` TR-8.1: 启动脚本可以运行Streamlit
  - `human-judgement` TR-8.2: README说明清晰
- **Notes**: 提供完整的使用文档

---

## Task Dependencies

```
Task 1 (项目结构)
    ↓
Task 2 ─┬─→ Task 7 (主应用集成)
Task 3 ─┤
Task 4 ─┤
Task 5 ─┤
Task 6 ─┘
    ↓
Task 8 (文档完善)
```

## 实施顺序

1. **第1步**: Task 1 - 建立项目结构
2. **第2步**: Task 2 - K线图表（核心组件）
3. **第3步**: Task 3 - 账户面板
4. **第4步**: Task 4 - 信号监控
5. **第5步**: Task 5 - 交易记录
6. **第6步**: Task 6 - 系统状态
7. **第7步**: Task 7 - 主应用集成
8. **第8步**: Task 8 - 文档完善
