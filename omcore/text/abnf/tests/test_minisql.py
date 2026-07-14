"""
Differential conformance: the interpreter and LALR engines must agree on the tokenized minisql fixture - both
acceptance and (rule-level) tree shape, from one shared grammar text.
"""
import os.path

import pytest

from .... import check
from .... import lang
from ..engines.lr import LrEngine
from ..engines.lr.engine import LrCompiledGrammar
from ..engines.tokens import extract_tokenized
from ..errors import AbnfParseError
from ..grammars import Grammar
from ..matches import Match
from ..meta import parse_grammar
from ..ops import RuleRef
from ..utils import only_match_rules


##


@lang.cached_function
def _fixture() -> tuple[Grammar, LrCompiledGrammar]:
    with open(os.path.join(os.path.dirname(__file__), 'minisql.abnf')) as f:
        g = parse_grammar(f.read(), root='single-stmt', no_optimize=True)

    lcg = check.isinstance(LrEngine().compile(g), LrCompiledGrammar)
    return (g, lcg)


@lang.cached_function
def _tokenized():
    g, _ = _fixture()
    return extract_tokenized(g)


##
# tree shape comparison
#
# LR trees are rule-level: parser-rule nodes, non-hidden token leaves, nothing else. Interp trees are op-level; after
# only_match_rules they still contain skip wrappers and token-internal rule refs, so prune to the same shape. Token
# leaf spans must agree exactly; internal node spans may differ at skip boundaries (interp rule spans can include
# leading/trailing whitespace matched by S refs inside the rule) - so shapes compare names + leaf spans only.


def _interp_shapes(m: Match) -> list:
    tkz = _tokenized()
    out: list = []
    for c in m.children:
        n = check.isinstance(c.op, RuleRef).name_f
        if n in tkz.parser_rules:
            out.append((n, _interp_shapes(c)))
        elif (ts := tkz.token_rule_specs.get(n)) is not None and not ts.hidden:
            out.append(('tok', n, c.start, c.end))
        # else: skip wrappers, hidden tokens - dropped
    return out


def _lr_shapes_children(m: Match) -> list:
    tkz = _tokenized()
    out: list = []
    for c in m.children:
        n = check.isinstance(c.op, RuleRef).name_f
        if n in tkz.token_rule_specs:
            out.append(('tok', n, c.start, c.end))
        else:
            out.append((n, _lr_shapes_children(c)))
    return out


def _assert_agree(src: str) -> None:
    g, lcg = _fixture()

    im = check.not_none(g.parse(src, complete=True))
    im = only_match_rules(im)
    ishape = _interp_shapes(im)  # the interp root node is the rule body op - children are the comparable level

    lm = check.not_none(lcg.parse(src, complete=True))
    assert check.isinstance(lm.op, RuleRef).name_f == 'single-stmt'
    lshape = _lr_shapes_children(lm)

    assert ishape == lshape, f'engines disagree on {src!r}'


def _assert_both_fail(src: str) -> None:
    g, lcg = _fixture()

    with pytest.raises(AbnfParseError):
        g.parse(src, complete=True)

    with pytest.raises(AbnfParseError):
        lcg.parse(src, complete=True)


##


def test_lr_compiles_clean():
    _, lcg = _fixture()
    assert lcg.tables.num_states > 50


@pytest.mark.parametrize('src', [
    'select x;',
    'select x from y;',
    'select * from t;',
    'select a, b + 1 as c from t;',
    "select a from t join u on t.x = u.y where a > 2 and b like 'foo%';",
    'select a from t left outer join u on t.a = u.a;',
    'with c as (select a from t) select a from c;',
    "select case when a = 1 then 'one' else 'other' end from t;",
    'select f(a, b), g(*) over (order by a desc) from t;',
    'select -1.5e3 + .5 from t;',
    'select "quoted id" from t;  -- trailing comment\n',
    '/* leading */ select /* mid */ x from t;',
    'select a from (select a from t) x;',
    'select a from t where a in (1, 2) and b in (select c from u);',
    'select left from right;',
    'select a || b from t;',
    'select a from t where a is not null;',
    'select t.a from db.t;',
    'select a::int from t;',
    'select a from t union all select b from u;',
    'select distinct a from t group by a having a > 1 order by a;',
    "select 'it''s', x from t;",
])
def test_engines_agree(src):
    _assert_agree(src)


@pytest.mark.parametrize('src', [
    '',
    ';',
    'select;',
    'select x from 1;',
    'select x',
    'select x from t',
    'select x from t;;',
    'selectx from t;',
    'select (a from t;',
    'select 1x;',  # requires the driver's elided-R gap assertion to fail in token mode
])
def test_engines_agree_on_failures(src):
    _assert_both_fail(src)


def test_known_reserved_word_divergence():
    # The one inherent semantic gap between the engines: char-level regular-ident happily matches reserved words
    # (pure ABNF cannot express the exclusion), while maximal-munch lexing reserves them. The original minisql grammar
    # carries the same caveat as a comment.
    g, lcg = _fixture()

    src = 'select from t;'  # 'from' as a bare identifier

    assert g.parse(src, complete=True) is not None

    with pytest.raises(AbnfParseError):
        lcg.parse(src, complete=True)


def test_comment_pickup():
    _, lcg = _fixture()

    src = 'select x -- pick me up\nfrom t; /* and me */'
    assert lcg.parse(src, complete=True) is not None

    comments = [t.text(src) for t in lcg.lex(src) if t.spec.name == 'comment']
    assert comments == ['-- pick me up', '/* and me */']
