import io
import pytest
import typing as ta

from ..errors import ParseError
from ..parsing import Parser
from ..values import Char
from ..values import List
from ..values import Map
from ..values import Nil
from ..values import Set
from ..values import Symbol
from ..values import Tagged
from ..values import Vector


##


@pytest.fixture
def parse() -> ta.Callable[[str], ta.Any]:
    def _parse(s: str) -> ta.Any:
        return Parser(io.StringIO(s)).parse()
    return _parse


def test_nil(parse):
    assert parse('nil') == Nil()
    with pytest.raises(ParseError):
        parse('nill')
    with pytest.raises(ParseError):
        parse('ni')


def test_boolean(parse):
    assert parse('true') is True
    assert parse('false') is False
    assert parse('True') == Symbol('True')
    assert parse('False') == Symbol('False')


def test_string(parse):
    assert parse('""') == ''
    assert parse('"hello"') == 'hello'
    assert parse('"hello\\nworld"') == 'hello\nworld'
    assert parse('"hello\\tworld"') == 'hello\tworld'
    assert parse('"hello\\\\world"') == 'hello\\world'
    assert parse('"hello\\"world"') == 'hello"world'
    with pytest.raises(ParseError):
        parse('"unclosed')
    with pytest.raises(ParseError):
        parse('"invalid\\escape"')


def test_character(parse):
    assert parse('\\a') == Char('a')
    assert parse('\\b') == Char('b')
    assert parse('\\space') == Char(' ')
    assert parse('\\newline') == Char('\n')
    assert parse('\\tab') == Char('\t')
    assert parse('\\return') == Char('\r')
    with pytest.raises(ParseError):
        parse('\\')


def test_symbol(parse):
    assert parse('abc') == Symbol('abc')
    assert parse('abc/def') == Symbol('def', 'abc')
    assert parse('abc.def') == Symbol('abc.def')
    assert parse('abc_def') == Symbol('abc_def')
    assert parse('abc!def') == Symbol('abc!def')
    assert parse('abc?def') == Symbol('abc?def')
    assert parse('abc$def') == Symbol('abc$def')
    assert parse('abc%def') == Symbol('abc%def')
    assert parse('abc&def') == Symbol('abc&def')
    assert parse('abc=def') == Symbol('abc=def')
    assert parse('abc<def') == Symbol('abc<def')
    assert parse('abc>def') == Symbol('abc>def')


def test_keyword(parse):
    assert parse(':abc') == Symbol('abc')
    assert parse(':abc/def') == Symbol('def', 'abc')
    assert parse(':abc.def') == Symbol('abc.def')


def test_list(parse):
    assert parse('()') == List([])
    assert parse('(1)') == List([1])
    assert parse('(1 2)') == List([1, 2])
    assert parse('(1 \"two\" true)') == List([1, 'two', True])
    with pytest.raises(ParseError):
        parse('(1 2')


def test_vector(parse):
    assert parse('[]') == Vector([])
    assert parse('[1]') == Vector([1])
    assert parse('[1 2]') == Vector([1, 2])
    assert parse('[1 \"two\" true]') == Vector([1, 'two', True])
    with pytest.raises(ParseError):
        parse('[1 2')


def test_set(parse):
    assert parse('#{}') == Set([])
    assert parse('#{1}') == Set([1])
    assert parse('#{1 2}') == Set([1, 2])
    assert parse('#{1 \"two\" true}') == Set([1, 'two', True])
    with pytest.raises(ParseError):
        parse('#{1 2')


def test_map(parse):
    assert parse('{}') == Map([])
    assert parse('{:a 1}') == Map([(Symbol('a'), 1)])
    assert parse('{:a 1, :b 2}') == Map([
        (Symbol('a'), 1),
        (Symbol('b'), 2)
    ])
    # Comma is optional
    assert parse('{:a 1 :b 2}') == Map([
        (Symbol('a'), 1),
        (Symbol('b'), 2)
    ])
    with pytest.raises(ParseError):
        parse('{:a')
    with pytest.raises(ParseError):
        parse('{:a 1')


def test_tagged(parse):
    assert parse('#myapp/Person {:name \"Fred\"}') == Tagged(
        Symbol('Person', 'myapp'),
        Map([(Symbol('name'), 'Fred')])
    )
    assert parse('#inst \"1985-04-12T23:20:50.52Z\"') == Tagged(
        Symbol('inst'),
        '1985-04-12T23:20:50.52Z'
    )
    with pytest.raises(ParseError):
        parse('#myapp/')


@pytest.mark.parametrize('input_str,expected', [
    ('0', 0),
    ('42', 42),
    ('-42', -42),
    ('3.14', 3.14),
    ('-3.14', -3.14),
    ('2.5e3', 2500.0),
    ('2.5E3', 2500.0),
    ('-2.5e3', -2500.0),
    ('-2.5E3', -2500.0),
])
def test_number(parse, input_str, expected):
    assert parse(input_str) == expected


def test_invalid_number(parse):
    with pytest.raises(ParseError):
        parse('12.34.56')


def test_whitespace_and_comments(parse):
    # Whitespace
    assert parse(' 42') == 42
    assert parse('42 ') == 42
    assert parse(' 42 ') == 42
    assert parse('\t42\n') == 42
    
    # Comments
    assert parse(';comment\n42') == 42
    assert parse('42;comment') == 42
    with pytest.raises(ParseError):
        parse('4;comment\n2')
    
    # Commas as whitespace
    assert parse('[1,2,3]') == Vector([1, 2, 3])


def test_nested_structures(parse):
    # Complex nested structure
    edn = """
    {
        :data [
            {:id 1, :tags #{:a :b}}
            {:id 2, :tags #{:b :c}}
        ]
        :meta {
            :count 2
            :source "test"
        }
    }
    """
    expected = Map([
        (Symbol('data'), Vector([
            Map([
                (Symbol('id'), 1),
                (Symbol('tags'), Set([Symbol('a'), Symbol('b')]))
            ]),
            Map([
                (Symbol('id'), 2),
                (Symbol('tags'), Set([Symbol('b'), Symbol('c')]))
            ])
        ])),
        (Symbol('meta'), Map([
            (Symbol('count'), 2),
            (Symbol('source'), 'test')
        ]))
    ])
    assert parse(edn) == expected
