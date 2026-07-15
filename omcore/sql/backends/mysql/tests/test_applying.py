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
from ....tabledefs.diffing import AlterColumn
from ....tabledefs.elements import Column
from ....tabledefs.elements import Elements
from ....tabledefs.elements import Index
from ....tabledefs.elements import PrimaryKey
from ....tabledefs.tabledefs import TableDef
from ....tests.harness import HarnessDbs
from ..inspect import MysqlInspector
from ..tabledefs import MysqlTabledefRenderer


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
    r = MysqlTabledefRenderer()
    insp = MysqlInspector()
    tn = 'test_migrate_table'

    async def inner() -> None:
        async with adb.connect() as conn:
            await qf.exec(conn, 'create database if not exists om_test')
            await qf.exec(conn, 'use om_test')
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


@ptu.skip.if_cant_import('pymysql')
def test_migrate_table_with_index(harness) -> None:
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
    r = MysqlTabledefRenderer()
    insp = MysqlInspector()
    tn = 'test_migrate_table_with_index'

    async def inner() -> None:
        async with adb.connect() as conn:
            await qf.exec(conn, 'create database if not exists om_test')
            await qf.exec(conn, 'use om_test')
            await qf.exec(conn, f'drop table if exists {tn}')

            # mysql can't index a String (-> TEXT) column without a key length, so index an integer column here
            td = TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('qty', Integer(), nullable=True),
                Index(['qty']),
            ))
            m1 = await migrate_table(conn, td, inspector=insp, renderer=r)
            assert m1.created

            # the index reflects + lifts, so a second run is a true no-op (no spurious index re-create)
            m2 = await migrate_table(conn, td, inspector=insp, renderer=r)
            assert not m2.created
            assert not m2.ops

            await qf.exec(conn, f'drop table if exists {tn}')

    lang.sync_await(inner())


@ptu.skip.if_cant_import('pymysql')
def test_migrate_table_alter_column(harness) -> None:
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
    r = MysqlTabledefRenderer()
    insp = MysqlInspector()
    tn = 'test_migrate_table_alter_column'

    async def inner() -> None:
        async with adb.connect() as conn:
            await qf.exec(conn, 'create database if not exists om_test')
            await qf.exec(conn, 'use om_test')
            await qf.exec(conn, f'drop table if exists {tn}')

            await migrate_table(conn, TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('val', Integer(), nullable=True),
            )), inspector=insp, renderer=r)

            # change val's type Integer -> String; mysql applies the alter via MODIFY, then a re-run is a no-op
            grown = TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('val', String(), nullable=True),
            ))
            m = await migrate_table(conn, grown, inspector=insp, renderer=r)
            assert [type(o) for o in m.ops] == [AlterColumn]

            m2 = await migrate_table(conn, grown, inspector=insp, renderer=r)
            assert not m2.ops

            await qf.exec(conn, f'drop table if exists {tn}')

    lang.sync_await(inner())
