import sqlite3
import urllib.parse

from .... import check
from ....testing import pytest as ptu
from ...dbs import UrlDbLoc
from ...tests.harness import HarnessDbs
from .. import funcs
from ..dbapi import DbapiDb


##


def test_sqlite() -> None:
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


@ptu.skip.if_cant_import('pg8000')
def test_pg8000(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pg8000

    with DbapiDb(lambda: pg8000.connect(
            p_u.username,
            host=p_u.hostname,
            port=p_u.port,
            password=p_u.password,
    )) as db:
        with db.connect() as conn:
            for q in [
                'select 1',
                'select 1 union select 2',
                # 'select 1, 2 union select 3, 4',
            ]:
                with funcs.query(conn, q) as rows:
                    vals = []
                    for row in rows:
                        vals.append(tuple(row.values))
                        print(row)

                print(vals)


def test_queries():
    from ...queries import Q

    with DbapiDb(lambda: sqlite3.connect(':memory:')) as db:
        with db.connect() as conn:
            print(funcs.query_all(conn, Q.select([1])))
            print(list(funcs.query(conn, Q.select([1]))))
            print(funcs.query(conn, Q.select([1])))
