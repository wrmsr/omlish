import sqlalchemy as sa
from sqlalchemy.dialects import sqlite as sal


DIALECT_NAME = 'sqlite__sqlean'


class SqleanDialect(sal.dialect):  # type: ignore
    supports_statement_cache = True

    @classmethod
    def import_dbapi(cls):
        from sqlean import dbapi2
        return dbapi2


sa.dialects.registry.register(DIALECT_NAME, __name__, SqleanDialect.__name__)
