import sqlite3

from ..... import check
from ....api import querierfuncs as qf
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....dtypes import Integer
from ....dtypes import String
from ....params import ParamStyle
from ....tabledefs.diffing import AddColumn
from ....tabledefs.diffing import diff_table
from ....tabledefs.elements import Column
from ....tabledefs.elements import Elements
from ....tabledefs.elements import PrimaryKey
from ....tabledefs.tabledefs import TableDef
from ..inspect import SqliteInspector
from ..tabledefs import SqliteStatementRenderer


def test_inspect_diff_apply(exit_stack) -> None:
    db = DbapiDb(ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True), param_style=ParamStyle.QMARK)
    conn = exit_stack.enter_context(db.connect())
    r = SqliteStatementRenderer()
    insp = SqliteInspector()

    # create the "current db" schema (missing the email column)
    existing = TableDef('users', Elements(Column('id', Integer()), PrimaryKey(['id'])))
    for s in r.render_create_statements(existing):
        qf.exec(conn, s)

    # the in-code definition has grown a column
    current = TableDef('users', Elements(
        Column('id', Integer()),
        PrimaryKey(['id']),
        Column('email', String(), nullable=True),
    ))

    # reflect the live db, lift it back to a tabledef, and diff
    reflected = insp.lift_table(check.not_none(insp.reflect_table(conn, 'users')))
    ops = diff_table(current, reflected)
    assert [type(o) for o in ops] == [AddColumn]

    # apply the migration
    for op in ops:
        for s in r.render_migration(op):
            qf.exec(conn, s)

    # the column now exists
    reflected2 = check.not_none(insp.reflect_table(conn, 'users'))
    assert {c.name for c in reflected2.columns} == {'id', 'email'}
