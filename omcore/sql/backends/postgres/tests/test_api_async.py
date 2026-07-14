import concurrent.futures as cf
import contextlib
import typing as ta
import urllib.parse

import pytest

from ..... import check
from ..... import lang
from .....asyncs.asyncio import all as au
from .....testing import pytest as ptu
from ....api import querierfuncs as qf
from ....api.asyncs import SyncToAsyncDb
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....dbs import UrlDbLoc
from ....queries import Q
from ....tests.harness import HarnessDbs
from ..drivers.asyncpg import AsyncpgDb


@pytest.mark.asyncs('asyncio')
@ptu.skip.if_cant_import('pg8000')
async def test_pg8000(harness):
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pg8000

    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = DbapiDb(ClosingDbapiConnector(
            pg8000.connect,
            p_u.username,
            host=p_u.hostname,
            port=p_u.port,
            password=p_u.password,
        ))
        adb = SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToExecutor(exe))), db)

        async with adb.connect() as conn:
            print(await qf.query_all(conn, Q.select([1])))

            # FIXME: :|||
            # print(await qf.query_all(
            #     conn,
            #     qf.as_query(
            #         Q.select([Q.p.barf]),
            #         adapter=DbapiAdapter(
            #             param_style=ParamStyle.FORMAT,
            #         ),
            #     ),
            #     {Q.p.barf: 420},
            # ))

        print(await qf.query_all(adb, Q.select([1])))


@pytest.mark.asyncs('asyncio')
@ptu.skip.if_cant_import('asyncpg')
async def test_asyncpg(harness):
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import asyncpg

    @contextlib.asynccontextmanager
    async def asyncpg_connect(
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.AsyncIterator[asyncpg.Connection]:
        conn = await asyncpg.connect(*args, **kwargs)
        try:
            yield conn
        finally:
            await conn.close()

    adb = AsyncpgDb(
        lambda: asyncpg_connect(
            user=p_u.username,
            host=p_u.hostname,
            port=p_u.port,
            password=p_u.password,
        ),
    )

    async with adb.connect() as conn:
        print(await qf.query_all(conn, Q.select([1])))

        # FIXME: :|||
        # print(await qf.query_all(conn, Q.select([Q.p.barf]), {Q.p.barf: 420}))

    print(await qf.query_all(adb, Q.select([1])))
