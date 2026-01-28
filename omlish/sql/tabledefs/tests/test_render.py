import dataclasses as dc
import typing as ta

from .... import collections as col
from ..values import Now
from .... import check
from ..dtypes import Datetime
from ..dtypes import Integer
from ..dtypes import String
from ..elements import Column
from ..elements import CreatedAtUpdatedAt
from ..elements import Elements
from ..elements import IdIntegerPrimaryKey
from ..elements import PrimaryKey
from ..elements import UpdatedAtTrigger
from ..lower import lower_table_elements
from ..tabledefs import TableDef


"""
create table users (
    id integer not null primary key,
    created_at datetime,
    updated_at datetime
)
"""


UPDATED_AT_TRIGGER_SRC = """\
create trigger {trigger_name}
after update on {table_name}
for each row
when new.{column_name} = old.{column_name}
begin
  update {table_name}
  set {column_name} = datetime('now')
  where rowid = new.rowid;
end;
"""


@dc.dataclass()
class RenderColumn:
    name: str
    type: str
    not_null: bool = False
    primary_key: bool = False
    default: str | None = None


def test_render_create_table():
    tbl = TableDef(
        'users',
        Elements([
            IdIntegerPrimaryKey(),
            CreatedAtUpdatedAt(),
            Column('name', String()),
        ]),
    )

    tbl = lower_table_elements(tbl)

    #

    cols: ta.Mapping[str, Column] = col.make_map_by(
        lambda c: c.name,
        tbl.elements.by_type[Column],
        strict=True,
    )

    #

    r_cols: dict[str, RenderColumn] = {}

    for c in cols.values():
        if isinstance(c.type, String):
            ct = 'string',
        elif isinstance(c.type, Integer):
            ct = 'integer',
        elif isinstance(c.type, Datetime):
            ct = 'datetime'
        else:
            raise TypeError(c.type)

        dfl: str | None = None
        if c.default.present:
            dv = c.default.must()

            if isinstance(dv, Now):
                dfl = "datetime('now')"
            else:
                raise TypeError(dv)

        r_cols[c.name] = RenderColumn(
            c.name,
            ct,
            not_null=c.not_null,
            default=dfl,
        )

    #

    pk_cols: ta.Sequence[str] | None = None

    triggers: list[str] = []

    for e in tbl.elements:
        if isinstance(e, Column):
            pass  # Already handled

        elif isinstance(e, PrimaryKey):
            check.none(pk_cols)
            pk_cols = e.columns

        elif isinstance(e, UpdatedAtTrigger):
            triggers.append(UPDATED_AT_TRIGGER_SRC.format(
                trigger_name=f'{tbl.name}__trigger__updated_at__{e.column}',
                table_name=tbl.name,
                column_name=e.column,
            ))

        else:
            raise TypeError(e)
