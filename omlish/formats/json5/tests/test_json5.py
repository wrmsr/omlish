# MIT License
#
# Copyright (c) 2012-2018 Aseem Kishore, and others.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# https://github.com/json5/json5/blob/32bb2cdae4864b2ac80a6d9b4045efc4cc54f47a/test/parse.js
import math

import pytest

from .. import parsing
from ..errors import Json5Error


def test_empty():
    for s in ['', ' ', '\n \t ']:
        with pytest.raises(Json5Error):
            parsing.parse(s)


def test_objects():
    assert parsing.parse('{"a":1}') == {'a': 1}
    assert parsing.parse("{'a':1}") == {'a': 1}
    assert parsing.parse('{a:1}') == {'a': 1}
    assert parsing.parse('{$_:1,_$:2,a\u200C:3}') == {'$_': 1, '_$': 2, 'a\u200C': 3}
    assert parsing.parse('{ùńîċõďë:9}') == {'ùńîċõďë': 9}
    assert parsing.parse('{\\u0061\\u0062:1,\\u0024\\u005F:2,\\u005F\\u0024:3}') == {'ab': 1, '$_': 2, '_$': 3}
    assert parsing.parse('{abc:1,def:2}') == {'abc': 1, 'def': 2}
    assert parsing.parse('{a:{b:2}}') == {'a': {'b': 2}}


def test_arrays():
    assert parsing.parse('[]') == []
    assert parsing.parse('[1]') == [1]
    assert parsing.parse('[1,2]') == [1, 2]
    assert parsing.parse('[1,[2,3]]') == [1, [2, 3]]


def test_nulls():
    assert parsing.parse('null') is None


def test_booleans():
    assert parsing.parse('true') is True
    assert parsing.parse('false') is False


def test_numbers():
    assert parsing.parse('[0,0.,0e0]') == [0, 0, 0]
    assert parsing.parse('[1,23,456,7890]') == [1, 23, 456, 7890]
    assert parsing.parse('[-1,+2,-.1,-0]') == [-1, +2, -0.1, -0]
    assert parsing.parse('[.1,.23]') == [0.1, 0.23]
    assert parsing.parse('[1.0,1.23]') == [1, 1.23]
    assert parsing.parse('[1e0,1e1,1e01,1.e0,1.1e0,1e-1,1e+1]') == [1, 10, 10, 1, 1.1, 0.1, 10]
    assert parsing.parse('[0x1,0x10,0xff,0xFF]') == [1, 16, 255, 255]
    assert parsing.parse('[Infinity,-Infinity]') == [float('inf'), -float('inf')]
    assert math.isnan(parsing.parse('NaN'))
    assert math.isnan(parsing.parse('-NaN'))
    assert parsing.parse('1') == 1
    assert parsing.parse('+1.23e100') == 1.23e100
    assert parsing.parse('0x1') == 0x1
    assert parsing.parse('-0x0123456789abcdefABCDEF') == -0x0123456789abcdefABCDEF


def test_strings():
    assert parsing.parse('"abc"') == 'abc'
    assert parsing.parse("'abc'") == 'abc'
    assert parsing.parse("""['"',"'"]""") == ['"', "'"]
    assert parsing.parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f'""") == """\b\f\n\r\t\v\0\x0f"""  # noqa
    assert parsing.parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parsing.parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\\u2028\\\u2029\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parsing.parse("'\u2028\u2029'") == '\u2028\u2029'


def test_strings2():
    parsing.parse('"' + (  # noqa
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
    assert parsing.parse('{//comment\n}') == {}
    assert parsing.parse('{}//comment') == {}
    assert parsing.parse('{/*comment\n** */}') == {}


def test_whitespace():
    assert parsing.parse('{\t\v\f \u00A0\uFEFF\n\r\u2028\u2029\u2003}') == {}
