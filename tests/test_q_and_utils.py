"""Q 对象和 escape_query_string 函数单元测试."""

import pytest

from elasticflow import Q, QueryStringOperator, escape_query_string
from elasticflow.exceptions import UnsupportedOperatorError


class TestEscapeQueryString:
    """escape_query_string 函数测试类."""

    def test_escape_space(self):
        """测试空格转义."""
        result = escape_query_string("hello world")
        assert result == "hello\\ world"

    def test_escape_plus(self):
        """测试加号转义."""
        result = escape_query_string("hello+world")
        assert result == "hello\\+world"

    def test_escape_minus(self):
        """测试减号转义."""
        result = escape_query_string("hello-world")
        assert result == "hello\\-world"

    def test_escape_colon(self):
        """测试冒号转义."""
        result = escape_query_string("key:value")
        assert result == "key\\:value"

    def test_escape_asterisk(self):
        """测试星号转义."""
        result = escape_query_string("test*")
        assert result == "test\\*"

    def test_escape_question_mark(self):
        """测试问号转义."""
        result = escape_query_string("test?")
        assert result == "test\\?"

    def test_escape_parentheses(self):
        """测试括号转义."""
        result = escape_query_string("(test)")
        assert result == "\\(test\\)"

    def test_escape_brackets(self):
        """测试方括号转义."""
        result = escape_query_string("[test]")
        assert result == "\\[test\\]"

    def test_escape_braces(self):
        """测试花括号转义."""
        result = escape_query_string("{test}")
        assert result == "\\{test\\}"

    def test_escape_double_quote(self):
        """测试双引号转义."""
        result = escape_query_string('"test"')
        assert result == '\\"test\\"'

    def test_escape_backslash(self):
        """测试反斜杠转义."""
        result = escape_query_string("test\\path")
        assert result == "test\\\\path"

    def test_escape_multiple_chars(self):
        """测试多个特殊字符转义."""
        result = escape_query_string("key: value + test")
        assert result == "key\\:\\ value\\ \\+\\ test"

    def test_no_double_escape(self):
        """测试避免双重转义."""
        result = escape_query_string("test\\:value")
        assert result == "test\\:value"

    def test_escape_many_mode(self):
        """测试批量转义模式."""
        result = escape_query_string(["a+b", "c:d"], many=True)
        assert result == ["a\\+b", "c\\:d"]

    def test_escape_many_single_string(self):
        """测试批量模式下单个字符串."""
        result = escape_query_string("a+b", many=True)
        assert result == ["a\\+b"]

    def test_escape_non_string(self):
        """测试非字符串值."""
        result = escape_query_string(None)
        assert result is None


class TestQ:
    """Q 对象测试类."""

    def test_explicit_params(self):
        """测试显式参数方式."""
        q = Q(field="status", operator=QueryStringOperator.EQUAL, value="error")
        result = q.build()
        assert result == 'status: "error"'

    def test_django_style_equal(self):
        """测试 Django 风格等于语法."""
        q = Q(status__equal="error")
        result = q.build()
        assert result == 'status: "error"'

    def test_django_style_default_equal(self):
        """测试 Django 风格默认等于."""
        q = Q(status="error")
        result = q.build()
        assert result == 'status: "error"'

    def test_django_style_gte(self):
        """测试 Django 风格大于等于."""
        q = Q(level__gte=3)
        result = q.build()
        assert result == "level: >=3"

    def test_django_style_include(self):
        """测试 Django 风格包含."""
        q = Q(message__include="timeout")
        result = q.build()
        assert result == "message: *timeout*"

    def test_django_style_nested_field(self):
        """测试 Django 风格嵌套字段."""
        q = Q(log__level__gte=3)
        result = q.build()
        assert result == "log.level: >=3"

    def test_and_operator(self):
        """测试 & 运算符."""
        q1 = Q(status__equal="error")
        q2 = Q(level__gte=3)
        combined = q1 & q2
        result = combined.build()
        assert result == 'status: "error" AND level: >=3'

    def test_or_operator(self):
        """测试 | 运算符."""
        q1 = Q(status__equal="error")
        q2 = Q(status__equal="warning")
        combined = q1 | q2
        result = combined.build()
        assert 'status: "error"' in result
        assert 'status: "warning"' in result
        assert "OR" in result

    def test_not_operator(self):
        """测试 ~ 运算符."""
        q = Q(status__equal="error")
        negated = ~q
        result = negated.build()
        assert result == 'NOT (status: "error")'

    def test_complex_combination(self):
        """测试复杂组合."""
        q = (Q(status__equal="error") | Q(status__equal="warning")) & Q(level__gte=3)
        result = q.build()
        assert "OR" in result
        assert "AND" in result
        assert 'status: "error"' in result
        assert 'status: "warning"' in result
        assert "level: >=3" in result

    def test_empty_q(self):
        """测试空 Q 对象."""
        q = Q()
        result = q.build()
        assert result == ""
        assert q.is_empty()

    def test_q_bool(self):
        """测试 Q 对象布尔值."""
        q_empty = Q()
        q_full = Q(status="error")
        assert not q_empty
        assert q_full

    def test_exists_operator(self):
        """测试 EXISTS 操作符."""
        q = Q(field__exists=True)
        result = q.build()
        assert result == "field: *"

    def test_not_exists_operator(self):
        """测试 NOT_EXISTS 操作符."""
        q = Q(field__not_exists=True)
        result = q.build()
        assert result == "NOT field: *"

    def test_regex_operator(self):
        """测试正则表达式操作符."""
        q = Q(email__regex=".*@example\\.com")
        result = q.build()
        assert result == "email: /.*@example\\.com/"

    def test_unsupported_operator(self):
        """测试不支持的操作符."""
        q = Q()
        q._children.append({"field": "test", "operator": "invalid", "value": "value"})
        with pytest.raises(UnsupportedOperatorError):
            q.build()

    def test_and_with_empty_q(self):
        """测试与空 Q 对象进行 AND."""
        q1 = Q(status="error")
        q2 = Q()
        combined = q1 & q2
        result = combined.build()
        assert result == 'status: "error"'

    def test_or_with_empty_q(self):
        """测试与空 Q 对象进行 OR."""
        q1 = Q()
        q2 = Q(status="error")
        combined = q1 | q2
        result = combined.build()
        assert result == 'status: "error"'

    def test_repr(self):
        """测试 Q 对象的字符串表示."""
        q = Q(status="error")
        repr_str = repr(q)
        assert "Q:" in repr_str
        assert "status" in repr_str

    def test_escape_in_include(self):
        """测试 INCLUDE 操作符中的转义."""
        q = Q(message__include="error: test")
        result = q.build()
        assert "error\\:\\ test" in result

    def test_escape_in_equal(self):
        """测试 EQUAL 操作符中双引号转义."""
        q = Q(message='say "hello"')
        result = q.build()
        assert 'message: "say \\"hello\\""' == result
