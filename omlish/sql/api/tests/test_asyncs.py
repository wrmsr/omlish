import asyncio
import sqlite3
import typing as ta

import pytest

from ...queries import Q
from .. import querierfuncs as qf
from ..asyncs import SyncToAsyncDb
from ..dbapi import DbapiDb


@pytest.mark.asyncs('asyncio')
async def test_queries():
    with DbapiDb(lambda: sqlite3.connect(':memory:')) as db:
        adb = SyncToAsyncDb(ta.cast(ta.Any, asyncio.to_thread), db)

        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

        print(await qf.query_all(adb, Q.select([1])))
