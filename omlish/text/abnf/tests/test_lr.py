# @omlish-precheck-allow-any-unicode
"""Tests for the LALR(1) engine: table construction, conflict rejection, the driver, and rule-level trees."""
import pytest

from .... import check
from ..engines.lr import LrEngine
from ..errors import AbnfEngineCapabilityError
from ..errors import AbnfLrConflictError
from ..errors import AbnfUnexpectedTokenError
from ..meta import parse_grammar
from ..ops import RuleRef


##


def _compile(src: str, root: str):
    g = parse_grammar(src, root=root, no_optimize=True)
    return LrEngine().compile(g)


_SKIP_RULES = """
        S = *WS
        R = 1*WS
        %token %channel(space) WS = 1*(SP / HTAB / CR / LF)
"""


##
# classic grammars


def test_left_recursive_expression_grammar():
    # The canonical LR strength: left recursion, impossible for the recursive-descent interpreter.
    cg = _compile(
        """
        expr   = expr S "+" S term | term
        term   = term S "*" S factor | factor
        factor = "(" S expr S ")" | num
        %token num = 1*DIGIT
        """ + _SKIP_RULES,
        'expr',
    )

    m = check.not_none(cg.parse('1 + 2 * (3 + 4)', complete=True))
    assert (m.start, m.end) == (0, 15)

    def shape(x):
        return (check.isinstance(x.op, RuleRef).name, [shape(c) for c in x.children])

    assert shape(m) == (
        'expr', [
            ('expr', [('term', [('factor', [('num', [])])])]),
            ('term', [
                ('term', [('factor', [('num', [])])]),
                ('factor', [
                    ('expr', [
                        ('expr', [('term', [('factor', [('num', [])])])]),
                        ('term', [('factor', [('num', [])])]),
                    ]),
                ]),
            ]),
        ],
    )


def test_ambiguous_grammar_rejected_with_report():
    src = """
        e = e S "+" S e | num
        %token num = 1*DIGIT
    """ + _SKIP_RULES

    with pytest.raises(AbnfLrConflictError) as ei:
        _compile(src, 'e')

    msg = str(ei.value)
    assert 'not LALR(1)' in msg
    assert 'shift' in msg
    assert 'reduce' in msg
    assert '•' in msg  # the state's item set is rendered


def test_deep_left_recursion_constant_stack():
    cg = _compile(
        """
        list = list S "," S num | num
        %token num = 1*DIGIT
        """ + _SKIP_RULES,
        'list',
    )

    src = ', '.join(str(i) for i in range(2000))
    m = check.not_none(cg.parse(src, complete=True))
    assert m.end == len(src)


##
# driver behavior


def test_parse_error_expected_tokens():
    cg = _compile(
        """
        stmt = "set" R name S "=" S num
        %token name = 1*ALPHA
        %token num = 1*DIGIT
        """ + _SKIP_RULES,
        'stmt',
    )

    with pytest.raises(AbnfUnexpectedTokenError) as ei:
        cg.parse('set x = y', complete=True)

    e = ei.value
    assert e.offset == 8
    assert e.expected is not None
    assert 'num' in e.expected
    assert 'line 1' in str(e)


def test_parse_error_unexpected_eof():
    cg = _compile(
        """
        stmt = "set" R name
        %token name = 1*ALPHA
        """ + _SKIP_RULES,
        'stmt',
    )

    with pytest.raises(AbnfUnexpectedTokenError) as ei:
        cg.parse('set ', complete=True)

    assert 'end of input' in str(ei.value)


def test_capability_gating():
    cg = _compile(
        """
        stmt = 1*("a" S)
        """ + _SKIP_RULES,
        'stmt',
    )

    assert not cg.capabilities.all_matches

    with pytest.raises(AbnfEngineCapabilityError):
        list(cg.iter_parse('a'))

    with pytest.raises(AbnfEngineCapabilityError):
        cg.parse('a')  # complete=False unsupported

    with pytest.raises(AbnfEngineCapabilityError):
        cg.parse('a', 'other', complete=True)  # non-compiled root


def test_comment_pickup_via_lex():
    cg = _compile(
        """
        conf = S 1*(stmt S)
        stmt = name S "=" S num
        %token name = 1*ALPHA
        %token num = 1*DIGIT
        SKIP = WS / comment
        S = *SKIP
        %token %channel(comment) comment = "#" *not-eol
        not-eol = %x20-7E
        %token %channel(space) WS = 1*(SP / HTAB / CR / LF)
        """,
        'conf',
    )

    src = 'a = 1 # first\nb = 2 # second\n'
    assert cg.parse(src, complete=True) is not None

    comments = [t.text(src) for t in cg.lex(src) if t.spec.name == 'comment']
    assert comments == ['# first', '# second']


def test_epsilon_reductions():
    cg = _compile(
        """
        stmt = "f" S "(" S [args S] ")"
        args = num *(S "," S num)
        %token num = 1*DIGIT
        """ + _SKIP_RULES,
        'stmt',
    )

    assert cg.parse('f()', complete=True) is not None
    assert cg.parse('f(1)', complete=True) is not None
    m = check.not_none(cg.parse('f( 1 , 2 , 3 )', complete=True))

    [args] = m.children
    assert check.isinstance(args.op, RuleRef).name == 'args'
    assert len(args.children) == 3  # the repeat spine splices flat
