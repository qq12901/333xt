# 333交易系统 - 文件结构优化 PRD

## Overview
- **Summary**: 重新梳理333交易系统的项目文件结构，将临时文件、测试文件、示例文件分类整理到指定目录
- **Purpose**: 使项目结构清晰、易于维护和扩展
- **Target Users**: 开发者和系统维护人员

## Goals
- 整理根目录下的临时文件到合适位置
- 创建清晰的目录层次结构
- 保留核心源代码结构不变
- 便于后续扩展和维护

## Non-Goals (Out of Scope)
- 不修改核心代码逻辑
- 不添加新功能
- 不改变现有API接口

## Background & Context
当前项目结构存在以下问题：
- 根目录下有多个临时测试文件（check_system.py, debug_datasource.py, test_backtest.py等）
- 示例文件和运行脚本混杂在根目录
- 缺少明确的分类目录

## Functional Requirements
- **FR-1**: 创建 scripts/ 目录存放运行脚本（run_realtime.py, start_system.py）
- **FR-2**: 创建 examples/ 目录存放示例代码（example_real_data.py, live_analysis.py）
- **FR-3**: 创建 tests/ 目录存放测试文件（check_system.py, test_backtest.py, debug_datasource.py）
- **FR-4**: 更新所有相关导入路径确保文件移动后正常工作
- **FR-5**: 更新 README.md 反映新的文件结构

## Non-Functional Requirements
- **NFR-1**: 目录结构清晰、符合Python项目最佳实践
- **NFR-2**: 文件移动后系统功能不受影响
- **NFR-3**: 便于后续扩展和维护

## Constraints
- **Technical**: Python文件导入路径需要更新
- **Dependencies**: 所有导入需要正确指向新位置

## Assumptions
- 用户希望保持src/目录结构不变
- 用户希望保留所有现有功能

## Acceptance Criteria

### AC-1: 文件结构整理完成
- **Given**: 当前杂乱的项目结构
- **When**: 执行文件整理
- **Then**: 所有文件按类别放入指定目录
- **Verification**: `human-judgment`

### AC-2: 导入路径更新完成
- **Given**: 文件已移动到新位置
- **When**: 运行系统
- **Then**: 所有导入正常工作，系统功能不受影响
- **Verification**: `programmatic`

### AC-3: README更新完成
- **Given**: 文件结构已整理
- **When**: 查看README.md
- **Then**: README反映新的文件结构
- **Verification**: `human-judgment`

## Open Questions
- [ ] 无

---

## 目标文件结构

```
333xt/                              # 项目根目录
├── .trae/                          # Trae工作目录（保留）
│   └── specs/                      # 规格文档
│       ├── build-333-trading-system/
│       ├── multi-data-source/
│       └── system-complete-check/
├── config/                         # 配置文件（保留）
│   ├── __init__.py
│   ├── settings.py
│   └── strategies.py
├── logs/                           # 日志目录（保留）
│   ├── signals/
│   └── trading_*.log
├── scripts/                        # 运行脚本（新增）
│   ├── run_realtime.py             # 实时监控运行脚本
│   └── start_system.py             # 快速启动脚本
├── examples/                       # 示例代码（新增）
│   ├── example_real_data.py        # 真实数据使用示例
│   └── live_analysis.py            # 实盘分析示例
├── tests/                          # 测试文件（新增）
│   ├── check_system.py             # 系统检查脚本
│   ├── test_backtest.py            # 回测测试
│   ├── test_data_sources.py        # 数据源测试
│   └── debug_datasource.py         # 数据源调试
├── src/                            # 核心源代码（保留）
│   ├── __init__.py
│   ├── main.py                     # 主程序入口
│   ├── realtime.py                 # 实时行情模块
│   ├── api/                        # API接口
│   ├── datasources/                # 数据源
│   ├── execution/                  # 执行模块
│   ├── indicators/                 # 指标计算
│   ├── logging/                    # 日志系统
│   ├── models/                     # 数据模型
│   └── strategy/                   # 策略模块
├── 333策略完整系统.docx             # 原始需求文档（保留）
├── README.md                       # 项目说明文档
└── SYSTEM_CHECK_REPORT.md          # 系统检查报告（保留）
```
