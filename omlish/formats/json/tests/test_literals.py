from ..literals import encode_string
from ..literals import encode_string_ascii
from ..literals import try_parse_number
from ..literals import try_parse_string


def test_parse_string():
    assert try_parse_string('"foo"') == ('foo', 5)
    assert try_parse_string('"foo" bar') == ('foo', 5)
    assert try_parse_string('foo"') is None


def test_parse_number():
    assert try_parse_number('5') == (5, 1)
    assert try_parse_number('5 foo') == (5, 1)
    assert try_parse_number('51') == (51, 2)
    assert try_parse_number('51 foo') == (51, 2)
    assert try_parse_number('5.1') == (5.1, 3)
    assert try_parse_number('x5') is None


def test_encode_string():
    assert encode_string('foo') == '"foo"'
    assert encode_string('f\noo') == '"f\\noo"'
    assert encode_string('f\noo☃') == '"f\\noo☃"'


def test_encode_string_ascii():
    assert encode_string_ascii('foo') == '"foo"'
    assert encode_string_ascii('f\noo') == '"f\\noo"'
    assert encode_string_ascii('f\noo☃') == '"f\\noo\\u2603"'
