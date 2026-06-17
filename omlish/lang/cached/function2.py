"""
The hot __call__ path of every cached function is code-generated per _CacheSpec (its 'species'): the axes that shape the
emitted code (key shape, bind kind, locking, exception caching) are a small NamedTuple, and a generated, per-species
class is cached and reused much like the stdlib dataclasses/namedtuple machinery. Only the key maker stays separate
(itself codegen'd per signature). See _gen_hot_call_src for the generator.

Done:
 - lighter weight bound methods - __get__ produces a minimal _BoundCachedFunction, no per-bind update_wrapper
 - specialize nullary (single-slot storage, no key maker)
 - reconcile A().f() with A.f(A()) - the latter routes to the instance cache (self clipped, never keyed)
 - free-function / staticmethod pickling

TODO:
 - !! use c-backed functools.cache if possible / riic - the cext mirrors the species with switch statements
 - significant_kwargs_order=False - stdlib has significant kwarg order
 - integrate / expose with collections.cache
 - weakrefs (selectable by arg)
 - use __transient_dict__ to support common state nuking
 - use __set_name__ ?
 - on_compute
 - max_recursion?
 - true __slots__ for bound wrappers (needs a heavy/light base split so update_wrapper-bearing species keep __dict__)
"""
import dataclasses as dc
import enum
import functools
import inspect
import types
import typing as ta

from ..classes.abstract import Abstract
from ..contextmanagers import DefaultLockable
from ..contextmanagers import default_lock
from ..descriptors import unwrap_func
from ..descriptors import unwrap_func_with_partials
from ..params import KwargsParam
from ..params import Param
from ..params import ParamSeparator
from ..params import ParamSpec
from ..params import ValParam
from ..params import param_render


P = ta.ParamSpec('P')
T = ta.TypeVar('T')

CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

CacheKeyMaker: ta.TypeAlias = ta.Callable[..., tuple]


##


def _nullary_cache_key_maker():
    return ()


def _self_cache_key_maker(self):
    return (self,)


_PRE_MADE_CACHE_KEY_MAKERS = [
    _nullary_cache_key_maker,
    _self_cache_key_maker,
]


_PRE_MADE_CACHE_KEY_MAKERS_BY_PARAM_SPEC: ta.Mapping[ParamSpec, CacheKeyMaker] = {
    ParamSpec.inspect(fn): fn  # type: ignore
    for fn in _PRE_MADE_CACHE_KEY_MAKERS
}


##


def _make_unwrapped_cache_key_maker(
        fn: ta.Callable,
        *,
        bound: bool = False,
) -> CacheKeyMaker:
    if inspect.isgeneratorfunction(fn) or inspect.iscoroutinefunction(fn):
        raise TypeError(fn)

    ps = ParamSpec.inspect(
        fn,
        offset=1 if bound else 0,
        strip_annotations=True,
    )

    if not len(ps):
        return _nullary_cache_key_maker

    if not ps.has_defaults:
        try:
            return _PRE_MADE_CACHE_KEY_MAKERS_BY_PARAM_SPEC[ps]
        except KeyError:
            pass

    builtin_pfx = '__cache_key_maker__'
    ns = {
        (builtin_tuple := builtin_pfx + 'tuple'): tuple,
        (builtin_sorted := builtin_pfx + 'sorted'): sorted,
    }

    src_params = []
    src_vals = []
    kwargs_name = None
    for p in ps.with_seps:
        if isinstance(p, ParamSeparator):
            # Reproduce '/' and '*' so the generated key maker enforces positional-only / keyword-only calling
            # conventions exactly, raising early on invalid calls rather than passing them through to the value fn (or,
            # worse, silently hitting a warm cache entry).
            src_params.append(p.value)
            continue

        if not isinstance(p, Param):
            raise TypeError(p)

        if isinstance(p, ValParam) and p.default.present:
            ns[p.name] = p.default

        src_params.append(param_render(
            p,
            render_default=lambda _: p.name,  # noqa
        ))

        if isinstance(p, KwargsParam):
            kwargs_name = p.name
        else:
            src_vals.append(p.name)

    if kwargs_name is not None:
        src_vals.append(f'{builtin_tuple}({builtin_sorted}({kwargs_name}.items()))')

    rendered = (
        f'def __func__({", ".join(src_params)}):\n'
        f'    return ({", ".join(src_vals)}{"," if len(src_vals) == 1 else ""})\n'
    )
    exec(rendered, ns)

    kfn: CacheKeyMaker = ns['__func__']  # type: ignore[assignment]
    return kfn


