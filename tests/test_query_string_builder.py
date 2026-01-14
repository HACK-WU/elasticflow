"""QueryStringBuilder 单元测试."""

import pytest

from elasticflow import (
    GroupRelation,
    LogicOperator,
    QueryStringBuilder,
    QueryStringOperator,
)
from elasticflow.exceptions import UnsupportedOperatorError


class TestQueryStringBuilder:
    """QueryStringBuilder 测试类."""

    def test_single_equal_filter(self):
        """测试单个等于条件."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.EQUAL, ["error"])
        result = builder.build()
        assert result == 'status: "error"'

    def test_multiple_equal_values(self):
        """测试多个等于值."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.EQUAL, ["error", "warning"])
        result = builder.build()
        assert result == 'status: ("error" OR "warning")'

    def test_include_filter(self):
        """测试包含条件."""
        builder = QueryStringBuilder()
        builder.add_filter("message", QueryStringOperator.INCLUDE, ["timeout"])
        result = builder.build()
        assert result == "message: *timeout*"

    def test_gte_filter(self):
        """测试大于等于条件."""
        builder = QueryStringBuilder()
        builder.add_filter("level", QueryStringOperator.GTE, [3])
        result = builder.build()
        assert result == "level: >=3"

    def test_between_filter(self):
        """测试范围条件."""
        builder = QueryStringBuilder()
        builder.add_filter("age", QueryStringOperator.BETWEEN, [18, 60])
        result = builder.build()
        assert result == "age: [18 TO 60]"

    def test_exists_filter(self):
        """测试字段存在条件."""
        builder = QueryStringBuilder()
        builder.add_filter("field1", QueryStringOperator.EXISTS, [])
        result = builder.build()
        assert result == "field1: *"

    def test_not_exists_filter(self):
        """测试字段不存在条件."""
        builder = QueryStringBuilder()
        builder.add_filter("field1", QueryStringOperator.NOT_EXISTS, [])
        result = builder.build()
        assert result == "NOT field1: *"

    def test_multiple_filters_and(self):
        """测试多个条件 AND 组合."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.EQUAL, ["error"])
        builder.add_filter("level", QueryStringOperator.GTE, [3])
        result = builder.build()
        assert result == 'status: "error" AND level: >=3'

    def test_multiple_filters_or(self):
        """测试多个条件 OR 组合."""
        builder = QueryStringBuilder(logic_operator=LogicOperator.OR)
        builder.add_filter("status", QueryStringOperator.EQUAL, ["error"])
        builder.add_filter("level", QueryStringOperator.GTE, [3])
        result = builder.build()
        assert result == 'status: "error" OR level: >=3'

    def test_group_relation_and(self):
        """测试多值 AND 关系."""
        builder = QueryStringBuilder()
        builder.add_filter(
            "tag",
            QueryStringOperator.EQUAL,
            ["tag1", "tag2"],
            group_relation=GroupRelation.AND,
        )
        result = builder.build()
        assert result == 'tag: ("tag1" AND "tag2")'

    def test_escape_special_characters(self):
        """测试特殊字符转义."""
        builder = QueryStringBuilder()
        builder.add_filter("message", QueryStringOperator.INCLUDE, ["error: test"])
        result = builder.build()
        assert "error\\:\\ test" in result

    def test_add_raw_query(self):
        """测试添加原生 Query String."""
        builder = QueryStringBuilder()
        builder.add_raw("status: error AND level: >=3")
        result = builder.build()
        assert result == "(status: error AND level: >=3)"

    def test_add_raw_with_filter(self):
        """测试原生 Query String 与过滤条件组合."""
        builder = QueryStringBuilder()
        builder.add_filter("app", QueryStringOperator.EQUAL, ["myapp"])
        builder.add_raw("status: error OR level: >=3")
        result = builder.build()
        assert result == 'app: "myapp" AND (status: error OR level: >=3)'

    def test_add_raw_empty_ignored(self):
        """测试空原生 Query String 被忽略."""
        builder = QueryStringBuilder()
        builder.add_raw("")
        builder.add_raw(None)
        builder.add_raw("   ")
        result = builder.build()
        assert result == ""

    def test_operator_mapping(self):
        """测试操作符映射."""
        operator_mapping = {
            "eq": QueryStringOperator.EQUAL,
            "contains": QueryStringOperator.INCLUDE,
        }
        builder = QueryStringBuilder(operator_mapping=operator_mapping)
        builder.add_filter("status", "eq", ["error"])
        result = builder.build()
        assert result == 'status: "error"'

    def test_chain_calls(self):
        """测试链式调用."""
        builder = QueryStringBuilder()
        result = (
            builder.add_filter("status", QueryStringOperator.EQUAL, ["error"])
            .add_filter("level", QueryStringOperator.GTE, [3])
            .build()
        )
        assert 'status: "error"' in result
        assert "level: >=3" in result

    def test_clear_filters(self):
        """测试清空过滤条件."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.EQUAL, ["error"])
        builder.clear()
        result = builder.build()
        assert result == ""

    def test_unsupported_operator(self):
        """测试不支持的操作符."""
        builder = QueryStringBuilder()
        builder._filters.append(
            {
                "field": "test",
                "operator": "invalid_op",
                "values": ["value"],
                "group_relation": GroupRelation.OR,
            }
        )
        with pytest.raises(UnsupportedOperatorError):
            builder.build()

    def test_between_insufficient_values(self):
        """测试 BETWEEN 操作符值不足."""
        builder = QueryStringBuilder()
        builder.add_filter("age", QueryStringOperator.BETWEEN, [18])
        with pytest.raises(ValueError, match="BETWEEN operator requires 2 values"):
            builder.build()

    def test_regex_filter(self):
        """测试正则表达式条件."""
        builder = QueryStringBuilder()
        builder.add_filter("email", QueryStringOperator.REG, [".*@example\\.com"])
        result = builder.build()
        assert result == "email: /.*@example\\.com/"

    def test_not_regex_filter(self):
        """测试非正则表达式条件."""
        builder = QueryStringBuilder()
        builder.add_filter("email", QueryStringOperator.NREG, [".*@test\\.com"])
        result = builder.build()
        assert result == "NOT email: /.*@test\\.com/"

    def test_not_equal_filter(self):
        """测试不等于条件."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.NOT_EQUAL, ["error"])
        result = builder.build()
        assert result == 'NOT status: "error"'

    def test_not_include_filter(self):
        """测试不包含条件."""
        builder = QueryStringBuilder()
        builder.add_filter("message", QueryStringOperator.NOT_INCLUDE, ["timeout"])
        result = builder.build()
        assert result == "NOT message: *timeout*"

    def test_gt_filter(self):
        """测试大于条件."""
        builder = QueryStringBuilder()
        builder.add_filter("level", QueryStringOperator.GT, [5])
        result = builder.build()
        assert result == "level: >5"

    def test_lt_filter(self):
        """测试小于条件."""
        builder = QueryStringBuilder()
        builder.add_filter("level", QueryStringOperator.LT, [10])
        result = builder.build()
        assert result == "level: <10"

    def test_lte_filter(self):
        """测试小于等于条件."""
        builder = QueryStringBuilder()
        builder.add_filter("level", QueryStringOperator.LTE, [3])
        result = builder.build()
        assert result == "level: <=3"

    def test_add_filter_single_value(self):
        """测试添加单个值（非列表）."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.EQUAL, "error")
        result = builder.build()
        assert result == 'status: "error"'

    def test_operator_mapping_fallback_to_equal(self):
        """测试操作符映射未匹配时回退到 EQUAL."""
        operator_mapping = {"eq": QueryStringOperator.EQUAL}
        builder = QueryStringBuilder(operator_mapping=operator_mapping)
        builder.add_filter("status", "unknown_op", ["error"])
        result = builder.build()
        assert result == 'status: "error"'

    def test_include_empty_after_strip(self):
        """测试 INCLUDE 值去除通配符后为空."""
        builder = QueryStringBuilder()
        builder.add_filter("message", QueryStringOperator.INCLUDE, ["***"])
        result = builder.build()
        assert result == ""

    def test_include_multiple_values(self):
        """测试多个 INCLUDE 值."""
        builder = QueryStringBuilder()
        builder.add_filter("message", QueryStringOperator.INCLUDE, ["error", "warning"])
        result = builder.build()
        assert result == "message: (*error* OR *warning*)"

    def test_empty_values_list(self):
        """测试空值列表."""
        builder = QueryStringBuilder()
        builder.add_filter("status", QueryStringOperator.EQUAL, [])
        result = builder.build()
        assert result == ""

    def test_build_empty(self):
        """测试无条件时构建空结果."""
        builder = QueryStringBuilder()
        result = builder.build()
        assert result == ""

    def test_equal_with_quotes(self):
        """测试 EQUAL 值包含双引号转义."""
        builder = QueryStringBuilder()
        builder.add_filter("message", QueryStringOperator.EQUAL, ['say "hello"'])
        result = builder.build()
        assert result == 'message: "say \\"hello\\""'

    def test_multiple_raw_queries(self):
        """测试多个原生查询."""
        builder = QueryStringBuilder()
        builder.add_raw("status: error")
        builder.add_raw("level: >=3")
        result = builder.build()
        assert result == "(status: error) AND (level: >=3)"

    def test_multiple_raw_queries_or(self):
        """测试多个原生查询 OR 组合."""
        builder = QueryStringBuilder(logic_operator=LogicOperator.OR)
        builder.add_raw("status: error")
        builder.add_raw("level: >=3")
        result = builder.build()
        assert result == "(status: error) OR (level: >=3)"


