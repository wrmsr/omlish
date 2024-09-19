from ..storage import Storage
from ..types import CacheEntry
from ..types import CacheKey


class SqliteStorage(Storage):
    def __init__(self) -> None:
        super().__init__()

    def get(self, key: CacheKey) -> CacheEntry | None:
        raise NotImplementedError

    def put(self, entry: CacheEntry) -> None:
        raise NotImplementedError

    def delete(self, key: CacheKey) -> None:
        raise NotImplementedError


def test_sql_storage():
    pass
