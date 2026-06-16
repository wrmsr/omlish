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
from ....params import ParamStyle
from ....tabledefs.diffing import AddColumn
from ....tabledefs.diffing import diff_table
from ....tabledefs.elements import Column
from ....tabledefs.elements import Elements
from ....tabledefs.elements import PrimaryKey
from ....tabledefs.tabledefs import TableDef
from ....tests.harness import HarnessDbs
from ..inspect import PostgresInspector
from ..tabledefs import PostgresTabledefRenderer


if ta.TYPE_CHECKING:
    import pg8000
else:
    pg8000 = lang.proxy_import('pg8000')


@ptu.skip.if_cant_import('pg8000')
def test_inspect_diff_apply(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    pu = urllib.parse.urlparse(url)

    db = DbapiDb(
        ClosingDbapiConnector(
            pg8000.connect,
            pu.username,
            host=pu.hostname,
            port=pu.port,
            password=pu.password,
            database='postgres',
        ),
        param_style=ParamStyle.FORMAT,
    )
    adb = SyncToAsyncDb(ImmediateSyncToAsyncRunner, db)

    r = PostgresTabledefRenderer()
    insp = PostgresInspector()
    tn = 'test_inspect_diff_apply'

    # the inspector is async-only; the sync pg8000 db is lifted into async (immediate, in-thread) and driven via
    # lang.sync_await - no event loop, since nothing ever suspends.
    async def inner() -> None:
        async with adb.connect() as conn:
            await qf.exec(conn, f'drop table if exists {tn} cascade')
            existing = TableDef(tn, Elements(Column('id', Integer()), PrimaryKey(['id'])))
            for s in r.render_create_statements(existing):
                await qf.exec(conn, s)

            current = TableDef(tn, Elements(
                Column('id', Integer()),
                PrimaryKey(['id']),
                Column('email', String(), nullable=True),
            ))

            reflected = insp.lift_table(check.not_none(await insp.reflect_table(conn, tn)))
            ops = diff_table(current, reflected)
            assert [type(o) for o in ops] == [AddColumn]

            for op in ops:
                for s in r.render_migration(op):
                    await qf.exec(conn, s)

            reflected2 = check.not_none(await insp.reflect_table(conn, tn))
            assert {c.name for c in reflected2.columns} == {'id', 'email'}

            await qf.exec(conn, f'drop table if exists {tn} cascade')

    lang.sync_await(inner())
