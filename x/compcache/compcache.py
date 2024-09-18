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
import abc
import contextlib
import functools
import importlib
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')
CacheT = ta.TypeVar('CacheT', bound='Cache')


##


CacheableVersion: ta.TypeAlias = ta.Hashable
CacheableVersionMap: ta.TypeAlias = ta.Mapping['CacheableName', CacheableVersion]

CacheableNameT = ta.TypeVar('CacheableNameT', bound='CacheableName')


class CacheableName(lang.Abstract):
    pass


class Cacheable(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> CacheableName:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> CacheableVersion:
        raise NotImplementedError


class CacheableResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, name: CacheableName) -> Cacheable:
        raise NotImplementedError


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class CacheKey(lang.Abstract, ta.Generic[CacheableNameT]):
    name: CacheableNameT

    @dc.validate
    def _check_types(self) -> bool:
        hash(self)
        return isinstance(self.name, CacheableName)


##


class Cache:
    def __init__(
            self,
            resolver: CacheableResolver,
    ) -> None:
        super().__init__()

        self._resolver = resolver

        self._dct: dict[CacheKey, 'Cache._Entry'] = {}

    @dc.dataclass(frozen=True)
    class _Entry:
        key: CacheKey
        versions: CacheableVersionMap
        value: ta.Any

    def get(self, key: CacheKey) -> lang.Maybe[ta.Any]:
        try:
            entry = self._dct[key]
        except KeyError:
            return lang.empty()
        else:
            return lang.just(entry.value)

    def put(self, key: CacheKey, versions: CacheableVersionMap, val: ta.Any) -> None:
        self._dct[key] = Cache._Entry(
            key,
            versions,
            val,
        )


##


@dc.dataclass(frozen=True)
class FnCacheableName(CacheableName, lang.Final):
    module: str
    qualname: str


@dc.dataclass(frozen=True)
class FnCacheable(Cacheable, lang.Final):
    fn: ta.Callable
    version: int = dc.xfield(override=True)

    @cached.property
    def name(self) -> FnCacheableName:
        return FnCacheableName(self.__module__, self.fn.__qualname__)


class FnCacheableResolver(CacheableResolver):
    def __init__(self) -> None:
        super().__init__()

        self._cache: dict[FnCacheableName, FnCacheable] = {}

    def resolve(self, name: CacheableName) -> Cacheable:
        fname = check.isinstance(name, FnCacheableName)
        try:
            return self._cache[fname]
        except KeyError:
            pass
        mod = importlib.import_module(fname.module)
        obj = mod
        for a in fname.qualname.split('.'):
            obj = getattr(obj, a)
        check.callable(obj)
        fc = check.isinstance(obj.__cacheable__, FnCacheable)
        self._cache[fname] = fc
        return fc


@dc.dataclass(frozen=True)
class FnCacheKey(CacheKey[FnCacheableName], lang.Final):
    args: tuple
    kwargs: col.frozendict[str, ta.Any]

    @dc.validate
    def _check_fn_types(self) -> bool:
        return (
                isinstance(self.name, FnCacheableName) and
                isinstance(self.args, tuple) and
                isinstance(self.kwargs, col.frozendict)
        )


##


_CURRENT_CACHE: Cache | None = None


@contextlib.contextmanager
def cache_context(cache: CacheT) -> ta.Iterator[CacheT]:
    global _CURRENT_CACHE
    prev = _CURRENT_CACHE
    try:
        _CURRENT_CACHE = cache
        yield
    finally:
        check.is_(_CURRENT_CACHE, cache)
        _CURRENT_CACHE = prev


@dc.dataclass(frozen=True)
class _CacheResult(ta.Generic[T], lang.Final):
    hit: bool
    value: T


@dc.dataclass()
class _CacheableContext(lang.Final):
    cacheable: Cacheable = dc.xfield(frozen=True)
    key: CacheKey = dc.xfield(frozen=True)

    result: _CacheResult | None = None

    parent: ta.Optional['_CacheableContext'] | None = dc.xfield(default=None, kw_only=True, frozen=True)
    children: list['_CacheableContext'] = dc.xfield(default_factory=list, frozen=True)

    def walk(self) -> ta.Iterator['_CacheableContext']:
        yield self
        for child in self.children:
            yield from child.walk()

    def build_version_map(self) -> CacheableVersionMap:
        versions: dict[CacheableName, CacheableVersion] = {}
        for ctx in self.walk():
            c = ctx.cacheable
            try:
                ex = versions[c.name]
            except KeyError:
                versions[c.name] = c.version
            else:
                if ex != c.version:
                    raise Exception(f'Version mismatch: {ex} {c}')
        return versions


_CURRENT_CACHEABLE_CONTEXT: _CacheableContext | None = None


@contextlib.contextmanager
def _cacheable_context(ctx: _CacheableContext) -> ta.Iterator[_CacheableContext]:
    check.none(ctx.parent)
    global _CURRENT_CACHEABLE_CONTEXT
    prev =_CURRENT_CACHEABLE_CONTEXT
    ctx = dc.replace(ctx, parent=prev)
    try:
        _CURRENT_CACHEABLE_CONTEXT = ctx
        if prev is not None:
            prev.children.append(ctx)
        yield ctx
    finally:
        check.is_(_CURRENT_CACHEABLE_CONTEXT, ctx)
        _CURRENT_CACHEABLE_CONTEXT = prev


def cached_fn(version: int) -> ta.Callable[[T], T]:
    def outer(fn):
        cacheable = FnCacheable(
            fn,
            version,
        )

        fn.__cacheable__ = cacheable

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            if (cache := _CURRENT_CACHE) is not None:
                key = FnCacheKey(
                    cacheable.name,
                    args,
                    col.frozendict(kwargs),
                )

                with _cacheable_context(_CacheableContext(
                        cacheable,
                        key,
                )) as ctx:  # noqa
                    if (hit := cache.get(key)).present:
                        val = hit.must()
                        ctx.result = _CacheResult(True, val)
                        return val

                    val = fn(*args, **kwargs)
                    ctx.result = _CacheResult(False, val)
                    cache.put(
                        key,
                        ctx.build_version_map(),
                        val,
                    )
                    return val

            else:
                return fn(*args, **kwargs)

        return inner

    return outer  # noqa


##


@cached_fn(0)
def f(x: int, y: int) -> int:
    print(f'f({x}, {y})')
    return x + y


@cached_fn(0)
def g(x: int, y: int) -> int:
    print(f'g({x}, {y})')
    return f(x, 1) + f(y, 1)


@cached_fn(0)
def h(x: int, y: int) -> int:
    print(f'g({x}, {y})')
    return g(x, 2) + g(y, 2)


def _main() -> None:
    fr = FnCacheableResolver()

    h_fc = h.__cacheable__
    h_fcn = h_fc.name
    check.is_(fr.resolve(h_fcn), h_fc)

    #

    # check.equal(h(1, 2), 11)

    #

    cache = Cache(resolver=fr)

    #

    with cache_context(cache):
        for _ in range(2):
            check.equal(h(1, 2), 11)
            check.equal(h(3, 2), 13)


if __name__ == '__main__':
    _main()
