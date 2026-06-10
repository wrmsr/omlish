import typing as ta
import urllib.parse

from ..... import check
from ..... import lang
from .....testing import pytest as ptu
from ....api import querierfuncs as qf
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
from ..tabledefs import PostgresStatementRenderer


if ta.TYPE_CHECKING:
    import pg8000
else:
    pg8000 = lang.proxy_import('pg8000')


@ptu.skip.if_cant_import('pg8000')
def test_inspect_diff_apply(harness, exit_stack) -> None:
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
    conn = exit_stack.enter_context(db.connect())

    r = PostgresStatementRenderer()
    insp = PostgresInspector()
    tn = 'test_inspect_diff_apply'

    qf.exec(conn, f'drop table if exists {tn} cascade')
    existing = TableDef(tn, Elements(Column('id', Integer()), PrimaryKey(['id'])))
    for s in r.render_create_statements(existing):
        qf.exec(conn, s)

    current = TableDef(tn, Elements(
        Column('id', Integer()),
        PrimaryKey(['id']),
        Column('email', String(), nullable=True),
    ))

    reflected = insp.lift_table(check.not_none(insp.reflect_table(conn, tn)))
    ops = diff_table(current, reflected)
    assert [type(o) for o in ops] == [AddColumn]

    for op in ops:
        for s in r.render_migration(op):
            qf.exec(conn, s)

    reflected2 = check.not_none(insp.reflect_table(conn, tn))
    assert {c.name for c in reflected2.columns} == {'id', 'email'}

    qf.exec(conn, f'drop table if exists {tn} cascade')
