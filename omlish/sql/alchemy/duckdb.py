"""
See:
 - https://duckdb.org/docs/api/python/overview.html
 - https://github.com/Mause/duckdb_engine/blob/0e3ea0107f81c66d50b444011d31fce22a9b902c/duckdb_engine/__init__.py
"""
import typing as ta

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sap

from ... import lang


if ta.TYPE_CHECKING:
    import duckdb
else:
    duckdb = lang.proxy_import('duckdb')


##


class ConnectionWrapper:
    def __init__(self, c: 'duckdb.DuckDBPyConnection') -> None:
        super().__init__()

        self.__c = c
        self.autocommit = None
        self.closed = False

    def cursor(self) -> 'CursorWrapper':
        return CursorWrapper(self.__c, self)

    def __getattr__(self, name: str) -> ta.Any:
        return getattr(self.__c, name)

    def close(self) -> None:
        self.__c.close()
        self.closed = True


def _is_transaction_context_message(e: Exception) -> bool:
    return e.args[0] == 'TransactionContext Error: cannot rollback - no transaction is active'


class CursorWrapper:
    def __init__(
            self,
            c: 'duckdb.DuckDBPyConnection',
            connection_wrapper: 'ConnectionWrapper',
    ) -> None:
        super().__init__()

        self.__c = c
        self.__connection_wrapper = connection_wrapper

    def executemany(
        self,
        statement: str,
        parameters: ta.Sequence[ta.Mapping[str, ta.Any]] | None = None,
        context: ta.Any | None = None,
    ) -> None:
        self.__c.executemany(statement, list(parameters) if parameters else [])

    def execute(
        self,
        statement: str,
        parameters: ta.Sequence[ta.Any] | None = None,
        context: ta.Any | None = None,
    ) -> None:
        try:
            if statement.lower() == 'commit':  # this is largely for ipython-sql
                self.__c.commit()
            elif parameters is None:
                self.__c.execute(statement)
            else:
                self.__c.execute(statement, parameters)
        except RuntimeError as e:
            if e.args[0].startswith('Not implemented Error'):
                raise NotImplementedError(*e.args) from e
            elif _is_transaction_context_message(e):
                return
            else:
                raise

    @property
    def connection(self):
        return self.__connection_wrapper

    def close(self) -> None:
        pass

    def __getattr__(self, name: str) -> ta.Any:
        return getattr(self.__c, name)

    def fetchmany(self, size: int | None = None) -> list:
        if size is None:
            return self.__c.fetchmany()
        else:
            return self.__c.fetchmany(size)


class DuckdbDialect(sap.base.PGDialect):
    name = 'postgres__duckdb'
    driver = 'duckdb_engine'

    supports_statement_cache = False

    @classmethod
    def import_dbapi(cls):
        return duckdb

    def connect(self, *cargs, **cparams):
        conn = self.loaded_dbapi.connect(*cargs, **cparams)

        return ConnectionWrapper(conn)

    def do_rollback(self, connection) -> None:
        try:
            super().do_rollback(connection)
        except duckdb.TransactionException as e:
            if _is_transaction_context_message(e):
                return
            else:
                raise

    def do_begin(self, connection) -> None:
        connection.begin()

    def get_default_isolation_level(self, connection) -> ta.Any:
        raise NotImplementedError

    def _get_server_version_info(self, connection) -> tuple[int, int]:
        connection.execute(sa.text('select version()')).fetchone()
        return (8, 0)

    def _set_backslash_escapes(self, connection):
        pass


sa.dialects.registry.register(DuckdbDialect.name, __name__, DuckdbDialect.__name__)
