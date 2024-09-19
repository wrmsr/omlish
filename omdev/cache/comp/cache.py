"""
TODO:
 - decorator
 - thread local cache instance - but shared
 - arbitrary user-specified cache keys
 - filesystem OPTIONAL
 - locking
 - Keyer scheme
 - per-module-ish CACHE_VERSION convention
 - are pickles stable?
 - ComputeCache class
 - Cacheable - fn is one
 - ttl
 - nice to have: np mmap
 - compress?
 - decos, descriptors, etc
 - overlap w/ jobs/dags/batches/whatever
 - joblib
 - keep src anyway, but just for warn
  - strip comments?
 - ** INPUTS **
  - if underlying impl changes, bust
  - kinda reacty/reffy/signally
 - decorator unwrapping and shit
 - proactive deep invalidate
 - tracked and versioned 'ops' but not result cached
  - 'Versioned'

manifest stuff
 - serialization_version
 - lib_version
 - lib_revision

fn manifest stuff
 - source
 - qualname
 - location

See:
 - https://github.com/amakelov/mandala
 - https://jax.readthedocs.io/en/latest/autodidax.html
 - tinyjit
 - https://docs.python.org/3/library/pickle.html#pickle.Pickler.dispatch_table

names:
 - CacheKey = unambiguous, fully qualified, unhashed map key - usually Cacheable + args
 - Cacheable = usually a fn
 - CacheableName = qualname of a cacheable
  - dir structure: __package__/__qualname__/... ?
"""
import copy
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc

from .types import CacheKey
from .types import CacheResult
from .types import Name
from .types import ObjectResolver
from .types import VersionMap


class Cache:
    def __init__(
            self,
            resolver: ObjectResolver,
    ) -> None:
        super().__init__()

        self._resolver = resolver

        self._dct: dict[CacheKey, Cache.Entry] = {}

        self._stats = Cache.Stats()

    @dc.dataclass()
    class Stats:
        num_hits: int = 0
        num_misses: int = 0
        num_invalidates: int = 0
        num_puts: int = 0

    @property
    def stats(self) -> Stats:
        return copy.deepcopy(self._stats)

    @dc.dataclass(frozen=True)
    class Entry:
        key: CacheKey
        versions: VersionMap
        value: ta.Any

        @dc.validate
        def _check_types(self) -> bool:
            return (
                isinstance(self.key, CacheKey) and
                isinstance(self.versions, col.frozendict)
            )

    def _build_version_map(self, names: ta.Iterable[Name]) -> VersionMap:
        dct = {}
        for n in names:
            c = self._resolver.resolve(n)
            dct[n] = c.version
        return col.frozendict(dct)

    def get(self, key: CacheKey) -> CacheResult | None:
        try:
            entry = self._dct[key]
        except KeyError:
            self._stats.num_misses += 1
            return None

        new_versions = self._build_version_map(entry.versions)
        if entry.versions != new_versions:
            del self._dct[key]
            self._stats.num_invalidates += 1
            return None

        self._stats.num_hits += 1
        return CacheResult(
            True,
            entry.versions,
            entry.value,
        )

    def put(self, key: CacheKey, versions: VersionMap, val: ta.Any) -> None:
        if key in self._dct:
            raise KeyError(key)

        self._dct[key] = Cache.Entry(
            key,
            versions,
            val,
        )
        self._stats.num_puts += 1
