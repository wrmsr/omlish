from ...api.dialects import Dialect


##


class SqliteDialect(Dialect):
    @property
    def supports_returning(self) -> bool:
        return True
