# 333交易系统 - 文件结构整理实现计划

## [ ] Task 1: 创建目录结构
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 scripts/ 目录
  - 创建 examples/ 目录
  - 创建 tests/ 目录
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 三个新目录已创建
- **Notes**: 使用mkdir命令创建

## [ ] Task 2: 移动运行脚本到scripts/
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 移动 run_realtime.py 到 scripts/
  - 移动 start_system.py 到 scripts/
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件已移动到scripts/目录
- **Notes**: 需要更新这些文件的导入路径

## [ ] Task 3: 移动示例代码到examples/
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 移动 example_real_data.py 到 examples/
  - 移动 live_analysis.py 到 examples/
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件已移动到examples/目录
- **Notes**: 需要更新这些文件的导入路径

## [ ] Task 4: 移动测试文件到tests/
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 移动 check_system.py 到 tests/
  - 移动 test_backtest.py 到 tests/
  - 移动 test_data_sources.py 到 tests/
  - 移动 debug_datasource.py 到 tests/
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件已移动到tests/目录
- **Notes**: 需要更新这些文件的导入路径

## [ ] Task 5: 更新文件导入路径
- **Priority**: P0
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 更新 scripts/ 目录下文件的导入路径
  - 更新 examples/ 目录下文件的导入路径
  - 更新 tests/ 目录下文件的导入路径
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有文件导入路径正确
  - `programmatic` TR-5.2: 系统能正常启动和运行
- **Notes**: 使用sys.path.insert更新路径

## [ ] Task 6: 更新README.md
- **Priority**: P1
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 更新README中的文件结构说明
  - 更新README中的运行命令说明
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-6.1: README反映新的文件结构
- **Notes**: 更新文档以匹配新结构

## [ ] Task 7: 验证系统功能
- **Priority**: P0
- **Depends On**: Task 5, Task 6
- **Description**: 
  - 运行系统检查脚本验证功能
  - 运行实盘分析验证功能
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-7.1: 系统能正常启动
  - `programmatic` TR-7.2: 实盘分析能正常运行
- **Notes**: 确保所有功能正常工作
