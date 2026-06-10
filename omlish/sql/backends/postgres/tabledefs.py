import io
import typing as ta

from .... import check
from .... import collections as col
from .... import dataclasses as dc
from ...dtypes import Datetime
from ...dtypes import Integer
from ...dtypes import String
from ...dtypes import Uuid
from ...tabledefs.elements import Column
from ...tabledefs.elements import Index
from ...tabledefs.elements import PrimaryKey
from ...tabledefs.elements import UpdatedAtTrigger
from ...tabledefs.rendering import StatementRenderer
from ...tabledefs.tabledefs import TableDef
from ...tabledefs.values import Now


##


CREATE_UPDATED_AT_TRIGGER_FUNCTION_SRC = """\
create or replace function {function_name}()
returns trigger
language plpgsql
as $$
begin
  if new.{column_name} is not distinct from old.{column_name} then
    new.{column_name} := current_timestamp;
  end if;

  return new;
end;
$$\
"""


CREATE_UPDATED_AT_TRIGGER_SRC = """\
create trigger {trigger_name}
before update on {table_name}
for each row
execute function {function_name}()
"""


CREATE_UPDATED_AT_TRIGGER_IF_NOT_EXISTS_SRC = """\
do $$
begin
  if not exists (
    select 1
    from pg_trigger
    where tgname = '{trigger_name}'
      and tgrelid = '{table_name}'::regclass
  ) then
    create trigger {trigger_name}
    before update on {table_name}
    for each row
    execute function {function_name}();
  end if;
end
$$\
"""


CREATE_INDEX_SRC = """\
create index {preamble} {index_name} on {table_name} ({columns})
"""


@dc.dataclass()
class RenderColumn:
    name: str
    type: str

    _: dc.KW_ONLY

    not_null: bool = False
    default: str | None = None
    identity: bool = False


class PostgresStatementRenderer(StatementRenderer):
    def render_create_statements(
            self,
            tbl: TableDef,
            opts: StatementRenderer.CreateOptions | None = None,
    ) -> list[str]:
        if opts is None:
            opts = self.CreateOptions()

        #

        cols: ta.Mapping[str, Column] = col.make_map_by(
            lambda c: c.name,
            tbl.elements[Column],
            strict=True,
        )

        #

        if (pk := tbl.elements.get(PrimaryKey)) is not None:
            identity_column = (
                pk.columns[0]
                if len(pk.columns) == 1 and isinstance(cols[pk.columns[0]].type, Integer)
                else None
            )
        else:
            identity_column = None

        #

        r_cols: dict[str, RenderColumn] = {}

        for c in cols.values():
            is_identity = c.name == identity_column

            ct: str
            if isinstance(c.type, String):
                ct = 'text'
            elif isinstance(c.type, Uuid):
                ct = 'uuid'
            elif isinstance(c.type, Integer):
                ct = 'bigint' if is_identity else 'integer'
            elif isinstance(c.type, Datetime):
                ct = 'timestamp with time zone'
            else:
                raise TypeError(c.type)

            dfl: str | None = None
            if c.default.present:
                if is_identity:
                    raise TypeError(c)

                dv = c.default.must()

                if isinstance(dv, Now):
                    dfl = 'current_timestamp'
                else:
                    raise TypeError(dv)

            r_cols[c.name] = RenderColumn(
                c.name,
                ct,
                not_null=not c.nullable,
                default=dfl,
                identity=is_identity,
            )

        #

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
                function_name = f'{tbl.name}__function__updated_at__{e.column}'
                trigger_name = f'{tbl.name}__trigger__updated_at__{e.column}'

                triggers.append(CREATE_UPDATED_AT_TRIGGER_FUNCTION_SRC.format(
                    function_name=function_name,
                    column_name=e.column,
                ))

                triggers.append((
                    CREATE_UPDATED_AT_TRIGGER_IF_NOT_EXISTS_SRC
                    if opts.if_not_exists
                    else CREATE_UPDATED_AT_TRIGGER_SRC
                ).format(
                    function_name=function_name,
                    trigger_name=trigger_name,
                    table_name=tbl.name,
                ))

            elif isinstance(e, Index):
                if (idx_name := e.name) is None:
                    idx_name = '__'.join([
                        tbl.name,
                        'index',
                        *e.columns,
                    ])

                indexes.append(CREATE_INDEX_SRC.format(
                    preamble='if not exists' if opts.if_not_exists else '',
                    index_name=idx_name,
                    table_name=tbl.name,
                    columns=', '.join(e.columns),
                ))

            else:
                raise TypeError(e)

        #

        cts = io.StringIO()

        cts.write(f'create table')
        if opts.if_not_exists:
            cts.write(' if not exists')
        cts.write(f' {tbl.name} (\n')

        for i, rc in enumerate(r_cols.values()):
            cts.write(f'  {rc.name} {rc.type}')

            if rc.identity:
                cts.write(' generated by default as identity')

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

        #

        stmts: list[str] = []

        if opts.drop_if_exists:
            stmts.append(f'drop table if exists {tbl.name} cascade')

        stmts.append(cts.getvalue())

        stmts.extend(indexes)
        stmts.extend(triggers)

        return stmts
