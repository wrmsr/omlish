import pytest

from .... import dataclasses as dc
from .... import lang
from ...dtypes import Integer
from ...dtypes import String
from ...syntax import CompareOp
from ..elements import Column
from ..elements import Elements
from ..elements import Index
from ..elements import PrimaryKey
from ..predicates import And
from ..predicates import Compare
from ..predicates import IsNull
from ..predicates import Not
from ..predicates import Or
from ..predicates import Predicate
from ..predicates import RawPredicate
from ..predicates import as_opt_predicate
from ..rendering import StatementRenderer
from ..tabledefs import TableDef


class _R(StatementRenderer):
    def column_type(self, c, *, is_identity, indexed=False):
        return 'integer' if isinstance(c.type, Integer) else 'text'

    def updated_at_trigger_statements(self, tbl, e, pk, opts):
        return []


def test_render_predicate_nodes():
    r = _R()
    assert r.render_predicate(RawPredicate('a > 0')) == 'a > 0'
    assert r.render_predicate(Compare('age', CompareOp.GE, 18)) == 'age >= 18'
    assert r.render_predicate(Compare('name', CompareOp.EQ, "x'y")) == "name = 'x''y'"
    assert r.render_predicate(IsNull('deleted_at')) == 'deleted_at is null'
    assert r.render_predicate(IsNull('deleted_at', negated=True)) == 'deleted_at is not null'
    assert r.render_predicate(Not(Compare('x', CompareOp.EQ, 1))) == 'not (x = 1)'
    assert r.render_predicate(And([Compare('a', CompareOp.EQ, 1), IsNull('b')])) == '(a = 1) and (b is null)'
    assert r.render_predicate(Or([Compare('a', CompareOp.LT, 1), Compare('a', CompareOp.GT, 9)])) == \
        '(a < 1) or (a > 9)'


def test_as_opt_predicate_coerces_str():
    p = as_opt_predicate('x > 0')
    assert isinstance(p, RawPredicate)
    assert p.s == 'x > 0'
    assert as_opt_predicate(None) is None


def test_partial_index_render():
    td = TableDef('t', Elements(
        Column('id', Integer()),
        PrimaryKey(['id']),
        Column('name', String()),
        Index(['name'], where=Compare('deleted', CompareOp.EQ, False)),
    ))

    stmts = _R().render_create_statements(td)
    idx = next(s for s in stmts if s.startswith('create index'))
    assert idx == 'create index t__index__name on t (name) where deleted = false\n'


def test_unique_index_render():
    td = TableDef('t', Elements(
        Column('id', Integer()),
        PrimaryKey(['id']),
        Column('name', String()),
        Index(['name'], unique=True),
    ))

    stmts = _R().render_create_statements(td)
    idx = next(s for s in stmts if 'index' in s)
    assert idx == 'create unique index t__index__name on t (name)\n'


##
# a backend-specific predicate node + a renderer that handles it, deferring to super for common nodes


@dc.dataclass(frozen=True)
class _PgRegexp(Predicate, lang.Final):
    column: str
    pattern: str


class _PgR(_R):
    def render_predicate(self, p):
        if isinstance(p, _PgRegexp):
            return f"{p.column} ~ '{p.pattern}'"
        return super().render_predicate(p)


def test_backend_predicate_override():
    r = _PgR()
    assert r.render_predicate(_PgRegexp('name', '^a')) == "name ~ '^a'"
    # common nodes still go through the base.
    assert r.render_predicate(Compare('x', CompareOp.EQ, 1)) == 'x = 1'


def test_base_fails_closed_on_backend_predicate():
    with pytest.raises(TypeError):
        _R().render_predicate(_PgRegexp('name', '^a'))
