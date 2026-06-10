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

    def render_default(self, v: SimpleValue) -> str:
        if isinstance(v, Now):
            return 'current_timestamp'
        else:
            raise TypeError(v)

    def table_suffixes(self, tbl: TableDef, identity_column: str | None) -> list[str]:
        return []

    def drop_statement(self, tbl: TableDef) -> str:
        return f'drop table if exists {tbl.name}'

    CREATE_INDEX_SRC = 'create index {preamble} {index_name} on {table_name} ({columns})\n'

    def index_statement(self, tbl: TableDef, e: Index, opts: CreateOptions) -> str:
        if (idx_name := e.name) is None:
            idx_name = '__'.join([tbl.name, 'index', *e.columns])

        return self.CREATE_INDEX_SRC.format(
            preamble='if not exists' if opts.if_not_exists else '',
            index_name=idx_name,
            table_name=tbl.name,
            columns=', '.join(e.columns),
        )

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
