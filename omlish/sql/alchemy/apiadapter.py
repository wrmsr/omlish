import sqlalchemy as sa

from .. import api


##

class SqlalchemyRows(api.Rows):
    @property
    def columns(self) -> api.Columns:
        raise NotImplementedError

    def __next__(self) -> api.Row:
        raise NotImplementedError


class SqlalchemyConn(api.Conn):
    def __init__(self, conn: sa.engine.Connection) -> None:
        super().__init__()

        self._sa_conn = conn

    @property
    def adapter(self) -> api.Adapter:
        raise NotImplementedError

    def query(self, query: api.Query) -> api.Rows:
        raise NotImplementedError


class SqlalchemyDb(api.Db):
    def __init__(self, engine: sa.engine.Engine) -> None:
        super().__init__()

        self._sa_engine = engine

    def connect(self) -> api.Conn:
        raise NotImplementedError

    @property
    def adapter(self) -> api.Adapter:
        raise NotImplementedError


class SqlalchemyAdapter(api.Adapter):
    def scan_type(self, c: api.Column) -> type:
        raise NotImplementedError
