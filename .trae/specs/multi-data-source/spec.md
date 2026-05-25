# 333交易系统 - 多数据源支持 - Product Requirement Document

## Overview
- **Summary**: 移除模拟数据源，新增新浪财经和腾讯财经作为备用数据源，建立多数据源切换与容错机制
- **Purpose**: 提升系统稳定性，在东方财富数据源不可用时自动切换到备用数据源
- **Target Users**: 量化交易者、系统用户

## Goals
- 移除模拟数据源（mock）
- 新增新浪财经数据源
- 新增腾讯财经数据源
- 实现多数据源自动切换与容错机制
- 更新系统集成支持多数据源配置

## Non-Goals (Out of Scope)
- 不实现券商实盘交易API对接
- 不实现Web监控界面（后续版本）
- 不实现移动端通知（后续版本）

## Background & Context
- 当前系统已有东方财富数据源
- 模拟数据源仅用于测试，生产环境不需要
- 需要备用数据源保证系统高可用性
- 新浪财经和腾讯财经提供免费的国内行情数据

## Functional Requirements
- **FR-1**: 移除模拟数据源（MockDataSource）
- **FR-2**: 实现新浪财经数据源（SinaDataSource）
- **FR-3**: 实现腾讯财经数据源（TencentDataSource）
- **FR-4**: 实现多数据源自动切换机制
- **FR-5**: 实现数据源优先级配置
- **FR-6**: 更新主程序支持多数据源

## Non-Functional Requirements
- **NFR-1**: 数据源切换延迟不超过5秒
- **NFR-2**: 数据源可用性检查超时不超过3秒
- **NFR-3**: 日志记录所有数据源切换事件

## Constraints
- **Technical**: 必须基于 Python 实现
- **Business**: 所有数据源必须使用免费API，无需API Key
- **Dependencies**: requests、json

## Assumptions
- 新浪财经API稳定可用
- 腾讯财经API稳定可用
- 所有数据源支持30分钟K线和实时行情
- 代码格式遵循现有代码风格

## Acceptance Criteria

### AC-1: 移除模拟数据源
- **Given**: 系统初始化时
- **When**: 创建数据源实例
- **Then**: 模拟数据源不再被使用或引用
- **Verification**: `programmatic`
- **Notes**: 删除相关代码，确保没有遗留引用

### AC-2: 新浪财经数据源可正常获取K线
- **Given**: 创建新浪财经数据源实例
- **When**: 调用 fetch_klines()
- **Then**: 返回有效的K线列表（至少包含最近50条）
- **Verification**: `programmatic`

### AC-3: 新浪财经数据源可获取实时行情
- **Given**: 创建新浪财经数据源实例
- **When**: 调用 get_realtime_quote()
- **Then**: 返回包含当前价格的实时行情数据
- **Verification**: `programmatic`

### AC-4: 腾讯财经数据源可正常获取K线
- **Given**: 创建腾讯财经数据源实例
- **When**: 调用 fetch_klines()
- **Then**: 返回有效的K线列表（至少包含最近50条）
- **Verification**: `programmatic`

### AC-5: 腾讯财经数据源可获取实时行情
- **Given**: 创建腾讯财经数据源实例
- **When**: 调用 get_realtime_quote()
- **Then**: 返回包含当前价格的实时行情数据
- **Verification**: `programmatic`

### AC-6: 多数据源自动切换
- **Given**: 系统配置多数据源优先级
- **When**: 主数据源不可用时
- **Then**: 系统自动切换到下一个可用的备用数据源
- **Verification**: `programmatic`

### AC-7: 数据源优先级配置
- **Given**: 系统初始化时
- **When**: 指定数据源优先级列表
- **Then**: 系统按优先级顺序尝试数据源
- **Verification**: `programmatic`

### AC-8: 系统集成更新
- **Given**: 创建 TradingSystem 实例
- **When**: use_real_data=True
- **Then**: 使用多数据源机制而非单一数据源
- **Verification**: `programmatic`

## Open Questions
- [ ] 暂无
