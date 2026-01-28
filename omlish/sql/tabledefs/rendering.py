import dataclasses as dc
import io
import typing as ta

from ... import collections as col
from ..tabledefs import TableDef
from .dtypes import Datetime
from .dtypes import Integer
from .dtypes import String
from .elements import Column
from .elements import Index
from .elements import PrimaryKey
from .elements import UpdatedAtTrigger
from .values import Now


##


UPDATED_AT_TRIGGER_SRC = """\
create trigger {trigger_name}
after update on {table_name}
for each row
when new.{column_name} = old.{column_name}
  begin
  update {table_name}
  set {column_name} = current_timestamp
  where rowid = new.rowid;
end\
"""


@dc.dataclass()
class RenderColumn:
    name: str
    type: str
    not_null: bool = False
    primary_key: bool = False
    default: str | None = None


def render_create_statements(tbl: TableDef) -> list[str]:
    cols: ta.Mapping[str, Column] = col.make_map_by(
        lambda c: c.name,
        tbl.elements.by_type[Column],
        strict=True,
    )

    #

    r_cols: dict[str, RenderColumn] = {}

    for c in cols.values():
        ct: str
        if isinstance(c.type, String):
            ct = 'string'
        elif isinstance(c.type, Integer):
            ct = 'integer'
        elif isinstance(c.type, Datetime):
            ct = 'datetime'
        else:
            raise TypeError(c.type)

        dfl: str | None = None
        if c.default.present:
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
        )

    #

    indexes: list[str] = []

    triggers: list[str] = []

    for e in tbl.elements:
        if isinstance(e, Column):
            pass  # Already handled

        elif isinstance(e, PrimaryKey):
            for pc in e.columns:
                rc = r_cols[pc]
                rc.primary_key = True

        elif isinstance(e, UpdatedAtTrigger):
            triggers.append(UPDATED_AT_TRIGGER_SRC.format(
                trigger_name=f'{tbl.name}__trigger__updated_at__{e.column}',
                table_name=tbl.name,
                column_name=e.column,
            ))

        elif isinstance(e, Index):
            if (idx_name := e.name) is None:
                idx_name = '__'.join([
                    tbl.name,
                    'index',
                    *e.columns,
                ])

            indexes.append(f'create index {idx_name} on {tbl.name} ({", ".join(e.columns)})')

        else:
            raise TypeError(e)

    #

    cts = io.StringIO()

    cts.write(f'create table {tbl.name} (\n')
    for i, rc in enumerate(r_cols.values()):
        cts.write(f'  {rc.name} {rc.type}')

        if rc.not_null:
            cts.write(' not null')

        if rc.primary_key:
            cts.write(' primary key')

        if rc.default is not None:
            cts.write(f' default {rc.default}')

        if i < len(r_cols) - 1:
            cts.write(',')

        cts.write('\n')

    cts.write(')')

    #

    stmts: list[str] = [cts.getvalue()]

    stmts.extend(indexes)
    stmts.extend(triggers)

    return stmts
