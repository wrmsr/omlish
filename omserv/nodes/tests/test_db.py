import sqlite3

from omlish import sql

from ..db import setup_db


##


def test_sqlite(exit_stack) -> None:
    db = exit_stack.enter_context(sql.api.DbapiDb(lambda: sqlite3.connect(':memory:', autocommit=True)))
    conn = exit_stack.enter_context(db.connect())

    setup_db(conn)

    with sql.query(conn, 'select * from nodes') as rows:
        for row in rows:
            print(row)
