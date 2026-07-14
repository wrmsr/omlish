import pytest

from .. import ops
from .. import parsing
from ..engines.base import MatchTreeFidelity
from ..engines.interp import InterpEngine
from ..errors import AbnfIncompleteParseError
from ..grammars import Grammar
from ..grammars import Rule
from ..meta import parse_grammar


##


def _num_grammar() -> Grammar:
    return parse_grammar(
        """
        root = 1*pair
        pair = key "=" value ";"
        key = 1*ALPHA
        value = 1*DIGIT
        """,
        root='root',
    )


def test_interp_engine_capabilities():
    cg = InterpEngine().compile(_num_grammar())

    caps = cg.capabilities
    assert caps.all_matches
    assert caps.partial_parses
    assert caps.any_root
    assert caps.match_tree is MatchTreeFidelity.OPS


def test_interp_engine_parse():
    g = _num_grammar()
    cg = InterpEngine().compile(g)

    m = cg.parse('a=1;b=2;', complete=True)
    assert m is not None
    assert (m.start, m.end) == (0, 8)

    assert cg.parse('!!!') is None

    with pytest.raises(AbnfIncompleteParseError):
        cg.parse('a=1;x', complete=True)


def test_interp_engine_iter_parse():
    g = Grammar(
        Rule('N', ops.repeat(1, ops.literal('0', '9'))),
        root='N',
    )
    cg = InterpEngine().compile(g)

    assert {(m.start, m.end) for m in cg.iter_parse('123')} == {(0, 1), (0, 2), (0, 3)}


def test_interp_engine_any_root():
    g = _num_grammar()
    cg = InterpEngine().compile(g)

    m = cg.parse('42', 'value', complete=True)
    assert m is not None


def test_default_compiled_cached():
    g = _num_grammar()

    cg1 = parsing._default_compiled(g)  # noqa
    cg2 = parsing._default_compiled(g)  # noqa
    assert cg1 is cg2

    # grammar methods route through the same seam and agree with direct engine use
    m1 = g.parse('a=1;', complete=True)
    m2 = cg1.parse('a=1;', complete=True)
    assert m1 == m2
