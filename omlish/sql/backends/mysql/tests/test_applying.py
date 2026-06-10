import typing as ta
import urllib.parse

from ..... import check
from ..... import lang
from .....testing import pytest as ptu
from ....api import querierfuncs as qf
from ....api.asyncs import ImmediateSyncToAsyncRunner
from ....api.asyncs import SyncToAsyncDb
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....dbs import UrlDbLoc
from ....dtypes import Integer
from ....dtypes import String
from ....inspect.migrating import migrate_table
from ....params import ParamStyle
from ....tabledefs.diffing import AddColumn
from ....tabledefs.elements import Column
from ....tabledefs.elements import Elements
from ....tabledefs.elements import PrimaryKey
from ....tabledefs.tabledefs import TableDef
from ....tests.harness import HarnessDbs
from ..inspect import MysqlInspector
from ..tabledefs import MysqlStatementRenderer


if ta.TYPE_CHECKING:
    import pymysql
else:
    pymysql = lang.proxy_import('pymysql')


@ptu.skip.if_cant_import('pymysql')
def test_migrate_table(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['mysql'].loc, UrlDbLoc).url, str)
    pu = urllib.parse.urlparse(url)

    db = DbapiDb(
        ClosingDbapiConnector(
            ta.cast(ta.Any, pymysql.connect),  # typed pymysql.connect won't unify with the connector ParamSpec
            host=pu.hostname,
            port=check.not_none(pu.port),
            user=pu.username,
            password=check.not_none(pu.password),
            autocommit=True,
        ),
        param_style=ParamStyle.PYFORMAT,
    )
    adb = SyncToAsyncDb(ImmediateSyncToAsyncRunner, db)
    r = MysqlStatementRenderer()
    insp = MysqlInspector()
    tn = 'test_migrate_table'

    async def inner() -> None:
        async with adb.connect() as conn:
            await qf.exec(conn, 'create database if not exists omlish_test')
            await qf.exec(conn, 'use omlish_test')
            await qf.exec(conn, f'drop table if exists {tn}')

            base = TableDef(tn, Elements(Column('id', Integer()), PrimaryKey(['id'])))
            m1 = await migrate_table(conn, base, inspector=insp, renderer=r)
            assert m1.created
            assert not m1.ops

            grown = TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('email', String(), nullable=True),
            ))
            m2 = await migrate_table(conn, grown, inspector=insp, renderer=r)
            assert not m2.created
            assert [type(o) for o in m2.ops] == [AddColumn]

            m3 = await migrate_table(conn, grown, inspector=insp, renderer=r)
            assert not m3.created
            assert not m3.ops

            await qf.exec(conn, f'drop table if exists {tn}')

    lang.sync_await(inner())
