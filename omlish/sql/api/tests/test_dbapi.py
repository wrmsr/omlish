import sqlite3
import typing as ta
import urllib.parse

import pytest

from .... import check
from ....resources import ResourceNotEnteredError
from ....testing import pytest as ptu
from ...dbs import UrlDbLoc
from ...tests.harness import HarnessDbs
from .. import querierfuncs as qf
from ..dbapi import DbapiDb


##


def test_sqlite(exit_stack) -> None:
    db = exit_stack.enter_context(DbapiDb(lambda: sqlite3.connect(':memory:', autocommit=True)))
    conn = exit_stack.enter_context(db.connect())

    for stmt in [
        'create table "movies" ("title", "year", "score")',  # noqa
        '\n'.join([
            'insert into "movies" values',  # noqa
            "('Monty Python and the Holy Grail', 1975, 8.2),",
            "('And Now for Something Completely Different', 1971, 7.5)",
        ]),
    ]:
        qf.exec(conn, stmt)

    with qf.query(
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

    with conn.begin():
        assert qf.query_scalar(conn, 'select count(*) from movies') == 2
        qf.exec(conn, "insert into movies (title, year, score) values ('Bad Movie', 1991, 0.1)")
        assert qf.query_scalar(conn, 'select count(*) from movies') == 3
    assert qf.query_scalar(conn, 'select count(*) from movies') == 3

    with conn.begin() as txn:
        assert qf.query_scalar(conn, 'select count(*) from movies') == 3
        qf.exec(conn, "insert into movies (title, year, score) values ('Bad Movie 2', 1992, 0.1)")
        assert qf.query_scalar(conn, 'select count(*) from movies') == 4
        txn.rollback()
    assert qf.query_scalar(conn, 'select count(*) from movies') == 3


@ptu.skip.if_cant_import('pg8000')
def test_pg8000(harness, exit_stack) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pg8000

    db = exit_stack.enter_context(DbapiDb(lambda: pg8000.connect(
        p_u.username,
        host=p_u.hostname,
        port=p_u.port,
        password=p_u.password,
    )))

    conn = exit_stack.enter_context(db.connect())

    for q in [
        'select 1',
        'select 1 union select 2',
        # 'select 1, 2 union select 3, 4',
    ]:
        with qf.query(conn, q) as rows:
            vals = []
            for row in rows:
                vals.append(tuple(row.values))
                print(row)

        print(vals)


def test_queries():
    from ...queries import Q

    with DbapiDb(lambda: sqlite3.connect(':memory:')) as db:
        with db.connect() as conn:
            print(qf.query_all(conn, Q.select([1])))


def test_check_entered():
    with DbapiDb(lambda: sqlite3.connect(':memory:')) as db:
        with db.connect() as conn:
            with pytest.raises(ResourceNotEnteredError):
                print(list(ta.cast(ta.Any, qf.query(conn, 'select 1'))))
