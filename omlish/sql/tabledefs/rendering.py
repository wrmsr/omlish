import abc
import io
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ..dtypes import Integer
from .elements import Column
from .elements import Index
from .elements import PrimaryKey
from .elements import UpdatedAtTrigger
from .predicates import And
from .predicates import Compare
from .predicates import IsNull
from .predicates import Not
from .predicates import Or
from .predicates import Predicate
from .predicates import RawPredicate
from .predicates import SimplePredicateValue
from .tabledefs import TableDef
from .values import Now
from .values import SimpleValue


##


@dc.dataclass()
class RenderColumn:
    name: str
    type: str

    _: dc.KW_ONLY

    not_null: bool = False
    default: str | None = None
    identity: str = ''
    extra: ta.Sequence[str] = ()


class StatementRenderer(lang.Abstract):
    """
    Standard CREATE-TABLE assembly shared by all backends. Dialects override only the small set of hooks below; the
    column/constraint/index layout and the identity-column detection are shared so backends do not duplicate them.
    """

    @dc.dataclass(frozen=True, kw_only=True)
    class CreateOptions:
        drop_if_exists: bool = False
        if_not_exists: bool = False

    ##
    # hooks

    @abc.abstractmethod
    def column_type(self, c: Column, *, is_identity: bool) -> str:
        raise NotImplementedError

    def column_identity_sql(self, c: Column) -> str:
        return ''

    def column_option_sql(self, c: Column) -> list[str]:
        # Base supports no column options; any present trips the fail-closed consumer.
        with c.options.consume():
            pass
        return []

    def consume_table_options(self, tbl: TableDef) -> None:
        # Base supports no table options.
        with tbl.options.consume():
            pass

    def render_default(self, v: SimpleValue) -> str:
        if isinstance(v, Now):
            return 'current_timestamp'
        else:
            raise TypeError(v)

    def table_suffixes(self, tbl: TableDef, identity_column: str | None) -> list[str]:
        return []

    def drop_statement(self, tbl: TableDef) -> str:
        return f'drop table if exists {tbl.name}'

    def index_statement(self, tbl: TableDef, e: Index, opts: CreateOptions) -> str:
        if (idx_name := e.name) is None:
            idx_name = '__'.join([tbl.name, 'index', *e.columns])

        with e.options.consume():
            pass  # base supports no index options

        out = io.StringIO()
        out.write('create ')
        if e.unique:
            out.write('unique ')
        out.write('index ')
        if opts.if_not_exists:
            out.write('if not exists ')
        out.write(f'{idx_name} on {tbl.name} ({", ".join(e.columns)})')
        if e.where is not None:
            out.write(f' where {self.render_predicate(e.where)}')
        out.write('\n')
        return out.getvalue()

    def render_predicate(self, p: Predicate) -> str:
        if isinstance(p, RawPredicate):
            return p.s
        elif isinstance(p, Compare):
            return f'{p.column} {p.op.value} {self.render_predicate_value(p.value)}'
        elif isinstance(p, IsNull):
            return f'{p.column} is not null' if p.negated else f'{p.column} is null'
        elif isinstance(p, Not):
            return f'not ({self.render_predicate(p.predicate)})'
        elif isinstance(p, And):
            return ' and '.join(f'({self.render_predicate(c)})' for c in p.predicates)
        elif isinstance(p, Or):
            return ' or '.join(f'({self.render_predicate(c)})' for c in p.predicates)
        else:
            raise TypeError(p)  # fail-closed: backend predicate nodes are handled by the backend's override

    def render_predicate_value(self, v: SimplePredicateValue) -> str:
        if v is None:
            return 'null'
        elif isinstance(v, bool):
            return 'true' if v else 'false'
        elif isinstance(v, (int, float)):
            return str(v)
        elif isinstance(v, str):
            return "'" + v.replace("'", "''") + "'"
        else:
            raise TypeError(v)

    @abc.abstractmethod
    def updated_at_trigger_statements(
            self,
            tbl: TableDef,
            e: UpdatedAtTrigger,
            pk: PrimaryKey | None,
            opts: CreateOptions,
    ) -> list[str]:
        raise NotImplementedError

    ##
    # shared assembly

    def _identity_column(self, cols: ta.Mapping[str, Column], pk: PrimaryKey | None) -> str | None:
        if pk is not None and len(pk.columns) == 1 and isinstance(cols[pk.columns[0]].type, Integer):
            return pk.columns[0]
        return None

    def render_create_statements(
            self,
            tbl: TableDef,
            opts: CreateOptions | None = None,
    ) -> list[str]:
        if opts is None:
            opts = self.CreateOptions()

        self.consume_table_options(tbl)

        cols: ta.Mapping[str, Column] = col.make_map_by(
            lambda c: c.name,
            tbl.elements[Column],
            strict=True,
        )

        pk = tbl.elements.get(PrimaryKey)
        identity_column = self._identity_column(cols, pk)

        r_cols: dict[str, RenderColumn] = {}
        for c in cols.values():
            is_identity = c.name == identity_column

            dfl: str | None = None
            if c.default.present:
                if is_identity:
                    raise TypeError(c)
                dfl = self.render_default(c.default.must())

            r_cols[c.name] = RenderColumn(
                c.name,
                self.column_type(c, is_identity=is_identity),
                not_null=not c.nullable,
                default=dfl,
                identity=self.column_identity_sql(c) if is_identity else '',
                extra=self.column_option_sql(c),
            )

        constraints: list[str] = []
        indexes: list[str] = []
        triggers: list[str] = []

        for e in tbl.elements:
            if isinstance(e, Column):
                pass  # Already handled

            elif isinstance(e, PrimaryKey):
                check.not_empty(e.columns)
                constraints.append(f'primary key ({", ".join(e.columns)})')

            elif isinstance(e, UpdatedAtTrigger):
                triggers.extend(self.updated_at_trigger_statements(tbl, e, pk, opts))

            elif isinstance(e, Index):
                indexes.append(self.index_statement(tbl, e, opts))

            else:
                raise TypeError(e)

        cts = io.StringIO()

        cts.write('create table')
        if opts.if_not_exists:
            cts.write(' if not exists')
        cts.write(f' {tbl.name} (\n')

        for i, rc in enumerate(r_cols.values()):
            cts.write(f'  {rc.name} {rc.type}')

            if rc.identity:
                cts.write(f' {rc.identity}')

            if rc.not_null:
                cts.write(' not null')

            if rc.default is not None:
                cts.write(f' default {rc.default}')

            for x in rc.extra:
                cts.write(f' {x}')

            if constraints or i < len(r_cols) - 1:
                cts.write(',')

            cts.write('\n')

        for i, cs in enumerate(constraints):
            cts.write(f'  {cs}')

            if i < len(constraints) - 1:
                cts.write(',')

            cts.write('\n')

        cts.write(')')

        for sfx in self.table_suffixes(tbl, identity_column):
            cts.write('\n')
            cts.write(sfx)

        stmts: list[str] = []

        if opts.drop_if_exists:
            stmts.append(self.drop_statement(tbl))

        stmts.append(cts.getvalue())

        stmts.extend(indexes)
        stmts.extend(triggers)

        return stmts
