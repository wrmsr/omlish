import concurrent.futures as cf
import sqlite3

import pytest

from ..... import lang
from ....api import querierfuncs as qf
from ....api.asyncs import AsyncioToExecutorSyncToAsyncRunner
from ....api.asyncs import ImmediateSyncToAsyncRunner
from ....api.asyncs import SyncToAsyncDb
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....queries import Q


@pytest.mark.asyncs('asyncio')
async def test_queries():
    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:'))
        adb = SyncToAsyncDb(AsyncioToExecutorSyncToAsyncRunner.factory(exe), db)

        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

        print(await qf.query_all(adb, Q.select([1])))


def test_immediate_queries():
    db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:'))
    adb = SyncToAsyncDb(ImmediateSyncToAsyncRunner, db)

    async def inner():
        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

        print(await qf.query_all(adb, Q.select([1])))

    lang.sync_await(inner())
