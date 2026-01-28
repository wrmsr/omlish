import sqlite3

from omlish.sql import api
from omlish.sql.tabledefs.lower import lower_table_elements
from omlish.sql.tabledefs.rendering import render_create_statements

from ..models import NODES



##


def test_sqlite(exit_stack) -> None:
    db = exit_stack.enter_context(api.DbapiDb(lambda: sqlite3.connect(':memory:', autocommit=True)))
    conn = exit_stack.enter_context(db.connect())

    for stmt in render_create_statements(lower_table_elements(NODES)):
        api.exec(conn, stmt)

    with api.query(conn, 'select * from nodes') as rows:
        for row in rows:
            print(row)
