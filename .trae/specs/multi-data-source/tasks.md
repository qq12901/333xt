# 333交易系统 - 多数据源支持 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 移除模拟数据源
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 删除 mock.py 文件
  - 从 __init__.py 中移除 MockDataSource 导出
  - 从相关配置和主程序中移除引用
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: mock.py 文件不存在
  - `programmatic` TR-1.2: 代码中无 MockDataSource 引用
  - `human-judgement` TR-1.3: 检查所有文件，确保无遗留引用
- **Notes**: 需检查 main.py、README.md 等文件

## [ ] Task 2: 实现新浪财经数据源 (SinaDataSource)
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 sina.py 文件
  - 实现 DataSource 基类接口
  - 支持30分钟K线获取
  - 支持实时行情获取
  - 处理沪市/深市代码格式
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: fetch_klines() 返回至少50条有效K线
  - `programmatic` TR-2.2: get_realtime_quote() 返回当前价格
  - `programmatic` TR-2.3: is_available() 正确返回可用性
  - `human-judgement` TR-2.4: 代码风格与现有数据源一致
- **Notes**: 参考 eastmoney.py 的实现方式

## [ ] Task 3: 实现腾讯财经数据源 (TencentDataSource)
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 tencent.py 文件
  - 实现 DataSource 基类接口
  - 支持30分钟K线获取
  - 支持实时行情获取
  - 处理沪市/深市代码格式
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: fetch_klines() 返回至少50条有效K线
  - `programmatic` TR-3.2: get_realtime_quote() 返回当前价格
  - `programmatic` TR-3.3: is_available() 正确返回可用性
  - `human-judgement` TR-3.4: 代码风格与现有数据源一致
- **Notes**: 参考 eastmoney.py 的实现方式

## [ ] Task 4: 实现多数据源管理与自动切换
- **Priority**: P0
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 创建 MultiDataSourceManager 类
  - 实现数据源优先级配置
  - 实现自动容错切换机制
  - 添加详细的切换日志
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 按优先级顺序选择可用数据源
  - `programmatic` TR-4.2: 主数据源不可用时自动切换到备用
  - `programmatic` TR-4.3: 切换事件记录到日志
  - `human-judgement` TR-4.4: 接口设计合理，易于使用
- **Notes**: 集成到 datasources/__init__.py

## [ ] Task 5: 更新主程序支持多数据源
- **Priority**: P0
- **Depends On**: Task 1, Task 4
- **Description**: 
  - 更新 main.py 的 create_system 和 TradingSystem
  - 集成 MultiDataSourceManager
  - 更新示例代码
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: use_real_data=True 时使用多数据源机制
  - `programmatic` TR-5.2: 系统能正常初始化和运行
  - `human-judgement` TR-5.3: 更新 README.md 文档
- **Notes**: 更新 run_realtime.py 和 example_real_data.py

## [ ] Task 6: 更新文档与示例
- **Priority**: P1
- **Depends On**: Task 5
- **Description**: 
  - 更新 README.md 说明新数据源
  - 更新使用示例
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-6.1: 文档清晰说明数据源配置
  - `human-judgement` TR-6.2: 提供完整的使用示例
- **Notes**: 确保文档与代码一致
