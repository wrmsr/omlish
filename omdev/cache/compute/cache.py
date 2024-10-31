"""
TODO:
 - filesystem OPTIONAL
 - also postgres + (s3?) blobstore
 - locking
 - alt codecs? json?

==

TODO (old):
 - are pickles stable?
 - ttl
 - np mmap
  - https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flags.html freeze ndarray w writable=False
 - compress?
 - overlap w/ jobs/dags/batches/whatever
 - joblib
 - ** INPUTS **
  - if underlying impl changes, bust
  - kinda reacty/reffy/signally
 - decorator unwrapping and shit
 - proactive deep invalidate
 ----
 - version can be anything - hashes, etc
 - version generators - one for ast
 - configurable serde - marshal vs pickle? marshal w/ override for ndarray to write to file?
 - ok:
  - @fn - version, passive=False, deps=[Objectable, …]
   - it no version use ast - specifically {'ast': <md5>}
   - but if present just use literal they gave, probably int
   - idiom: Version can be a frozendict, conventionally of str -> ta.Hashable
  - auto deps - fn can get containing Packages
  - Module, Resource, …
  - hrm.. LiteralVersion, MapVersion? + custom Marshal? need to deser as frozendict
 - storage
  - object table? w/ versions? strictly one row per object, evict objects with diff versions than those encountered
  - nah Cache iface, SimpleCache, SqlCache
  - dir structure: __package__/__qualname__/... ?
 - next: Versions get squashed into VersionHash, store whole version in db but only pass and cmp md5
  - thus VersionHashMap

manifest stuff
 - serialization_version
 - lib_version
 - lib_revision

See:
 - https://jax.readthedocs.io/en/latest/autodidax.html
 - https://github.com/tinygrad/tinygrad/blob/78699d9924feb96dc0bac88c3646b5d4f9ecad23/tinygrad/engine/jit.py
 - https://github.com/SeaOfNodes/Simple/tree/c7445ad142aeaece5b2b1059c193735ba7e509d9 (gvn)
 - https://github.com/joblib/joblib/tree/bca1f4216a38cff82a85371c45dde79bed977d0e/joblib
 - https://docs.python.org/3/library/pickle.html#pickle.Pickler.dispatch_table

Don't see:
 - https://github.com/amakelov/mandala
"""
import copy
import typing as ta

from omlish import collections as col

from .storage import Storage
from .types import CacheEntry
from .types import CacheKey
from .types import CacheResult
from .types import CacheStats
from .types import Name
from .types import ObjectResolver
from .types import VersionMap


class Cache:
    def __init__(
            self,
            resolver: ObjectResolver,
            storage: Storage,
    ) -> None:
        super().__init__()

        self._resolver = resolver
        self._storage = storage

        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        return copy.deepcopy(self._stats)

    def _build_version_map(self, names: ta.Iterable[Name]) -> VersionMap:
        dct = {}
        for n in names:
            c = self._resolver.resolve(n)
            dct[n] = c.version
        return col.frozendict(dct)

    def get(self, key: CacheKey) -> CacheResult | None:
        entry = self._storage.get(key)
        if entry is None:
            self._stats.num_misses += 1
            return None

        new_versions = self._build_version_map(entry.versions)
        if entry.versions != new_versions:
            self._storage.delete(key)
            self._stats.num_invalidates += 1
            return None

        self._stats.num_hits += 1
        return CacheResult(
            True,
            entry.versions,
            entry.value,
        )

    def put(self, key: CacheKey, versions: VersionMap, val: ta.Any) -> None:
        self._storage.put(CacheEntry(
            key,
            versions,
            val,
        ))
        self._stats.num_puts += 1
