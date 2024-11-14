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
