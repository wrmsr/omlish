"""
https://docs.python.org/3/library/sqlite3.html
https://www.sqlite.org/fts5.html

--enable-loadable-sqlite-extensions
"""
import contextlib
import sqlite3

import pytest

from ...testing import pytest as ptu


def test_sqlite_fts():
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


@pytest.mark.skipif(not hasattr(sqlite3.Connection, 'enable_load_extension'), reason='requires enable_load_extension')
@ptu.skip_if_cant_import('sqlite_vec')
def test_sqlite_vec():
    # https://github.com/asg017/sqlite-vec/tree/main
    import sqlite_vec

    db = sqlite3.connect(':memory:')
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    vec_version, = db.execute('select vec_version()').fetchone()
    print(f'vec_version={vec_version}')

    #

    from sqlite_vec import serialize_float32

    embedding = [0.1, 0.2, 0.3, 0.4]
    result = db.execute('select vec_length(?)', [serialize_float32(embedding)])

    print(result.fetchone()[0])  # 4


@ptu.skip_if_cant_import('apsw')
def test_apsw():
    # https://rogerbinns.github.io/apsw/pysqlite.html
    import apsw

    con = apsw.Connection(':memory:')
    cur = con.cursor()
    for row in cur.execute(
            '; '.join([
                'create table foo (x, y, z)',
                'insert into foo values (?, ?, ?)',
                'insert into foo values (?, ?, ?)',
                'select * from foo',
                'drop table foo',
                'create table bar (x, y)',
                'insert into bar values (?, ?)',
                'insert into bar values (?, ?)',
                'select * from bar',
            ]),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    ):
        print(row)
