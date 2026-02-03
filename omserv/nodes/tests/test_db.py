import contextlib
import sqlite3

from omlish import sql
from omlish.sql import Q

from ..db import setup_db


##


def test_sqlite(exit_stack) -> None:
    db = sql.api.DbapiDb(lambda: contextlib.closing(sqlite3.connect(':memory:', autocommit=True)))
    conn = exit_stack.enter_context(db.connect())

    setup_db(conn)

    for _ in range(2):
        with sql.query(conn, Q.select([Q.star], Q.n.nodes)) as rows:
            for row in rows:
                print(row)
