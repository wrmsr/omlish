import pytest

from .. import errors
from .. import ops
from ..grammars import Grammar
from ..grammars import Rule
from ..meta import parse_grammar
from ..positions import format_offset
from ..positions import get_ofs_line_column


##
# positions


def test_get_ofs_line_column():
    s = 'ab\ncd\r\nef'

    assert get_ofs_line_column(s, 0) == (0, 0)
    assert get_ofs_line_column(s, 1) == (0, 1)
    assert get_ofs_line_column(s, 2) == (0, 2)  # the \n itself
    assert get_ofs_line_column(s, 3) == (1, 0)
    assert get_ofs_line_column(s, 5) == (1, 2)  # the \r
    assert get_ofs_line_column(s, 6) == (1, 3)  # the \n
    assert get_ofs_line_column(s, 7) == (2, 0)
    assert get_ofs_line_column(s, 8) == (2, 1)

    # EOF on an unterminated final line stays on that line
    assert get_ofs_line_column(s, 9) == (2, 2)

    # EOF just after a trailing newline is the start of the (virtual) next line
    assert get_ofs_line_column('ab\n', 3) == (1, 0)

    # empty source
    assert get_ofs_line_column('', 0) == (0, 0)

    with pytest.raises(ValueError):  # noqa
        get_ofs_line_column('ab', 3)
    with pytest.raises(ValueError):  # noqa
        get_ofs_line_column('ab', -1)


def test_format_offset():
    assert format_offset('ab\ncd', 4) == 'line 2, column 2'


##
# grammar construction validation


def test_unknown_rule_ref():
    with pytest.raises(errors.AbnfUnknownRuleError) as ei:
        Grammar(
            Rule('root', ops.concat(ops.rule('nope'), ops.literal('x'))),
            root='root',
        )

    assert ei.value.names == {'nope': ('root',)}


def test_unknown_rule_ref_multiple():
    with pytest.raises(errors.AbnfUnknownRuleError) as ei:
        Grammar(
            Rule('a', ops.rule('missing-one')),
            Rule('b', ops.either(ops.rule('missing-one'), ops.rule('missing-two'))),
        )

    assert set(ei.value.names) == {'missing-one', 'missing-two'}
    assert set(ei.value.names['missing-one']) == {'a', 'b'}


def test_rule_refs_case_insensitive():
    # refs resolve case-insensitively, so this must not raise
    g = Grammar(
        Rule('Root', ops.rule('LEAF')),
        Rule('leaf', ops.literal('x')),
        root='ROOT',
    )

    assert g.parse('x') is not None


def test_no_validate():
    g = Grammar(
        Rule('root', ops.rule('nope')),
        root='root',
        no_validate=True,
    )

    assert g is not None


def test_unknown_root():
    with pytest.raises(errors.AbnfUnknownRuleError):
        Grammar(
            Rule('root', ops.literal('x')),
            root='nope',
        )


def test_unknown_parse_root():
    g = Grammar(Rule('root', ops.literal('x')))

    with pytest.raises(errors.AbnfUnknownRuleError):
        g.parse('x', 'nope')


def test_no_root():
    g = Grammar(Rule('root', ops.literal('x')))

    with pytest.raises(errors.AbnfError):
        g.parse('x')


##
# parse errors


def test_incomplete_parse_error():
    g = parse_grammar(
        """
        root = 1*pair
        pair = key "=" value ";"
        key = 1*ALPHA
        value = 1*DIGIT
        """,
        root='root',
    )

    assert g.parse('a=1;b=2;', complete=True) is not None

    with pytest.raises(errors.AbnfIncompleteParseError) as ei:
        g.parse('a=1;b=x;', complete=True)

    e = ei.value
    assert e.source == 'a=1;b=x;'
    assert e.furthest_offset is not None
    assert e.furthest_offset >= 6  # got as far as 'b=' at least
    assert 'line 1' in str(e)


def test_incomplete_parse_error_no_match():
    g = parse_grammar('root = "x"', root='root')

    # complete=True raises even when there is no match at all
    with pytest.raises(errors.AbnfIncompleteParseError) as ei:
        g.parse('y', complete=True)

    assert ei.value.match_end is None

    # without complete, no match is still just None
    assert g.parse('y') is None


def test_incomplete_parse_error_rule_trace():
    g = parse_grammar(
        """
        root = "(" inner ")"
        inner = 1*DIGIT
        """,
        root='root',
    )

    with pytest.raises(errors.AbnfIncompleteParseError) as ei:
        g.parse('(12x)', complete=True)

    tr = ei.value.rule_trace
    assert tr is not None


def test_max_steps_exceeded():
    g = parse_grammar(
        """
        root = 1*(ALPHA / DIGIT)
        """,
        root='root',
    )

    with pytest.raises(errors.AbnfMaxStepsExceededError) as ei:
        g.parse('abcdef' * 10, max_steps=3)

    assert ei.value.steps >= 3


def test_grammar_parse_error_position():
    with pytest.raises(errors.AbnfGrammarParseError) as ei:
        parse_grammar(
            """
            root = "a" &&& "b"
            """,
            root='root',
        )

    assert 'line' in str(ei.value)
