import contextlib
import sqlite3

from .. import querierfuncs as qf
from ...params import ParamStyle
from ...queries import Q
from ..dbapi import DbapiDb


##


def test_sqlite(exit_stack) -> None:
    db = DbapiDb(
        lambda: contextlib.closing(sqlite3.connect(':memory:', autocommit=True)),
        param_style=ParamStyle.QMARK,
    )
    conn = exit_stack.enter_context(db.connect())

    assert qf.query_scalar(conn, Q.select([Q.add(Q.p.x, 1)]), {Q.p.x: 2}) == 3
