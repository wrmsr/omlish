import pytest

from .... import lang
from .... import typedvalues as tv
from ...dtypes import String
from ..elements import Column
from ..elements import Elements
from ..elements import PrimaryKey
from ..lower import select_backend_options
from ..options import BackendOption
from ..options import ColumnOption
from ..rendering import StatementRenderer
from ..tabledefs import TableDef


##
# fake backends + options, standing in for what backends/<name> will define


class _PgOption(BackendOption, lang.Abstract):
    pass


class _MyOption(BackendOption, lang.Abstract):
    pass


class _CommonColOpt(ColumnOption, lang.Final):
    pass


class _PgColOpt(_PgOption, ColumnOption, lang.Final):
    pass


class _MyColOpt(_MyOption, ColumnOption, lang.Final):
    pass


##


def test_select_backend_options_strips_foreign():
    td = TableDef('t', Elements(
        Column('x', String(), options=tv.TypedValues(_CommonColOpt(), _PgColOpt(), _MyColOpt())),
    ))

    kept = select_backend_options(td, _PgOption)

    # common + target-backend options survive; the foreign backend's option is stripped.
    assert set(map(type, kept.elements[Column][0].options)) == {_CommonColOpt, _PgColOpt}


##


class _MinimalRenderer(StatementRenderer):
    def column_type(self, c, *, is_identity):
        return 'text'

    def updated_at_trigger_statements(self, tbl, e, pk, opts):
        return []


class _PgRenderer(_MinimalRenderer):
    def column_option_sql(self, c):
        out = []
        with c.options.consume() as cons:
            if cons.pop(_PgColOpt, None) is not None:
                out.append('/* pg */')
        return out


def test_renderer_fails_closed_on_unhandled_option():
    td = TableDef('t', Elements(
        Column('x', String(), options=tv.TypedValues(_CommonColOpt())),
        PrimaryKey(['x']),
    ))

    with pytest.raises(tv.UnconsumedTypedValuesError):
        _MinimalRenderer().render_create_statements(td)


def test_renderer_handles_known_option():
    td = TableDef('t', Elements(
        Column('x', String(), options=tv.TypedValues(_PgColOpt())),
        PrimaryKey(['x']),
    ))

    stmts = _PgRenderer().render_create_statements(td)
    assert '/* pg */' in stmts[0]