class TestQueryStringBuilderWithQ:
    """QueryStringBuilder 与 Q 对象集成测试."""

    def test_add_q_simple(self):
        """测试添加简单 Q 对象."""
        from elasticflow.core.query import Q

        builder = QueryStringBuilder()
        builder.add_q(Q(status__equal="error"))
        result = builder.build()
        assert result == '(status: "error")'

    def test_add_q_with_filter(self):
        """测试 Q 对象与 filter 组合."""
        from elasticflow.core.query import Q

        builder = QueryStringBuilder()
        builder.add_filter("app", QueryStringOperator.EQUAL, ["myapp"])
        builder.add_q(Q(status__equal="error"))
        result = builder.build()
        assert result == 'app: "myapp" AND (status: "error")'

    def test_add_q_complex(self):
        """测试添加复杂 Q 对象."""
        from elasticflow.core.query import Q

        builder = QueryStringBuilder()
        builder.add_q(Q(status__equal="error") | Q(level__gte=3))
        result = builder.build()
        assert "status" in result
        assert "level" in result
        assert "OR" in result

    def test_add_q_empty(self):
        """测试添加空 Q 对象."""
        from elasticflow.core.query import Q

        builder = QueryStringBuilder()
        builder.add_q(Q())
        result = builder.build()
        assert result == ""

    def test_add_q_none(self):
        """测试添加 None Q 对象."""
        builder = QueryStringBuilder()
        builder.add_q(None)
        result = builder.build()
        assert result == ""

    def test_add_multiple_q(self):
        """测试添加多个 Q 对象."""
        from elasticflow.core.query import Q

        builder = QueryStringBuilder()
        builder.add_q(Q(status__equal="error"))
        builder.add_q(Q(level__gte=3))
        result = builder.build()
        assert '(status: "error")' in result
        assert "(level: >=3)" in result
        assert "AND" in result
