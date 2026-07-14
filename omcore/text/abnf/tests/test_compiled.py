"""
Differential tests: the closure-compiled interpreter must agree exactly with the reference implementation - parse
results, full match trees (compared by render, as compiled rule-ref nodes carry canonical RuleRef instances), iter_parse
span multisets and order, and failure diagnostics.
"""
import os.path

import pytest

from .. import ops
from ..engines.interp import InterpEngine
from ..errors import AbnfIncompleteParseError
from ..grammars import Grammar
from ..grammars import Rule
from ..meta import parse_grammar


##


_COMPILED_ENGINE = InterpEngine()
_REFERENCE_ENGINE = InterpEngine(no_closures=True)


def _assert_engines_agree(g, source, *, root=None):
    cg = _COMPILED_ENGINE.compile(g)
    rg = _REFERENCE_ENGINE.compile(g)

    cms = list(cg.iter_parse(source, root))
    rms = list(rg.iter_parse(source, root))

    assert [(m.start, m.end) for m in cms] == [(m.start, m.end) for m in rms]
    assert [m.render() for m in cms] == [m.render() for m in rms]

    cm = cg.parse(source, root)
    rm = rg.parse(source, root)
    assert (cm is None) == (rm is None)
    if cm is not None and rm is not None:
        assert cm.render() == rm.render()


##


def test_simple_grammars_agree():
    g = parse_grammar(
        """
        root = 1*pair
        pair = key "=" value ";"
        key = 1*ALPHA
        value = 1*DIGIT
        """,
        root='root',
    )

    for src in ['a=1;', 'a=1;b=22;', 'a=1;b=;', '', 'a', '!', 'a=1']:
        _assert_engines_agree(g, src)


def test_nullable_repeat_agree():
    inner = ops.repeat(ops.StringLiteral('a'))  # *"a" - nullable

    for op, srcs in [
        (ops.repeat(2, 2, inner), ['a', '', 'aa', 'aaa']),
        (ops.repeat(1, None, inner), ['', 'a', 'aa']),
    ]:
        g = Grammar(Rule('root', op), root='root')
        for src in srcs:
            _assert_engines_agree(g, src)


def test_bounded_repeat_agree():
    g = parse_grammar(
        """
        root = 2*4"ab" ["!"]
        """,
        root='root',
    )

    for src in ['', 'ab', 'abab', 'ababab', 'abababab', 'ababababab', 'abab!']:
        _assert_engines_agree(g, src)


def test_first_match_either_agree():
    g = parse_grammar(
        """
        root = ("x" | "xy") ["z"]
        """,
        root='root',
    )

    for src in ['x', 'xy', 'xz', 'xyz']:
        _assert_engines_agree(g, src)


def test_case_insensitive_agree():
    g = Grammar(
        Rule('root', ops.concat(
            ops.CaseInsensitiveStringLiteral('Hello'),
            ops.repeat(ops.CaseInsensitiveStringLiteral('ß')),
        )),
        root='root',
    )

    for src in ['hello', 'HELLO', 'HeLLoß', 'helloßß', 'helloss', 'hell']:
        _assert_engines_agree(g, src)


def test_overlapping_alternation_agree():
    g = parse_grammar(
        """
        root = 3*3( "aaa" / "a" )
        """,
        root='root',
    )

    for src in ['aaa', 'aaaaa', 'aaaaaaaaa', 'aa']:
        _assert_engines_agree(g, src)


@pytest.mark.parametrize('optimize', [False, True])
def test_json_corpus_agree(optimize):
    with open(os.path.join(os.path.dirname(__file__), 'json.abnf')) as f:
        g = parse_grammar(f.read(), root='JSON-text', no_optimize=not optimize)

    srcs = [
        '{}',
        '{"a": 1}',
        '{"a": [1, 2.5, -3e4], "b": {"c": true, "d": null}, "e": "x\\ny"}',
        '  [ 1 , 2 ]  ',
        '{"a": }',
        '"lone string"',
    ]

    for src in srcs:
        _assert_engines_agree(g, src)


def test_incomplete_parse_diagnostics_agree():
    g = parse_grammar(
        """
        root = 1*pair
        pair = key "=" value ";"
        key = 1*ALPHA
        value = 1*DIGIT
        """,
        root='root',
    )

    cg = _COMPILED_ENGINE.compile(g)
    rg = _REFERENCE_ENGINE.compile(g)

    src = 'a=1;b=x;'

    with pytest.raises(AbnfIncompleteParseError) as cei:
        cg.parse(src, complete=True)
    with pytest.raises(AbnfIncompleteParseError) as rei:
        rg.parse(src, complete=True)

    assert cei.value.furthest_offset == rei.value.furthest_offset


def test_compiled_state_inspectable():
    from ..engines.interp.engine import InterpCompiledGrammar

    g = parse_grammar('root = 1*DIGIT', root='root')

    cg = _COMPILED_ENGINE.compile(g)
    assert isinstance(cg, InterpCompiledGrammar)
    assert cg.parse('123') is not None

    st = cg._last_state  # noqa
    assert st is not None
    assert st.source == '123'
    assert st.furthest_end == 3
