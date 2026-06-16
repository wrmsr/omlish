import sqlite3

import pytest

from ..... import lang
from ....api.asyncs import ImmediateSyncToAsyncRunner
from ....api.asyncs import SyncToAsyncDb
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....dtypes import Integer
from ....dtypes import String
from ....inspect.migrating import migrate_table
from ....params import ParamStyle
from ....tabledefs.diffing import AddColumn
from ....tabledefs.elements import Column
from ....tabledefs.elements import Elements
from ....tabledefs.elements import Index
from ....tabledefs.elements import PrimaryKey
from ....tabledefs.rendering import UnsupportedMigrationError
from ....tabledefs.tabledefs import TableDef
from ..inspect import SqliteInspector
from ..tabledefs import SqliteTabledefRenderer


def test_migrate_table() -> None:
    async def inner() -> None:
        db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True), param_style=ParamStyle.QMARK)
        adb = SyncToAsyncDb(ImmediateSyncToAsyncRunner, db)
        r = SqliteTabledefRenderer()
        insp = SqliteInspector()
        tn = 'users'

        async with adb.connect() as conn:
            base = TableDef(tn, Elements(Column('id', Integer()), PrimaryKey(['id'])))

            # first run creates the table wholesale
            m1 = await migrate_table(conn, base, inspector=insp, renderer=r)
            assert m1.created
            assert not m1.ops

            # the in-code definition has grown a column -> one AddColumn is applied
            grown = TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('email', String(), nullable=True),
            ))
            m2 = await migrate_table(conn, grown, inspector=insp, renderer=r)
            assert not m2.created
            assert [type(o) for o in m2.ops] == [AddColumn]

            # idempotent: re-running against the now-current db is a no-op
            m3 = await migrate_table(conn, grown, inspector=insp, renderer=r)
            assert not m3.created
            assert not m3.ops

    lang.sync_await(inner())


def test_migrate_table_with_index() -> None:
    async def inner() -> None:
        db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True), param_style=ParamStyle.QMARK)
        adb = SyncToAsyncDb(ImmediateSyncToAsyncRunner, db)
        r = SqliteTabledefRenderer()
        insp = SqliteInspector()
        tn = 'widget'

        async with adb.connect() as conn:
            td = TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('email', String(), nullable=True),
                Index(['email']),
            ))

            m1 = await migrate_table(conn, td, inspector=insp, renderer=r)
            assert m1.created

            # the index reflects + lifts now, so a second run is a true no-op (no spurious index re-create)
            m2 = await migrate_table(conn, td, inspector=insp, renderer=r)
            assert not m2.created
            assert not m2.ops

    lang.sync_await(inner())


def test_migrate_table_type_change_refused() -> None:
    async def inner() -> None:
        db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True), param_style=ParamStyle.QMARK)
        adb = SyncToAsyncDb(ImmediateSyncToAsyncRunner, db)
        r = SqliteTabledefRenderer()
        insp = SqliteInspector()
        tn = 'gadget'

        async with adb.connect() as conn:
            await migrate_table(conn, TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('val', Integer(), nullable=True),
            )), inspector=insp, renderer=r)

            # the in-code column type changed Integer -> String; sqlite cannot alter a column in place, so it refuses
            with pytest.raises(UnsupportedMigrationError):
                await migrate_table(conn, TableDef(tn, Elements(
                    Column('id', Integer()),
                    PrimaryKey(['id']),
                    Column('val', String(), nullable=True),
                )), inspector=insp, renderer=r)

    lang.sync_await(inner())
