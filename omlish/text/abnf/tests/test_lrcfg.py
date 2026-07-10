"""Tests for lowering tokenized parser rules to a CFG."""
from ..engines.lr.cfg import Nt
from ..engines.lr.cfg import lower_to_cfg
from ..engines.tokens import extract_tokenized
from ..engines.tokens.specs import TokenSpec
from ..meta import parse_grammar


##


def _lower(src: str, root: str):
    g = parse_grammar(src, root=root, no_optimize=True)
    return lower_to_cfg(extract_tokenized(g))


def test_lower_simple():
    cfg = _lower(
        """
        root = t S %x3B
        %token t = 1*ALPHA
        S = *WS
        %token %channel(space) WS = 1*SP
        """,
        'root',
    )

    assert cfg.root_nt.name == 'root'
    assert cfg.root_nt.is_rule

    [p] = cfg.by_lhs[cfg.root_nt]
    # the S ref is elided entirely
    assert [s.name for s in p.rhs] == ['t', '";"']
    assert all(isinstance(s, TokenSpec) for s in p.rhs)


def test_lower_repeat_left_recursive():
    cfg = _lower(
        """
        root = t *(S %x2C S t)
        %token t = 1*ALPHA
        S = *WS
        %token %channel(space) WS = 1*SP
        """,
        'root',
    )

    # the star lowers to a nullable left-recursive spine
    spines = [n for n in cfg.nts if not n.is_rule]
    assert len(spines) == 1
    [spine] = spines

    prods = cfg.by_lhs[spine]
    assert len(prods) == 2
    empt = [p for p in prods if not p.rhs]
    recs = [p for p in prods if p.rhs]
    assert len(empt) == 1
    [rec] = recs
    assert rec.rhs[0] is spine  # left recursion


def test_lower_alternation_splice_nts():
    cfg = _lower(
        """
        root = a S b
        a = "x" | "y"
        b = "z"
        S = *WS
        %token %channel(space) WS = 1*SP
        """,
        'root',
    )

    a_nt = next(n for n in cfg.nts if n.name == 'a' and isinstance(n, Nt))
    assert a_nt.is_rule
    # the | alternation lowers to two productions on a synthetic splice nt (or directly on 'a')
    assert sum(len(cfg.by_lhs[n]) for n in cfg.nts if n.rule_name == 'a') >= 2


def test_lower_bounded_repeat():
    cfg = _lower(
        """
        root = 2*4(t S)
        %token t = 1*ALPHA
        S = *WS
        %token %channel(space) WS = 1*SP
        """,
        'root',
    )

    [p] = cfg.by_lhs[cfg.root_nt]
    # two required copies plus two optional-slots
    assert len(p.rhs) == 4

    opts = [n for n in cfg.nts if not n.is_rule]
    assert len(opts) == 1
    assert len(cfg.by_lhs[opts[0]]) == 2  # empty | body


def test_lower_terminals_collected():
    cfg = _lower(
        """
        root = kw S t
        kw = "select"
        %token t = 1*ALPHA
        S = *WS
        %token %channel(space) WS = 1*SP
        """,
        'root',
    )

    names = {ts.name for ts in cfg.terminals.values()}
    assert names == {'%i"select"', 't'}