def _make_cache_key_maker(
        fn: ta.Any,
        *,
        bound: bool = False,
):
    fn, partials = unwrap_func_with_partials(fn)

    kfn = _make_unwrapped_cache_key_maker(fn, bound=bound)

    for part in partials[::-1]:
        kfn = functools.partial(kfn, *part.args, **part.keywords)

    return kfn


##


class _CachedException(ta.NamedTuple):
    ex: BaseException


_MISSING = object()

_EMPTY_DICT: ta.Mapping = {}  # read-only fallback for instances without a __dict__


def _raise_cached(ce: _CachedException) -> ta.NoReturn:
    raise ce.ex


#


class _KeyShape(enum.Enum):
    NULLARY = enum.auto()  # zero effective params -> constant key, single-slot storage, no key maker
    GENERAL = enum.auto()  # arbitrary signature -> backed by the codegen'd key maker + mapping


class _BindKind(enum.Enum):
    FREE = enum.auto()        # top-level callable: runtime-bound method, staticmethod (full base, carries metadata)
    BOUND = enum.auto()       # per-instance / per-owner wrapper produced by a descriptor's __get__ (lightweight base)
    DESCRIPTOR = enum.auto()  # the descriptor for an instance/class method: directly callable AND a __get__ provider


class _CacheSpec(ta.NamedTuple):
    """The axes of a cache configuration that shape the generated code (instance data lives off the instance)."""

    key_shape: _KeyShape
    bind_kind: _BindKind
    locked: bool
    cache_exceptions: bool


#


class _CachedFunction(Abstract, ta.Generic[T]):
    @dc.dataclass(frozen=True, kw_only=True)
    class Opts:
        map_maker: ta.Callable[[], ta.MutableMapping] = dict
        lock: DefaultLockable = None
        transient: bool = False
        no_wrapper_update: bool = False
        cache_exceptions: type[BaseException] | tuple[type[BaseException], ...] | None = None

        def __post_init__(self) -> None:
            if (ce := self.cache_exceptions) is not None:
                if isinstance(ce, type):
                    if not issubclass(ce, BaseException):
                        raise TypeError(ce)
                elif isinstance(ce, tuple):
                    for e in ce:
                        if not issubclass(e, BaseException):
                            raise TypeError(e)
                else:
                    raise TypeError(ce)

    def __init__(
            self,
            fn: ta.Callable[P, T],
            *,
            opts: Opts = Opts(),
            key_maker: ta.Callable[..., tuple] | None = None,
            values: ta.MutableMapping | None = None,
            value_fn: ta.Callable[P, T] | None = None,
    ) -> None:
        super().__init__()

        self._fn = (fn,)
        self._opts = opts
        self._key_maker = key_maker if key_maker is not None else _make_cache_key_maker(fn)

        self._lock = default_lock(opts.lock, False)() if opts.lock is not None else None
        self._values = values if values is not None else opts.map_maker()
        self._value_fn = value_fn if value_fn is not None else fn
        self._v = _MISSING  # single-slot storage for nullary species
        self._cache_exceptions = opts.cache_exceptions  # referenced directly by generated __call__s
        if not self._opts.no_wrapper_update:
            functools.update_wrapper(self, fn)

    @property
    def _fn(self):
        return self.__fn

    @_fn.setter
    def _fn(self, x):
        self.__fn = x

    def reset(self) -> None:
        self._values = self._opts.map_maker()
        self._v = _MISSING

    def __bool__(self) -> bool:
        raise TypeError

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        # The real, hot implementation is generated per-species by the code generator (see _gen_hot_call_src) and
        # installed on each concrete species class; this only declares the callable contract.
        raise NotImplementedError


#


class _FreeCachedFunction(_CachedFunction[T]):
    """
    Hand-written base for free (non-descriptor) species: runtime-bound methods and staticmethods. The hot __call__ is
    generated per-spec by _get_species; everything else (init, reduce) is shared here.
    """

    def __reduce__(self):
        fn, = self._fn
        return (
            _unpickle_free,
            (
                fn,
                self._opts,
                self._values if not self._opts.transient else None,
            ),
        )


#


