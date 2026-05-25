# 333交易系统 V2.0 - 极简Web界面实施计划

## [x] Task 1: 重构Web应用为极简单页面
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 完全重写 `src/web/app.py`
  - 单页面设计，所有信息一屏展示
  - 删除多标签页设计
  - 删除复杂参数配置
  - 突出"下一个操作"这个核心信息
- **Acceptance Criteria Addressed**: 极简单页面布局
- **Test Requirements**:
  - `human-judgement` TR-1.1: 所有核心信息在一屏内可见
  - `human-judgement` TR-1.2: "下一个操作"信息突出显示
  - `human-judgement` TR-1.3: 界面简洁不花哨
- **Notes**: 保持代码简洁，不超过200行

---

## [x] Task 2: 实现核心状态展示
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 实现账户状态区域（余额、持仓、盈亏）
  - 实现333策略分析区域（MA30、趋势、信号）
  - 实现下一个操作建议（最重要，红色大字）
  - 实现333策略规则说明
- **Acceptance Criteria Addressed**: 核心状态展示
- **Test Requirements**:
  - `human-judgement` TR-2.1: 账户余额清晰显示
  - `human-judgement` TR-2.2: 持仓盈亏清晰显示
  - `human-judgement` TR-2.3: 下一个操作建议突出显示
- **Notes**: 按优先级排列信息，操作建议最重要

---

## [x] Task 3: 实现简洁价格线图表
- **Priority**: P1
- **Depends On**: Task 1
- **Description**:
  - 使用Streamlit原生st.line_chart
  - 显示最近30根K线收盘价
  - 叠加MA30均线
  - 简洁不复杂
- **Acceptance Criteria Addressed**: 简洁价格线
- **Test Requirements**:
  - `human-judgement` TR-3.1: 价格折线图正常显示
  - `human-judgement` TR-3.2: MA30均线叠加正确
- **Notes**: 不使用Plotly，保持简单

---

## [x] Task 4: 实现自动刷新功能
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 默认30秒自动刷新
  - 显示最后更新时间
  - 手动刷新按钮（备用）
- **Acceptance Criteria Addressed**: 自动实时刷新
- **Test Requirements**:
  - `programmatic` TR-4.1: 自动刷新功能正常
  - `human-judgement` TR-4.2: 最后更新时间正确显示
- **Notes**: 简单可靠，不使用复杂定时器

---

## Task Dependencies

```
Task 1 (重构Web应用)
    ↓
Task 2 ─┬─→ 整合到 Task 1
Task 3 ─┘
    ↓
Task 4 → 整合到 Task 1
```

## 实施原则

1. **保持极简** - 不超过200行代码
2. **一屏展示** - 所有信息一眼可见
3. **操作优先** - 下一个操作建议最重要
4. **无花哨功能** - 只保留核心功能
5. **实用为主** - 删除所有不必要的东西
