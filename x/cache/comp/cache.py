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

from omlish import dataclasses as dc
from omlish import lang

from .types import CacheKey
from .types import CacheableName
from .types import CacheableResolver
from .types import CacheableVersionMap


class Cache:
    def __init__(
            self,
            resolver: CacheableResolver,
    ) -> None:
        super().__init__()

        self._resolver = resolver

        self._dct: dict[CacheKey, 'Cache._Entry'] = {}

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
    class _Entry:
        key: CacheKey
        versions: CacheableVersionMap
        value: ta.Any

    def _build_version_map(self, names: ta.Iterable[CacheableName]) -> CacheableVersionMap:
        dct = {}
        for n in names:
            c = self._resolver.resolve(n)
            dct[n] = c.version
        return dct

    def get(self, key: CacheKey) -> lang.Maybe[ta.Any]:
        try:
            entry = self._dct[key]
        except KeyError:
            self._stats.num_misses += 1
            return lang.empty()

        new_versions = self._build_version_map(entry.versions)
        if entry.versions != new_versions:
            del self._dct[key]
            self._stats.num_invalidates = 0
            return lang.empty()

        self._stats.num_hits += 1
        return lang.just(entry.value)

    def put(self, key: CacheKey, versions: CacheableVersionMap, val: ta.Any) -> None:
        if key in self._dct:
            raise KeyError(key)

        self._dct[key] = Cache._Entry(
            key,
            versions,
            val,
        )
        self._stats.num_puts += 1