class _BoundCachedFunction(_CachedFunction[T]):
    """
    Hand-written base for the lightweight per-instance / per-owner wrapper a descriptor produces on __get__. It holds
    only the bound value fn and its own cache, delegating all metadata (__wrapped__, __name__, _opts, ...) to the
    descriptor - so binding a fresh instance does not rebuild a whole wrapper (no update_wrapper per __get__).
    """

    def __init__(  # noqa
            self,
            desc,
            instance,
            owner,
            value_fn,
            values=None,
    ):
        # NOTE: deliberately does NOT call super().__init__ - skipping the heavy per-bind init / update_wrapper is the
        # entire point of the lightweight bound wrapper.
        self._desc = desc
        self._instance = instance
        self._owner = owner
        self._value_fn = value_fn
        self._key_maker = desc._bound_key_maker  # noqa
        opts = desc._opts  # noqa
        self._values = values if values is not None else opts.map_maker()
        self._lock = default_lock(opts.lock, False)() if opts.lock is not None else None
        self._cache_exceptions = opts.cache_exceptions
        self._v = _MISSING

    def __getattr__(self, name):
        if name == '_desc':  # guard against recursion before __init__ has run
            raise AttributeError(name)
        return getattr(self._desc, name)

    def __get__(self, instance, owner=None):
        # Only reached for classmethod-scoped bounds installed on a class (instance bounds live in instance.__dict__ and
        # shadow this). Re-bind when accessed through a different owner so subclasses get their own per-owner cache.
        desc = self._desc
        if desc._scope is classmethod:  # noqa
            return self if owner is self._owner else desc._bind(None, owner)  # noqa
        if instance is None or instance is self._instance:
            return self
        return desc._bind(instance, owner)  # noqa

    def __reduce__(self):
        desc = self._desc
        if desc._scope is not None:  # noqa
            raise NotImplementedError
        if self._instance is None:
            raise RuntimeError
        if desc._opts.transient:  # noqa
            state = None
        elif self._v is not _MISSING:  # nullary species: the value lives in the single slot
            state = (True, self._v)
        else:  # general species: the value(s) live in the mapping
            state = (False, self._values)
        return (_unpickle_bound, (self._instance, desc._name, state))  # noqa


#


class _UnboundCachedMethod:
    """
    Returned by a (non-classmethod) descriptor's __get__ for class-level access (e.g. ``A.f``). Calling it as
    ``A.f(inst, ...)`` routes to inst's own per-instance cache - inst is clipped off and never keyed, and storage lives
    on inst, exactly as ``inst.f(...)`` would (no shared/global store, no hard ref to inst).
    """

    __slots__ = ('_desc', '_owner')

    def __init__(self, desc: _DescriptorCachedFunction, owner: ta.Any) -> None:
        self._desc = desc
        self._owner = owner

    def __getattr__(self, name):
        if name == '_desc':  # guard against recursion before __init__ has run
            raise AttributeError(name)
        return getattr(self._desc, name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._desc!r})'

    def __call__(self, instance, /, *args, **kwargs):
        desc = self._desc
        bound = getattr(instance, '__dict__', _EMPTY_DICT).get(desc._name)  # noqa
        if not (isinstance(bound, _BoundCachedFunction) and bound._desc is desc):  # noqa
            bound = desc._bind(instance, type(instance))  # noqa
        return bound(*args, **kwargs)


#


