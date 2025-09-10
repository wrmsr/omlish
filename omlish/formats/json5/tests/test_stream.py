import math

from ..stream import stream_parse_one_value


def parse(s):
    return stream_parse_one_value(s)


def test_comments():
    assert parse('{//comment\n}') == {}
    assert parse('{}//comment') == {}
    assert parse('{/*comment\n** */}') == {}
    assert parse('{"abc": 420//comment\n}') == {'abc': 420}


def test_strings():
    assert parse('"abc"') == 'abc'
    assert parse("'abc'") == 'abc'
    assert parse("""['"',"'"]""") == ['"', "'"]
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f'""") == """\b\f\n\r\t\v\0\x0f"""  # noqa
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\\u2028\\\u2029\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parse("'\u2028\u2029'") == '\u2028\u2029'


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


def test_arrays():
    assert parse('[]') == []
    assert parse('[1]') == [1]
    assert parse('[1,2]') == [1, 2]
    assert parse('[1,[2,3]]') == [1, [2, 3]]
    assert parse('[1,]') == [1]
    assert parse('[1,2,]') == [1, 2]
    assert parse('[1,[2,3,],]') == [1, [2, 3]]
