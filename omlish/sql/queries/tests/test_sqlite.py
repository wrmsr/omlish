import contextlib
import sqlite3
import typing as ta

from ...abc import DbapiColumnDescription_
from .. import Q
from .. import render


def test_sqlite_query():
    with contextlib.closing(sqlite3.connect(':memory:')) as db:
        cur = db.cursor()

        cur.execute('create table movies(title, year, score)')

        cur.execute("""
            insert into movies values
                ('Monty Python and the Holy Grail', 1975, 8.2),
                ('And Now for Something Completely Different', 1971, 7.5)
        """)
        db.commit()

        def exec_query(qs: str) -> list[dict[str, ta.Any]]:
            res = cur.execute(qs)
            dsc_lst = [DbapiColumnDescription_(*dt) for dt in res.description]
            rows_tups = res.fetchall()
            return [
                {dsc.name: v for dsc, v in zip(dsc_lst, row)}
                for row in rows_tups
            ]

        q = Q.select(
            [Q.n.score],
            Q.n.movies,
        )
        rq = render(q)

        print(exec_query(rq.s))
