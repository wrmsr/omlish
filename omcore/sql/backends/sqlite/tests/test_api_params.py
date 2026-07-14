import sqlite3

from ....api import querierfuncs as qf
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....params import ParamStyle
from ....queries import Q


def _db() -> DbapiDb:
    return DbapiDb(
        ClosingDbapiConnector(sqlite3.connect, ':memory:', autocommit=True),
        param_style=ParamStyle.QMARK,
    )


def test_string_positional_params(exit_stack) -> None:
    conn = exit_stack.enter_context(_db().connect())
    assert qf.query_scalar(conn, 'select ? + ?', [2, 3]) == 5


def test_stmt_params(exit_stack) -> None:
    conn = exit_stack.enter_context(_db().connect())
    assert qf.query_scalar(conn, Q.select([Q.add(Q.p.x, Q.p.y)]), {Q.p.x: 2, Q.p.y: 3}) == 5


def test_exec_many_string(exit_stack) -> None:
    conn = exit_stack.enter_context(_db().connect())
    qf.exec(conn, 'create table t (a integer, b text)')
    qf.exec_many(conn, 'insert into t (a, b) values (?, ?)', [[1, 'x'], [2, 'y'], [3, 'z']])
    rows = qf.query_all(conn, 'select a, b from t order by a')
    assert [tuple(r.values) for r in rows] == [(1, 'x'), (2, 'y'), (3, 'z')]


def test_exec_many_stmt(exit_stack) -> None:
    conn = exit_stack.enter_context(_db().connect())
    qf.exec(conn, 'create table t2 (a integer, b integer)')
    qf.exec_many(
        conn,
        Q.insert(['a', 'b'], Q.n.t2, [Q.p.a, Q.p.b]),
        [{Q.p.a: 1, Q.p.b: 10}, {Q.p.a: 2, Q.p.b: 20}],
    )
    assert qf.query_scalar(conn, 'select sum(b) from t2') == 30
