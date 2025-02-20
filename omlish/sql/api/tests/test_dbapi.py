import sqlite3

from .. import funcs
from ..dbapi import DbapiDb


##


def test_dbapi() -> None:
    with DbapiDb(lambda: sqlite3.connect(':memory:')) as db:
        with db.connect() as conn:
            for stmt in [
                'create table "movies" ("title", "year", "score")',  # noqa
                '\n'.join([
                    'insert into "movies" values',  # noqa
                    "('Monty Python and the Holy Grail', 1975, 8.2),",
                    "('And Now for Something Completely Different', 1971, 7.5)",
                ]),
            ]:
                funcs.exec(conn, stmt)

            with funcs.query(
                    conn,
                    'select "score" from "movies"',  # noqa
            ) as rows:
                vals = []
                for row in rows:
                    vals.append(tuple(row.values))
                    print(row)

            assert vals == [
                (8.2,),
                (7.5,),
            ]
