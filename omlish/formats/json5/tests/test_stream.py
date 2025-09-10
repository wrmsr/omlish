import math

import pytest

from ..stream import stream_parse_one_value


def parse(s):
    return stream_parse_one_value(s)


def test_empty():
    for s in ['', ' ', '\n \t ']:
        with pytest.raises(Exception):  # noqa
            parse(s)


def test_objects():
    assert parse('{"a":1}') == {'a': 1}
    assert parse('{"a":1,}') == {'a': 1}
    assert parse("{'a':1}") == {'a': 1}
    assert parse('{a:1}') == {'a': 1}
    assert parse('{$_:1,_$:2,a\u200C:3}') == {'$_': 1, '_$': 2, 'a\u200C': 3}
    assert parse('{ùńîċõďë:9}') == {'ùńîċõďë': 9}
    assert parse('{\\u0061\\u0062:1,\\u0024\\u005F:2,\\u005F\\u0024:3}') == {'ab': 1, '$_': 2, '_$': 3}
    assert parse('{abc:1,def:2}') == {'abc': 1, 'def': 2}
    assert parse('{a:{b:2}}') == {'a': {'b': 2}}


def test_arrays():
    assert parse('[]') == []
    assert parse('[1]') == [1]
    assert parse('[1,2]') == [1, 2]
    assert parse('[1,[2,3]]') == [1, [2, 3]]
    assert parse('[1,]') == [1]
    assert parse('[1,2,]') == [1, 2]
    assert parse('[1,[2,3,],]') == [1, [2, 3]]


def test_nulls():
    assert parse('null') is None


def test_booleans():
    assert parse('true') is True
    assert parse('false') is False


def test_numbers():
    assert parse('[0,0.,0e0]') == [0, 0, 0]
    assert parse('[1,23,456,7890]') == [1, 23, 456, 7890]
    assert parse('[-1,+2,-.1,-0]') == [-1, +2, -0.1, -0]
    assert parse('[.1,.23]') == [0.1, 0.23]
    assert parse('[1.0,1.23]') == [1, 1.23]
    assert parse('[1e0,1e1,1e01,1.e0,1.1e0,1e-1,1e+1]') == [1, 10, 10, 1, 1.1, 0.1, 10]
    assert parse('[0x1,0x10,0xff,0xFF]') == [1, 16, 255, 255]
    assert parse('[Infinity,-Infinity]') == [float('inf'), -float('inf')]
    assert math.isnan(parse('NaN'))
    assert math.isnan(parse('-NaN'))
    assert parse('1') == 1
    assert parse('+1.23e100') == 1.23e100
    assert parse('0x1') == 0x1
    assert parse('-0x0123456789abcdefABCDEF') == -0x0123456789abcdefABCDEF


def test_strings():
    assert parse('"abc"') == 'abc'
    assert parse("'abc'") == 'abc'
    assert parse("""['"',"'"]""") == ['"', "'"]
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f'""") == """\b\f\n\r\t\v\0\x0f"""  # noqa
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\\u2028\\\u2029\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parse("'\u2028\u2029'") == '\u2028\u2029'


def test_strings2():
    parse('"' + (  # noqa
        '\\b'
        '\\f'
        '\\n'
        '\\r'
        '\\t'
        '\\v'
        '\\0'
        '\\x0f'
        '\\u01fF'
        '\\\n'
        '\\\r\n'
        '\\\r'
        '\\\u2028'
        '\\\u2029'
        '\\a'
        '\\\''
        '\\"'
    ) + '"')


def test_comments():
    assert parse('{//comment\n}') == {}
    assert parse('{}//comment') == {}
    assert parse('{/*comment\n** */}') == {}


def test_whitespace():
    assert parse('{\t\v\f \u00A0\uFEFF\n\r\u2028\u2029\u2003}') == {}
