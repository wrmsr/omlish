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
from ..tabledefs import MysqlTabledefRenderer


if ta.TYPE_CHECKING:
    import pymysql
else:
    pymysql = lang.proxy_import('pymysql')


@ptu.skip.if_cant_import('pymysql')
def test_render_create_table(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['mysql'].loc, UrlDbLoc).url, str)
    pu = urllib.parse.urlparse(url)

    with contextlib.ExitStack() as es:
        conn = es.enter_context(contextlib.closing(pymysql.connect(
            host=pu.hostname,
            port=check.not_none(pu.port),
            user=pu.username,
            password=check.not_none(pu.password),
        )))
        cursor = es.enter_context(contextlib.closing(conn.cursor()))

        cursor.execute('create database if not exists omlish_test')
        cursor.execute('use omlish_test')
        cursor.execute('drop table if exists test_render_create_table')

        tbl = lower_table_elements(TableDef('test_render_create_table', Elements(
            IdIntegerPrimaryKey(),
            CreatedAtUpdatedAt(),
            Column('name', String()),
        )))

        for s in MysqlTabledefRenderer().render_create_statements(tbl):
            cursor.execute(s)

        conn.commit()
