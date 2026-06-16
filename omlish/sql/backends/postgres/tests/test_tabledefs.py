import contextlib
import typing as ta
import urllib.parse

from ..... import check
from ..... import lang
from .....testing import pytest as ptu
from ....dbs import UrlDbLoc
from ....dtypes import String
from ....tabledefs.elements import Column
from ....tabledefs.elements import CreatedAtUpdatedAt
from ....tabledefs.elements import Elements
from ....tabledefs.elements import IdIntegerPrimaryKey
from ....tabledefs.lower import lower_table_elements
from ....tabledefs.tabledefs import TableDef
from ....tests.harness import HarnessDbs
from ..tabledefs import PostgresTabledefRenderer


if ta.TYPE_CHECKING:
    import pg8000
else:
    pg8000 = lang.proxy_import('pg8000')


@ptu.skip.if_cant_import('pg8000')
def test_render_create_table(harness):
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    pu = urllib.parse.urlparse(url)

    with contextlib.ExitStack() as es:
        # Connect to the PostgreSQL database
        conn: pg8000.Connection = es.enter_context(contextlib.closing(pg8000.connect(  # noqa
            host=pu.hostname,
            database='postgres',
            user=pu.username,
            password=pu.password,
            port=pu.port,
        )))

        cursor: pg8000.Cursor = es.enter_context(contextlib.closing(conn.cursor()))  # noqa

        cursor.execute('drop table if exists test_render_create_table')

        tbl = TableDef(
            'test_render_create_table',
            Elements(*[
                IdIntegerPrimaryKey(),
                CreatedAtUpdatedAt(),
                Column('name', String()),
            ]),
        )

        tbl = lower_table_elements(tbl)

        stmts = PostgresTabledefRenderer().render_create_statements(tbl)

        print('\n\n'.join(stmts))

        for stmt in stmts:
            cursor.execute(stmt)

        cursor.execute('commit')
