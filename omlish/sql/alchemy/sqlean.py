import sqlalchemy as sa
from sqlalchemy.dialects import sqlite as sal


class SqleanDialect(sal.dialect):  # type: ignore
    name = 'sqlite__sqlean'
    driver = 'sqlean_engine'

    supports_statement_cache = True

    @classmethod
    def import_dbapi(cls):
        from sqlean import dbapi2
        return dbapi2


sa.dialects.registry.register(SqleanDialect.name, __name__, SqleanDialect.__name__)
