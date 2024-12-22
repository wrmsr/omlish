import typing as ta
import urllib.parse

from ... import check
from ... import lang
from ...testing import pytest as ptu
from ..dbs import UrlDbLoc
from .harness import HarnessDbs


if ta.TYPE_CHECKING:
    import pg8000
else:
    pg8000 = lang.proxy_import('pg8000')


@ptu.skip.if_cant_import('pg8000')
def test_pg(harness):
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    pu = urllib.parse.urlparse(url)

    try:
        # Connect to the PostgreSQL database
        conn = pg8000.connect(
            host=pu.hostname,
            database='postgres',
            user=pu.username,
            password=pu.password,
            port=pu.port,
        )

        print('Connected to the database!')

        # Create a cursor
        cursor = conn.cursor()

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

        # Close the cursor and connection
        cursor.close()
        conn.close()
        print('Database connection closed.')

    except pg8000.exceptions.InterfaceError as e:
        print(f'Error connecting to the database: {e}')
    except pg8000.exceptions.DatabaseError as e:
        print(f'Database error: {e}')
    except Exception as e:  # noqa
        print(f'Unexpected error: {e}')
