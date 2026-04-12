"""
TODO:
 - dedicated single thread executor (current makes no guarantee about getting same thread)
"""
import concurrent.futures as cf
import contextlib
import sqlite3
import typing as ta
import urllib.parse

import pytest

from .... import check
from .... import lang
from ....asyncs.asyncio import all as au
from ....testing import pytest as ptu
from ...dbs import UrlDbLoc
from ...queries import Q
from ...tests.harness import HarnessDbs
from .. import querierfuncs as qf
from ..asyncs import SyncToAsyncDb
from ..dbapi import DbapiDb


@pytest.mark.asyncs('asyncio')
async def test_queries():
    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = DbapiDb(lambda: contextlib.closing(sqlite3.connect(':memory:')))
        adb = SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)

        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

        print(await qf.query_all(adb, Q.select([1])))


@pytest.mark.asyncs('asyncio')
@ptu.skip.if_cant_import('pg8000')
async def test_pg8000(harness):
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pg8000

    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = DbapiDb(lambda: contextlib.closing(pg8000.connect(
            p_u.username,
            host=p_u.hostname,
            port=p_u.port,
            password=p_u.password,
        )))
        adb = SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)

        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

        print(await qf.query_all(adb, Q.select([1])))


# @pytest.mark.asyncs('asyncio')
# @ptu.skip.if_cant_import('asyncpg')
# async def test_asyncpg(harness):
#     url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
#     p_u = urllib.parse.urlparse(url)
#
#     with cf.ThreadPoolExecutor(max_workers=1) as exe:
#         db = DbapiDb(lambda: contextlib.closing(sqlite3.connect(':memory:')))
#         adb = SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)
#
#         async with adb.connect() as conn:
#             print(await qf.query_all(conn, Q.select([1])))
#
#         print(await qf.query_all(adb, Q.select([1])))
