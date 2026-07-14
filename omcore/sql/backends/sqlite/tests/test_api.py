import sqlite3

from ....api import querierfuncs as qf
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb


##


def test_sqlite(exit_stack) -> None:
    db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True))
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

    assert qf.query_scalar(conn, 'select ? + 1', [2]) == 3
