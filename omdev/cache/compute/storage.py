import abc

from .types import CacheEntry
from .types import CacheKey


class Storage(abc.ABC):
    @abc.abstractmethod
    def get(self, key: CacheKey) -> CacheEntry | None:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, entry: CacheEntry) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key: CacheKey) -> None:
        raise NotImplementedError


class DictStorage(Storage):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[CacheKey, CacheEntry] = {}

    def get(self, key: CacheKey) -> CacheEntry | None:
        try:
            return self._dct[key]
        except KeyError:
            return None

    def put(self, entry: CacheEntry) -> None:
        if entry.key in self._dct:
            raise KeyError(entry.key)
        self._dct[entry.key] = entry

    def delete(self, key: CacheKey) -> None:
        del self._dct[key]
