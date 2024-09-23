"""
https://docs.python.org/3/library/sqlite3.html
https://www.sqlite.org/fts5.html
"""
import contextlib
import sqlite3


def test_sqlite():
    with contextlib.closing(sqlite3.connect(':memory:')) as db:
        cur = db.cursor()

        cur.execute('create table movies(title, year, score)')

        cur.execute("""
            insert into movies values
                ('Monty Python and the Holy Grail', 1975, 8.2),
                ('And Now for Something Completely Different', 1971, 7.5)
        """)
        db.commit()

        res = cur.execute('select score from movies')
        print(res.fetchall())

        cur.execute('create virtual table movies_fts using fts5(title)')
        cur.execute("""
            insert into movies_fts
            select title from movies
        """)
        db.commit()

        res = cur.execute('select * from movies_fts where title match ?', ['something'])
        print(res.fetchall())
