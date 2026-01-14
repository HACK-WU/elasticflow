# Changelog

本文档记录了 ElasticFlow 项目的所有重要变更。

## [v0.3.0] - 2026-01-14

### 重构 QueryStringBuilder
- 移除 `is_wildcard` 参数，所有值自动转义
- 优化 INCLUDE/NOT_INCLUDE 操作符模板格式
- 新增 `add_raw()` 方法支持原生 Query String
- 新增 `add_q()` 方法支持 Q 对象查询

### 实现 Q 对象
- 支持 Django 风格字段查找语法
- 支持逻辑运算符（`&`, `|`, `~`）
- 支持嵌套查询组合

### 其他改进
- 添加 `escape_query_string()` 转义工具函数
- 完整的单元测试覆盖（93%）

## [v0.2.0] - 2026-01-13

### 新增功能
- 添加 QueryStringTransformer（Query String 转换器）
- 支持字段名映射和值翻译
- 完整的单元测试覆盖（93%）

## [v0.1.0] - 2026-01-13

### 初始版本
- QueryStringBuilder 实现
- DslQueryBuilder 实现
- 核心模块和操作符定义
