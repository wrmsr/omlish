"""
TODO:
 - dedicated single thread executor (current makes no guarantee about getting same thread)
"""
import concurrent.futures as cf
import contextlib
import sqlite3
import typing as ta

import pytest

from ....asyncs.asyncio import all as au
from ...queries import Q
from .. import querierfuncs as qf
from ..asyncs import SyncToAsyncDb
from ..dbapi import DbapiDb


@pytest.mark.asyncs('asyncio')
async def test_queries():
    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = DbapiDb(lambda: contextlib.closing(sqlite3.connect(':memory:')))
        adb = SyncToAsyncDb(ta.cast(ta.Any, au.ToThread(exe=exe)), db)

        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

        print(await qf.query_all(adb, Q.select([1])))
