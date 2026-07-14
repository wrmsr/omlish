from ...api.dialects import Dialect


##


class PostgresDialect(Dialect):
    @property
    def supports_returning(self) -> bool:
        return True
