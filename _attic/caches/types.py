import abc
import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')


class OverweightException(Exception):
    pass


class Cache(ta.MutableMapping[K, V]):
    """
    https://google.github.io/guava/releases/16.0/api/docs/com/google/common/cache/CacheBuilder.html
    """

    Eviction = ta.Callable[['Cache'], None]

    @abc.abstractmethod
    def reap(self) -> None:
        pass

    class Stats(ta.NamedTuple):
        seq: int
        size: int
        weight: float
        hits: int
        misses: int
        max_size_ever: int
        max_weight_ever: float

    @abc.abstractproperty
    def stats(self) -> Stats:
        raise NotImplementedError
