from ...syntax import QuoteStyles
from ..base import Backend
from ..mysql.adapters import mysql_adapter
from ..mysql.backend import MysqlBackend
from ..mysql.dialect import MysqlDialect
from ..mysql.inspect import MysqlInspector
from ..mysql.tabledefs import MysqlTabledefRenderer
from ..postgres.adapters import postgres_adapter
from ..postgres.backend import PostgresBackend
from ..postgres.dialect import PostgresDialect
from ..postgres.inspect import PostgresInspector
from ..postgres.tabledefs import PostgresTabledefRenderer
from ..sqlite.adapters import sqlite_adapter
from ..sqlite.backend import SqliteBackend
from ..sqlite.dialect import SqliteDialect
from ..sqlite.inspect import SqliteInspector
from ..sqlite.tabledefs import SqliteTabledefRenderer


def test_postgres_backend():
    b = PostgresBackend()
    assert isinstance(b, Backend)
    assert isinstance(b.dialect, PostgresDialect)
    assert isinstance(b.tabledef_renderer, PostgresTabledefRenderer)
    assert isinstance(b.inspector, PostgresInspector)


def test_sqlite_backend():
    b = SqliteBackend()
    assert isinstance(b.dialect, SqliteDialect)
    assert isinstance(b.tabledef_renderer, SqliteTabledefRenderer)
    assert isinstance(b.inspector, SqliteInspector)


def test_mysql_backend():
    b = MysqlBackend()
    assert isinstance(b.dialect, MysqlDialect)
    assert isinstance(b.tabledef_renderer, MysqlTabledefRenderer)
    assert isinstance(b.inspector, MysqlInspector)


def test_adapter_factories_carry_dialect():
    # the dialect facets (capabilities, quoting) flow up through the adapter
    assert sqlite_adapter().supports_returning is True
    assert postgres_adapter().supports_returning is True
    assert mysql_adapter().supports_returning is False
    assert mysql_adapter().quote_style == QuoteStyles.BACKTICK
