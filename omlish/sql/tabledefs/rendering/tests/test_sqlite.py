import contextlib
import sqlite3

from ...dtypes import String
from ...elements import Column
from ...elements import CreatedAtUpdatedAt
from ...elements import Elements
from ...elements import IdIntegerPrimaryKey
from ...lower import lower_table_elements
from ...tabledefs import TableDef
from ..sqlite import SqliteStatementRenderer


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

    stmts = SqliteStatementRenderer().render_create_statements(tbl)

    print('\n\n'.join(stmts))

    with contextlib.closing(sqlite3.connect(':memory:')) as db:
        cur = db.cursor()

        for stmt in stmts:
            cur.execute(stmt)
