import contextlib
import sqlite3

from ....dtypes import String
from ....tabledefs.elements import Column
from ....tabledefs.elements import CreatedAtUpdatedAt
from ....tabledefs.elements import Elements
from ....tabledefs.elements import IdIntegerPrimaryKey
from ....tabledefs.lower import lower_table_elements
from ....tabledefs.tabledefs import TableDef
from ..tabledefs import SqliteTabledefRenderer


def test_render_create_table():
    tbl = TableDef(
        'users',
        Elements(*[
            IdIntegerPrimaryKey(),
            CreatedAtUpdatedAt(),
            Column('name', String()),
        ]),
    )

    tbl = lower_table_elements(tbl)

    stmts = SqliteTabledefRenderer().render_create_statements(tbl)

    print('\n\n'.join(stmts))

    with contextlib.closing(sqlite3.connect(':memory:')) as db:
        cur = db.cursor()

        for stmt in stmts:
            cur.execute(stmt)
