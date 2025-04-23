import os.path
import sqlite3

from omlish import sql


def test_new_state(tmp_path):
    db_file = os.path.join(str(tmp_path), 'state.db')
    print(db_file)

    with sql.api.DbapiDb(lambda: sqlite3.connect(db_file)) as db:
        with db.connect() as conn:
            sql.api.exec(conn, """create table if not exists "state" ("state")""")
            sql.api.exec(conn, """insert into "state" ("state") values ('I am state')""")

            for row in sql.api.query_all(conn, 'select * from "state"'):
                print(row)
