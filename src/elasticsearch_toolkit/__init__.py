"""ES Query Toolkit - Elasticsearch Query Building and Transformation Toolkit.

这是一个用于简化 Elasticsearch 查询构建和转换的 Python 库。

主要功能:
    - QueryStringBuilder: 构建 Query String 查询
    - DslQueryBuilder: 构建完整的 ES DSL 查询
    - QueryStringTransformer: 转换和处理 Query String

使用示例:
    from elasticsearch_toolkit import QueryStringBuilder, QueryStringOperator

    builder = QueryStringBuilder()
    builder.add_filter("status", QueryStringOperator.EQUAL, ["error"])
    query_string = builder.build()
"""

__version__ = "0.3.0"

# 导出构建器
from elasticsearch_toolkit.builders import DslQueryBuilder, QueryStringBuilder

# 导出核心组件
from elasticsearch_toolkit.core import (
    ConditionItem,
    ConditionParser,
    DefaultConditionParser,
    FieldMapper,
    GroupRelation,
    LogicOperator,
    Q,
    QueryField,
    QueryStringOperator,
    escape_query_string,
)

# 导出异常
from elasticsearch_toolkit.exceptions import (
    ConditionParseError,
    EsQueryToolkitError,
    QueryStringParseError,
    UnsupportedOperatorError,
)

# 导出转换器
from elasticsearch_toolkit.transformers import QueryStringTransformer

__all__ = [
    # 版本
    "__version__",
    # 构建器
    "QueryStringBuilder",
    "DslQueryBuilder",
    # 操作符和枚举
    "QueryStringOperator",
    "LogicOperator",
    "GroupRelation",
    # 核心组件
    "QueryField",
    "FieldMapper",
    "ConditionItem",
    "ConditionParser",
    "DefaultConditionParser",
    "Q",
    "escape_query_string",
    # 异常
    "EsQueryToolkitError",
    "QueryStringParseError",
    "ConditionParseError",
    "UnsupportedOperatorError",
    # 转换器
    "QueryStringTransformer",
]
