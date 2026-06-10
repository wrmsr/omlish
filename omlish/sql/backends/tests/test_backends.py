from ..base import Backend
from ..mysql.backend import MysqlBackend
from ..mysql.dialect import MysqlDialect
from ..mysql.inspect import MysqlInspector
from ..mysql.tabledefs import MysqlStatementRenderer
from ..postgres.backend import PostgresBackend
from ..postgres.dialect import PostgresDialect
from ..postgres.inspect import PostgresInspector
from ..postgres.tabledefs import PostgresStatementRenderer
from ..sqlite.backend import SqliteBackend
from ..sqlite.dialect import SqliteDialect
from ..sqlite.inspect import SqliteInspector
from ..sqlite.tabledefs import SqliteStatementRenderer


def test_postgres_backend():
    b = PostgresBackend()
    assert isinstance(b, Backend)
    assert isinstance(b.dialect, PostgresDialect)
    assert isinstance(b.statement_renderer, PostgresStatementRenderer)
    assert isinstance(b.inspector, PostgresInspector)


def test_sqlite_backend():
    b = SqliteBackend()
    assert isinstance(b.dialect, SqliteDialect)
    assert isinstance(b.statement_renderer, SqliteStatementRenderer)
    assert isinstance(b.inspector, SqliteInspector)


def test_mysql_backend():
    b = MysqlBackend()
    assert isinstance(b.dialect, MysqlDialect)
    assert isinstance(b.statement_renderer, MysqlStatementRenderer)
    assert isinstance(b.inspector, MysqlInspector)
