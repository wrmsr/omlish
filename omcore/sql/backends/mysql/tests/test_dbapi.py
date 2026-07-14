import contextlib
import typing as ta
import urllib.parse

from ..... import check
from ..... import lang
from .....testing import pytest as ptu
from ....dbs import UrlDbLoc
from ....tests.harness import HarnessDbs


if ta.TYPE_CHECKING:
    import pymysql
else:
    pymysql = lang.proxy_import('pymysql')


@ptu.skip.if_cant_import('pymysql')
def test_mysql(harness):
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['mysql'].loc, UrlDbLoc).url, str)
    pu = urllib.parse.urlparse(url)

    with contextlib.ExitStack() as es:
        try:
            conn: pymysql.Connection = es.enter_context(contextlib.closing(pymysql.connect(  # noqa
                host=pu.hostname,
                database='omlish',
                user=pu.username,
                password=check.not_none(pu.password),
                port=check.not_none(pu.port),
            )))

            print('Connected to the database!')

            # Create a cursor
            cursor = es.enter_context(contextlib.closing(conn.cursor()))  # noqa

            # Example 1: Create a table
            cursor.execute("""
            create table if not exists example_table (
                id serial primary key,
                name text not null,
                age integer not null
            )
            """)
            print('Table created (if not already existing).')

            # Example 2: Insert data
            cursor.execute("""
            insert into example_table (name, age)
            values (%s, %s)
            """, ('Alice', 30))
            print('Inserted one row.')

            # Commit the transaction
            conn.commit()

            # Example 3: Query data
            cursor.execute('select id, name, age from example_table')
            rows = cursor.fetchall()

            print('Retrieved rows:')
            for row in rows:
                print(row)

        except Exception as e:  # noqa
            print(f'Unexpected error: {e}')
