import os.path
import sqlite3

from omlish import sql


def test_new_state(tmp_path):
    db_file = os.path.join(str(tmp_path), 'state.db')
    print(db_file)

    with sql.api.DbapiDb(lambda: sqlite3.connect(db_file)) as db:
        with db.connect() as conn:
            with sql.api.query(
                    conn,
                    'select 1',  # noqa
            ) as rows:
                vals = []
                for row in rows:
                    vals.append(tuple(row.values))
                    print(row)
