from ..casing import CAMEL_CASE
from ..casing import LOW_CAMEL_CASE
from ..casing import SNAKE_CASE
from ..casing import STRING_CASINGS
from ..casing import UP_SNAKE_CASE
from ..casing import camel_case
from ..casing import snake_case


def test_casing():
    cl = STRING_CASINGS

    for c in cl:
        assert c.match('FooBarBaz') == (c is CAMEL_CASE)
    assert CAMEL_CASE.split('FooBarBaz') == ['foo', 'bar', 'baz']
    assert CAMEL_CASE.join('foo', 'bar', 'baz') == 'FooBarBaz'

    for c in cl:
        assert c.match('fooBarBaz') == (c is LOW_CAMEL_CASE)
    assert LOW_CAMEL_CASE.split('fooBarBaz') == ['foo', 'bar', 'baz']
    assert LOW_CAMEL_CASE.join('foo', 'bar', 'baz') == 'fooBarBaz'

    for c in cl:
        assert c.match('foo_bar_baz') == (c is SNAKE_CASE)
    assert SNAKE_CASE.split('foo_bar_baz') == ['foo', 'bar', 'baz']
    assert SNAKE_CASE.join('foo', 'bar', 'baz') == 'foo_bar_baz'

    for c in cl:
        assert c.match('FOO_BAR_BAZ') == (c is UP_SNAKE_CASE)
    assert UP_SNAKE_CASE.split('FOO_BAR_BAZ') == ['foo', 'bar', 'baz']
    assert UP_SNAKE_CASE.join('foo', 'bar', 'baz') == 'FOO_BAR_BAZ'


def test_camel_case():
    assert camel_case('some', 'class') == 'SomeClass'


def test_snake_case():
    assert snake_case('abc') == 'abc'
    assert snake_case('abc', 'def') == 'abc_def'
    assert snake_case('abc', 'def', 'g') == 'abc_def_g'
    assert snake_case('abc', 'def', 'g', 'h') == 'abc_def_g_h'
    assert snake_case('') == ''
