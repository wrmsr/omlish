import sqlite3

from ....api import querierfuncs as qf
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....params import ParamStyle
from ....queries import Q


##


def test_sqlite(exit_stack) -> None:
    db = DbapiDb(
        ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True),
        param_style=ParamStyle.QMARK,
    )
    conn = exit_stack.enter_context(db.connect())

    assert qf.query_scalar(conn, Q.select([Q.add(Q.p.x, 1)]), {Q.p.x: 2}) == 3