class _DescriptorCachedFunction(_CachedFunction[T]):
    """
    The descriptor for instance methods (scope=None) and classmethods (scope=classmethod). It is itself a species - its
    direct __call__ (used when called as a plain function, e.g. a module-level cache) is generated like any other - and
    additionally implements __get__, producing the lightweight per-instance/owner _BoundCachedFunction on access.
    """

    def __init__(
            self,
            fn: ta.Callable[P, T],
            scope: ta.Any,  # classmethod | None
            *,
            name: str | None = None,
            **kwargs,
    ) -> None:
        super().__init__(fn, **kwargs)

        self._scope = scope
        self._name = name if name is not None else unwrap_func(fn).__name__
        self._bound_key_maker: ta.Callable[..., tuple] | None = None
        self._bound_species: type | None = None

    def __reduce__(self):
        # The unbound descriptor is a class attribute - it should be pickled by reference, not by value.
        raise TypeError(self)

    def _ensure_bound_species(self) -> type:
        if (bs := self._bound_species) is not None:
            return bs

        fn, = self._fn
        self._bound_key_maker = km = _make_cache_key_maker(fn, bound=True)
        opts = self._opts
        self._bound_species = bs = _get_species(_CacheSpec(
            key_shape=(
                _KeyShape.NULLARY
                if (opts.map_maker is dict and km is _nullary_cache_key_maker)
                else _KeyShape.GENERAL
            ),
            bind_kind=_BindKind.BOUND,
            locked=opts.lock is not None,
            cache_exceptions=opts.cache_exceptions is not None,
        ))
        return bs

    def _bind(
            self,
            instance,
            owner=None,
            *,
            values: ta.MutableMapping | None = None,
    ):
        fn, = self._fn
        species = self._ensure_bound_species()
        bound = species(self, instance, owner, fn.__get__(instance, owner), values)

        if self._scope is classmethod and owner is not None:
            setattr(owner, self._name, bound)
        elif instance is not None:
            instance.__dict__[self._name] = bound

        return bound

    def __get__(self, instance, owner=None):
        if self._scope is classmethod:
            return self._bind(None, owner)
        if instance is None:
            # Class-level access (A.f): hand back an unbound method that routes A.f(inst) to inst's cache.
            return self if owner is None else _UnboundCachedMethod(self, owner)
        return self._bind(instance, owner)


##
# Species code generation. The hot __call__ path is fully codegen'd per _CacheSpec (everything but the key maker); the
# rest of each species is inherited from a hand-written base selected by bind_kind.


def _species_tag(spec: _CacheSpec) -> str:
    return '_'.join([
        spec.key_shape.name.lower(),
        spec.bind_kind.name.lower(),
        *(['locked'] if spec.locked else []),
        *(['exc'] if spec.cache_exceptions else []),
    ])


_GEN_INDENT = '    '


def _gen_hot_call_src(spec: _CacheSpec) -> tuple[str, str]:
    """
    Composes the hot __call__ body from per-axis fragments rather than enumerating every axis intersection: a single
    cache_exceptions-aware return/probe helper, a single store helper, and a single `locked` transform that wraps and
    indents the miss path under a `with` block. Adding an axis means adding one fragment/transform, not doubling blocks.
    """

    name = f'_cached_call__{_species_tag(spec)}'
    nullary = spec.key_shape is _KeyShape.NULLARY
    exc = spec.cache_exceptions

    sig = '(self)' if nullary else '(self, *args, **kwargs)'
    compute = 'self._value_fn()' if nullary else 'self._value_fn(*args, **kwargs)'
    target = 'self._v' if nullary else 'self._values[k]'

    # The single place cache_exceptions changes how a cached value is yielded. `bound` distinguishes an already-bound
    # name (the slot / freshly stored v) from an expression that must be evaluated exactly once (the dict subscript).
    def ret(value_src: str, *, bound: bool) -> str:
        if not exc:
            return f'return {value_src}'
        elif bound:
            return f'return {value_src} if type({value_src}) is not _CachedException else _raise_cached({value_src})'
        else:
            return f'return v if type(v := {value_src}) is not _CachedException else _raise_cached(v)'

    # Probe the cache; on a hit, return (unwrapping a cached exception); on a miss, fall through.
    def probe(*, first: bool) -> list[str]:
        if nullary:
            return [f'if (v := self._v) is not _MISSING: {ret("v", bound=True)}']
        sub = 'self._values[(k := self._key_maker(*args, **kwargs))]' if first else 'self._values[k]'
        return [
            f'try: {ret(sub, bound=False)}',
            'except KeyError: pass',
        ]

    # The single place cache_exceptions changes storage: wrap the compute so a matching exception is cached.
    def store() -> list[str]:
        if not exc:
            return [f'{target} = v = {compute}']
        return [
            f'try: {target} = v = {compute}',
            f'except self._cache_exceptions as e: {target} = v = _CachedException(e)',
        ]

    lines = probe(first=True)

    miss = [
        *(probe(first=False) if spec.locked else []),  # double-check re-probe only matters under a lock
        *store(),
    ]
    if spec.locked:  # the single `locked` transform: indent the miss path and slap a `with` above it
        lines += ['with self._lock:', *(_GEN_INDENT + ln for ln in miss)]
    else:
        lines += miss

    lines.append(ret('v', bound=True))

    src = '\n'.join([
        f'def {name}{sig}:',
        *[_GEN_INDENT + ln for ln in lines],
        '',
    ])
    return name, src


