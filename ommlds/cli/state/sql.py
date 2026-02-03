import typing as ta

from omlish import sql
from omlish.sql import Q

from .storage import MarshalStateStorage


T = ta.TypeVar('T')


##


class SqlStateStorage(MarshalStateStorage):
    def __init__(self, db: sql.api.AsyncDb) -> None:
        super().__init__()

        self._db = db

    async def load_state(self, key: str, ty: type[T] | None) -> T | None:
        row = sql.api.query_opt_one(self._db, Q.select([Q.n.value], Q.n.states, Q.eq(Q.n.key, key)))  # noqa
        raise NotImplementedError

    async def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        raise NotImplementedError
