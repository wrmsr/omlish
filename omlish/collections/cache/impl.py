"""
TODO:
 - dogpile
 - midpoint/arc
 - heapq/etc powered lfu
 - thread scoped?
 - __sizeof__ interop
 - further cythonize hot path?
"""
import collections
import contextlib
import functools
import time
import typing as ta
import weakref

from ... import lang
from ...logs import all as logs
from .types import Cache
from .types import Eviction
from .types import OverweightError


K = ta.TypeVar('K')
K2 = ta.TypeVar('K2')
V = ta.TypeVar('V')
V2 = ta.TypeVar('V2')


log = logs.get_module_logger(globals())


##


class SKIP(lang.Marker):
    pass


def LRU(cache: 'Cache') -> None:  # noqa
    cache._kill(cache._root.lru_next)  # type: ignore  # noqa


# aka FIFO
def LRI(cache: 'Cache') -> None:  # noqa
    cache._kill(cache._root.ins_next)  # type: ignore  # noqa


def LFU(cache: 'Cache') -> None:  # noqa
    cache._kill(cache._root.lfu_prev)  # type: ignore  # noqa


class CacheImpl(Cache[K, V]):
    """
    https://google.github.io/guava/releases/16.0/api/docs/com/google/common/cache/CacheBuilder.html
    """

    class Link:
        __slots__ = [
            'seq',
            'ins_prev',
            'ins_next',
            'lru_prev',
            'lru_next',
            'lfu_prev',
            'lfu_next',
            'key',
            'value',
            'weight',
            'written',
            'accessed',
            'hits',
            'unlinked',
        ]

        seq: int
        ins_prev: 'CacheImpl.Link'
        ins_next: 'CacheImpl.Link'
        lru_prev: 'CacheImpl.Link'
        lru_next: 'CacheImpl.Link'
        lfu_prev: 'CacheImpl.Link'
        lfu_next: 'CacheImpl.Link'
        key: ta.Any | weakref.ref
        value: ta.Any | weakref.ref
        weight: float
        written: float
        accessed: float
        hits: int
        unlinked: bool

        def __repr__(self) -> str:
            return (
                f'Link@{self.seq!s}('
                f'ins_prev={("@" + str(self.ins_prev.seq)) if self.ins_prev is not None else None}, '
                f'ins_next={("@" + str(self.ins_next.seq)) if self.ins_next is not None else None}, '
                f'lru_prev={("@" + str(self.lru_prev.seq)) if self.lru_prev is not None else None}, '
                f'lru_next={("@" + str(self.lru_next.seq)) if self.lru_next is not None else None}, '
                f'lfu_prev={("@" + str(self.lfu_prev.seq)) if self.lfu_prev is not None else None}, '
                f'lfu_next={("@" + str(self.lfu_next.seq)) if self.lfu_next is not None else None}, '
                f'key={self.key!r}, '
                f'value={self.value!r}, '
                f'weight={self.weight}, '
                f'written={self.written}, '
                f'accessed={self.accessed}, '
                f'hits={self.hits}, '
                f'unlinked={self.unlinked})'
            )

    _cache: ta.MutableMapping[ta.Any, Link]

    DEFAULT_MAX_SIZE = 256

    def __init__(
            self,
            *,
            max_size: int = DEFAULT_MAX_SIZE,
            max_weight: float | None = None,
            identity_keys: bool = False,
            expire_after_access: float | None = None,
            expire_after_write: float | None = None,
            removal_listener: ta.Callable[[K | weakref.ref, V | weakref.ref], None] | None = None,
            clock: ta.Callable[[], float] | None = None,
            weak_keys: bool = False,
            weak_values: bool = False,
            weigher: ta.Callable[[V], float] = lambda _: 1.,
            lock: lang.DefaultLockable = None,
            raise_overweight: bool = False,
            eviction: Eviction = LRU,
            track_frequency: bool | None = None,
    ) -> None:
        super().__init__()

        if clock is None:
            if expire_after_access is not None or expire_after_write is not None:
                clock = time.time
            else:
                clock = lambda: 0.  # noqa

        self._max_size = max_size
        self._max_weight = max_weight
        self._identity_keys = identity_keys
        self._expire_after_access = expire_after_access
        self._expire_after_write = expire_after_write
        self._removal_listener = removal_listener
        self._clock = clock
        self._weak_keys = weak_keys
        self._weak_values = weak_values
        self._weigher = weigher
        self._lock = lang.default_lock(lock, True)
        self._raise_overweight = raise_overweight
        self._eviction = eviction
        self._track_frequency = track_frequency if track_frequency is not None else (eviction is LFU)

        if weak_keys and not identity_keys:
            self._cache = weakref.WeakKeyDictionary()
        else:
            self._cache = {}

        self._root = CacheImpl.Link()
        self._root.seq = 0
        self._root.ins_next = self._root.ins_prev = self._root
        self._root.lru_next = self._root.lru_prev = self._root
        if self._track_frequency:
            self._root.lfu_next = self._root.lfu_prev = self._root

        weak_dead: collections.deque[CacheImpl.Link] | None
        if weak_keys or weak_values:
            weak_dead = collections.deque()
            weak_dead_ref = weakref.ref(weak_dead)
        else:
            weak_dead = None
            weak_dead_ref = None
        self._weak_dead = weak_dead
        self._weak_dead_ref = weak_dead_ref

        self._seq = 0
        self._size = 0
        self._weight = 0.
        self._hits = 0
        self._misses = 0
        self._max_size_ever = 0
        self._max_weight_ever = 0.

    def _unlink(self, link: Link) -> None:
        if link is self._root:
            raise TypeError
        if link.unlinked:
            return

        link.ins_prev.ins_next = link.ins_next
        link.ins_next.ins_prev = link.ins_prev
        link.ins_next = link.ins_prev = link

        link.lru_prev.lru_next = link.lru_next
        link.lru_next.lru_prev = link.lru_prev
        link.lru_next = link.lru_prev = link

        if self._track_frequency:
            link.lfu_prev.lfu_next = link.lfu_next
            link.lfu_next.lfu_prev = link.lfu_prev
            link.lfu_next = link.lfu_prev = link

        if self._removal_listener is not None:
            try:
                self._removal_listener(link.key, link.value)
            except Exception:
                log.exception('Removal listener raised exception')

        self._size -= 1
        self._weight -= link.weight
        link.key = link.value = None
        link.unlinked = True

    def _kill(self, link: Link) -> None:
        if link is self._root:
            raise RuntimeError

        key = link.key
        if self._weak_keys:
            if key is not None:
                key = key()
            if key is None:
                key = SKIP

        if key is not SKIP:
            cache_key = id(key) if self._identity_keys else key
            cache_link = self._cache.get(cache_key)
            if cache_link is link:
                del self._cache[cache_key]

        self._unlink(link)

    def _reap(self) -> None:
        if self._weak_dead is not None:
            while True:
                try:
                    link = self._weak_dead.popleft()
                except IndexError:
                    break
                self._kill(link)

        clock = None

        if self._expire_after_write is not None:
            clock = self._clock()
            deadline = clock - self._expire_after_write

            while self._root.ins_next is not self._root:
                link = self._root.ins_next
                if link.written > deadline:
                    break
                self._kill(link)

        if self._expire_after_access is not None:
            if clock is None:
                clock = self._clock()
            deadline = clock - self._expire_after_access

            while self._root.lru_next is not self._root:
                link = self._root.lru_next
                if link.accessed > deadline:
                    break
                self._kill(link)

    def reap(self) -> None:
        with self._lock():
            self._reap()

    def _get_link(self, key: K) -> tuple[Link, V]:
        cache_key = id(key) if self._identity_keys else key

        link = self._cache[cache_key]
        if link.unlinked:
            raise Exception

        def fail():
            with contextlib.suppress(KeyError):
                del self._cache[cache_key]
            self._unlink(link)
            raise KeyError(key)

        if self._identity_keys:
            link_key = link.key
            if self._weak_keys:
                link_key = link_key()
                if link_key is None:
                    fail()
            if key is not link_key:
                fail()

        value = link.value
        if self._weak_values:
            if value is not None:
                value = value()
            if value is None:
                fail()

        return link, value  # type: ignore

    def __getitem__(self, key: K) -> V:
        with self._lock():
            self._reap()

            try:
                link, value = self._get_link(key)
            except KeyError:
                self._misses += 1
                raise KeyError(key) from None

            if link.lru_next is not self._root:
                link.lru_prev.lru_next = link.lru_next
                link.lru_next.lru_prev = link.lru_prev

                lru_last = self._root.lru_prev
                lru_last.lru_next = self._root.lru_prev = link
                link.lru_prev = lru_last
                link.lru_next = self._root

            if self._track_frequency:
                lfu_pos = link.lfu_prev
                while lfu_pos is not self._root and lfu_pos.hits <= link.hits:
                    lfu_pos = lfu_pos.lfu_prev

                if link.lfu_prev is not lfu_pos:
                    link.lfu_prev.lfu_next = link.lfu_next
                    link.lfu_next.lfu_prev = link.lfu_prev

                    lfu_last = lfu_pos.lfu_prev
                    lfu_last.lfu_next = lfu_pos.lfu_prev = link
                    link.lfu_prev = lfu_last
                    link.lfu_next = lfu_pos

            link.accessed = self._clock()
            link.hits += 1
            self._hits += 1
            return value

    @staticmethod
    def _weak_die(dead_ref: weakref.ref, link: Link, key_ref: weakref.ref) -> None:  # noqa
        dead = dead_ref()
        if dead is not None:
            dead.append(link)

    @property
    def _full(self) -> bool:
        if self._max_size is not None and self._size >= self._max_size:
            return True
        if self._max_weight is not None and self._weight >= self._max_weight:
            return True
        return False

    def clear(self) -> None:
        with self._lock():
            self._cache.clear()
            while True:
                link = self._root.ins_prev
                if link is self._root:
                    break
                if link.unlinked:
                    raise TypeError
                self._unlink(link)

    def __setitem__(self, key: K, value: V) -> None:
        weight = self._weigher(value)

        with self._lock():
            self._reap()

            if self._max_weight is not None and weight > self._max_weight:
                if self._raise_overweight:
                    raise OverweightError
                else:
                    return

            try:
                existing_link, existing_value = self._get_link(key)
            except KeyError:
                pass
            else:
                self._unlink(existing_link)

            while self._full:
                self._eviction(self)

            link = CacheImpl.Link()

            self._seq += 1
            link.seq = self._seq

            def make_ref(o, b):
                if not b:
                    return o
                return weakref.ref(o, functools.partial(CacheImpl._weak_die, self._weak_dead_ref, link))  # type: ignore  # noqa

            link.key = make_ref(key, self._weak_keys)
            link.value = make_ref(value, self._weak_values)

            link.weight = weight
            link.written = link.accessed = self._clock()
            link.hits = 0
            link.unlinked = False

            ins_last = self._root.ins_prev
            ins_last.ins_next = self._root.ins_prev = link
            link.ins_prev = ins_last
            link.ins_next = self._root

            lru_last = self._root.lru_prev
            lru_last.lru_next = self._root.lru_prev = link
            link.lru_prev = lru_last
            link.lru_next = self._root

            if self._track_frequency:
                lfu_last = self._root.lfu_prev
                lfu_last.lfu_next = self._root.lfu_prev = link
                link.lfu_prev = lfu_last
                link.lfu_next = self._root

            self._weight += weight
            self._size += 1
            self._max_size_ever = max(self._size, self._max_size_ever)
            self._max_weight_ever = max(self._weight, self._max_weight_ever)

            cache_key = id(key) if self._identity_keys else key
            self._cache[cache_key] = link

    def __delitem__(self, key: K) -> None:
        with self._lock():
            self._reap()

            link, value = self._get_link(key)

            cache_key = id(key) if self._identity_keys else key
            del self._cache[cache_key]

            self._unlink(link)

    def __len__(self) -> int:
        with self._lock():
            self._reap()

            return self._size

    def __contains__(self, key: K) -> bool:  # type: ignore
        with self._lock():
            self._reap()

            try:
                self._get_link(key)
            except KeyError:
                return False
            else:
                return True

    def __iter__(self) -> ta.Iterator[K]:
        with self._lock():
            self._reap()

            link = self._root.ins_prev
            while link is not self._root:
                key = link.key
                if self._weak_keys:
                    if key is not None:
                        key = key()
                    if key is not None:
                        yield key
                else:
                    yield key  # type: ignore

                nxt = link.ins_prev
                if nxt is link:
                    raise ValueError
                link = nxt

    @property
    def stats(self) -> Cache.Stats:
        with self._lock():
            return Cache.Stats(
                self._seq,
                self._size,
                self._weight,
                self._hits,
                self._misses,
                self._max_size_ever,
                self._max_weight_ever,
            )


new_cache = CacheImpl