_SPECIES_BASES_BY_BIND_KIND: ta.Mapping[_BindKind, type] = {
    _BindKind.FREE: _FreeCachedFunction,
    _BindKind.BOUND: _BoundCachedFunction,
    _BindKind.DESCRIPTOR: _DescriptorCachedFunction,
}


_SPECIES_CACHE: dict[_CacheSpec, type] = {}


def _get_species(spec: _CacheSpec) -> type:
    try:
        return _SPECIES_CACHE[spec]
    except KeyError:
        pass

    name, src = _gen_hot_call_src(spec)
    ns: dict = {
        '_MISSING': _MISSING,
        '_CachedException': _CachedException,
        '_raise_cached': _raise_cached,
    }
    exec(src, ns)  # noqa

    cls = type(
        f'_CachedFunction[{_species_tag(spec)}]',
        (_SPECIES_BASES_BY_BIND_KIND[spec.bind_kind],),
        {'__call__': ns[name]},
    )
    _SPECIES_CACHE[spec] = cls
    return cls


def _make_free(fn: ta.Any, opts: _CachedFunction.Opts, *, values: ta.MutableMapping | None = None):
    if isinstance(fn, types.MethodType):
        value_fn, bound = fn, True
    elif isinstance(fn, staticmethod):
        value_fn, bound = unwrap_func(fn), False
    else:
        value_fn, bound = fn, False

    key_maker = _make_cache_key_maker(fn, bound=bound)

    spec = _CacheSpec(
        key_shape=(
            _KeyShape.NULLARY
            if (opts.map_maker is dict and key_maker is _nullary_cache_key_maker)
            else _KeyShape.GENERAL
        ),
        bind_kind=_BindKind.FREE,
        locked=opts.lock is not None,
        cache_exceptions=opts.cache_exceptions is not None,
    )

    return _get_species(spec)(fn, opts=opts, key_maker=key_maker, values=values, value_fn=value_fn)


def _make_descriptor(fn: ta.Any, scope: ta.Any, opts: _CachedFunction.Opts):
    # The descriptor's own (direct) key maker is unbound - it keys every argument, for when the descriptor is called as
    # a plain function (e.g. a module-level cache). This also performs the generator/coroutine rejection check.
    key_maker = _make_cache_key_maker(fn)

    spec = _CacheSpec(
        key_shape=(
            _KeyShape.NULLARY
            if (opts.map_maker is dict and key_maker is _nullary_cache_key_maker)
            else _KeyShape.GENERAL
        ),
        bind_kind=_BindKind.DESCRIPTOR,
        locked=opts.lock is not None,
        cache_exceptions=opts.cache_exceptions is not None,
    )

    return _get_species(spec)(fn, scope, opts=opts, key_maker=key_maker)


def _unpickle_free(fn, opts, values):
    return _make_free(fn, opts, values=values)


def _unpickle_bound(instance, name, state):
    obj = type(instance)

    desc: _DescriptorCachedFunction
    for bc in obj.__mro__[:-1]:
        try:
            desc = bc.__dict__[name]
        except KeyError:
            continue
        break
    else:
        raise AttributeError(name)

    if not isinstance(desc, _DescriptorCachedFunction):
        raise TypeError(desc)

    if state is None:
        return desc._bind(instance, obj)  # noqa

    slot, data = state
    if slot:
        bound = desc._bind(instance, obj)  # noqa
        bound._v = data  # noqa
        return bound
    return desc._bind(instance, obj, values=data)  # noqa


#


@ta.overload
def cached_function(fn: None = None, **kwargs: ta.Any) -> ta.Callable[[CallableT], CallableT]: ...


@ta.overload
def cached_function(fn: CallableT, **kwargs: ta.Any) -> CallableT: ...


def cached_function(fn=None, **kwargs):  # noqa
    if fn is None:
        return functools.partial(cached_function, **kwargs)

    opts = _CachedFunction.Opts(**kwargs)

    if isinstance(fn, (types.MethodType, staticmethod)):
        return _make_free(fn, opts)

    scope = classmethod if isinstance(fn, classmethod) else None

    return _make_descriptor(fn, scope, opts)


def static_init(fn: CallableT) -> CallableT:
    fn = cached_function(fn)
    fn()
    return fn
