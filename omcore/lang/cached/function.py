"""
A cached-function ('memoization') mechanism supporting free functions, bound methods, staticmethods, classmethods, and
instance methods, with full descriptor-protocol and python-calling-convention fidelity.

The implementation is 'species'-based: the axes of a cache configuration that shape its hot code paths (key tier and
signature shape, bind kind, scope, locking, exception caching, raw-fn calling) form a small NamedTuple (_CacheSpec),
and a concrete class per spec - its 'species' - is generated, cached, and reused, much like the stdlib
dataclasses/namedtuple machinery. The hot `__call__` (and, for instance-method descriptors, the hot binding `__get__`)
is fully code-generated per species (see _SpeciesCodeGen); cold paths (init, pickling, reset, classmethod/defensive
`__get__`s) live on hand-written base classes chosen by bind kind.

Keys come in three tiers:

- NULLARY: zero effective params (and a plain dict map) - single-slot storage, no key maker, no backing map.
- INLINE: the generated `__call__` carries the wrapped function's own (bound-clipped) signature directly, so the
  *interpreter* performs kwarg canonicalization and positional-only / keyword-only enforcement natively. Keys are built
  inline (a bare un-tupled key when there is exactly one contribution), omitted defaulted args are keyed by the
  pickle-stable _OMITTED_ARG sentinel (distinct from explicitly passing a value equal to the default, matching
  functools.lru_cache), and the miss path reconstructs the original call, omitting args whose value is that sentinel.
- GENERAL: the fallback for anything the inline tier can't express (functools.partial-wrapped functions, defaulted
  positional-only params, defaulted pos-or-kw params preceding *args, hostile param names) - a code-generated
  per-signature key maker canonicalizes (*args, **kwargs) into a key tuple exactly reproducing the calling convention.
  This facility remains the calling-convention authority for the future cext.

Binding is instance-dict based: a descriptor's `__get__` installs a lightweight per-instance bound wrapper in
`instance.__dict__[name]` (shadowing the non-data descriptor - later accesses never re-bind). Everything shared across
an instance method's bindings (wrapper metadata, opts, key maker, defaults) lives as *class attributes* of a
per-descriptor generated bound class, so the warm bind is a single generated `__get__` frame: `object.__new__` plus one
`__dict__` literal holding only the truly per-instance state, plus the install. Class-attribute values that are
descriptors themselves must be neutralized: function-valued attributes (`__wrapped__`, the key maker, the raw fn) are
`staticmethod`-wrapped, and the back-reference to the descriptor (itself a `__get__`-provider!) is tuple-wrapped behind
the `_desc` property. When the decorated function is exactly a plain `types.FunctionType`, binding skips creating a
MethodType entirely - `fn.__get__(inst)(x) ≡ fn(inst, x)` is a language guarantee, so the species passes
`self._instance` to the raw fn (a shared class attribute); anything with a custom `__get__` keeps the per-bind
`fn.__get__` path.

No shared/global store exists, no hard instance refs are held outside the instance itself, and `self` is never a key
component. Classmethod-scope wrappers install on the owner class analogously. `A.f(inst, ...)` routes through inst's
own per-instance cache exactly as `inst.f(...)` would. All generated source is registered with linecache under virtual
filenames, so debuggers can step it and tracebacks render it.

A future optional cext may replace the generated species with a single heap type switching on the same _CacheSpec axes
(python-level codegen becomes C-level iffing) - _get_species is the single seam where that swaps in. The cext can cover
the NULLARY and GENERAL tiers first (calling the python key maker for the latter); INLINE species may remain
python-only until vectorcall-based argument parsing is warranted.

TODO:
 - cext species (see above) - also gets the hot path out of debugger singlestepping
 - INLINE defaulted pos-or-kw params preceding *args (currently GENERAL): reconstruction is possible - a non-empty
   received varargs tuple implies every preceding defaulted pk param was necessarily filled positionally, so the miss
   path can branch: `if va:` re-pass them positionally ahead of *va, else the existing omission-filtered kwargs dict
 - significant_kwargs_order=False - stdlib has significant kwarg order
 - integrate / expose with collections.cache
 - weakrefs (selectable by arg)
 - classmethod-scope pickling
 - use __transient_dict__ to support common state nuking
 - on_compute
 - max_recursion?
"""
import dataclasses as dc
import enum
import functools
import inspect
import itertools
import threading
import types
import typing as ta

from ..classes.abstract import Abstract
from ..classes.restrict import Final
from ..contextmanagers import DefaultLockable
from ..descriptors import unwrap_func
from ..descriptors import unwrap_func_with_partials
from ..params import ArgsParam
from ..params import KwargsParam
from ..params import KwOnlyParam
from ..params import Param
from ..params import ParamSeparator
from ..params import ParamSpec
from ..params import PosOnlyParam
from ..params import ValParam
from ..params import param_render


P = ta.ParamSpec('P')
T = ta.TypeVar('T')

CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

CacheKeyMaker: ta.TypeAlias = ta.Callable[..., tuple]


##


_GEN_SRC_COUNT = itertools.count()

_POPULATE_LINECACHE = False


def _register_gen_src(name: str, src: str) -> str:
    """
    Registers generated source with linecache under a unique virtual filename (returned, for compile()) so debuggers can
    step it and tracebacks render it.
    """

    filename = f'<generated:{__name__}:{next(_GEN_SRC_COUNT)}:{name}>'

    if _POPULATE_LINECACHE:
        import linecache

        linecache.cache[filename] = (len(src), None, src.splitlines(keepends=True), filename)

    return filename


def _exec_src(src: str, filename: str, ns: ta.Any) -> None:
    exec(compile(src, filename, 'exec'), ns)  # noqa


##
# The GENERAL-tier key maker facility: canonicalizes a call's (*args, **kwargs) into a hashable tuple key honoring the
# wrapped function's exact calling convention. The INLINE tier subsumes this for most signatures; this remains the
# fallback (partials, defaulted positional-only params, hostile names) and the convention authority for the cext.


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
            # The default rendered into the generated signature is the Maybe wrapper itself, not its value - a unique,
            # stable sentinel. An omitted arg is thus keyed distinctly from an explicitly-passed value equal to the
            # default, matching functools.lru_cache.
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

    filename = _register_gen_src(f'key_maker__{getattr(fn, "__qualname__", "?")}', rendered)
    _exec_src(rendered, filename, ns)  # noqa

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


class _OmittedArgSentinel:
    """
    The INLINE tier's omitted-defaulted-arg key component: cache keys for calls omitting a defaulted arg contain this
    singleton where the arg would be (key tuple position disambiguates params, so one global sentinel suffices). It
    pickles by reference back to the singleton itself, so cache entries keyed by omitted args survive pickling with
    identity (and thus key equality) intact - as the GENERAL tier's value-equal Maybe-default sentinels already do -
    rather than orphaning into never-again-hit entries.
    """

    def __repr__(self) -> str:
        return '<omitted>'

    def __reduce__(self):
        return '_OMITTED_ARG'


_OMITTED_ARG = _OmittedArgSentinel()


#


class _KeyShape(enum.Enum):
    NULLARY = enum.auto()  # zero effective params + dict map -> single-slot storage, no key maker, no backing map
    INLINE = enum.auto()   # __call__ carries the fn's own signature - interpreter-native canonicalization
    GENERAL = enum.auto()  # (*args, **kwargs) __call__ backed by the codegen'd key maker


class _BindKind(enum.Enum):
    FREE = enum.auto()        # top-level callable: plain fn, runtime-bound method, staticmethod - no __get__
    BOUND = enum.auto()       # per-instance / per-owner wrapper produced by a descriptor's __get__
    DESCRIPTOR = enum.auto()  # the descriptor for an instance/class method: directly callable AND a __get__ provider


class _CacheSpec(ta.NamedTuple):
    """
    The axes of a cache configuration that shape its generated code. Fields not meaningful for a given bind kind are
    normalized to their defaults so the species cache shares maximally. A future cext species is one heap type switching
    on these axes.
    """

    bind_kind: _BindKind
    key_shape: _KeyShape
    shape: tuple | None = None      # INLINE only: hashable signature-shape encoding, else None
    cls_scope: bool = False         # classmethod scoping - selects the __get__ variant; always False for FREE
    locked: bool = False
    cache_exceptions: bool = False
    raw_fn: bool = False             # BOUND only: compute passes self._instance to a raw class-attr fn
    dict_map: bool = True            # DESCRIPTOR instance-scope only: bind literal uses {} vs the map maker
    bound_nullary: bool = False      # DESCRIPTOR instance-scope only: binds omit _values (slot storage)
    bound_raw_fn: bool = False       # DESCRIPTOR instance-scope only: binds omit _value_fn (raw-fn bound species)


#


class _ResolvedKeyShape(ta.NamedTuple):
    key_shape: _KeyShape
    shape: tuple | None
    key_maker: CacheKeyMaker | None


# Bare names the generated bodies reference - params shadowing them are ineligible for the INLINE tier (all other
# generated names are __-prefixed, and __-prefixed params are rejected wholesale).
_INLINE_FORBIDDEN_PARAM_NAMES: ta.AbstractSet[str] = frozenset(['KeyError'])


def _inline_shape(ps: ParamSpec) -> tuple | None:
    """
    Encodes a ParamSpec as a hashable signature shape for the INLINE tier, or returns None when the signature is
    ineligible (defaulted positional-only params, defaulted pos-or-kw params preceding *args, __-prefixed or reserved
    param names).
    """

    out: list = []
    dflt_pk = False
    for p in ps.with_seps:
        if isinstance(p, ParamSeparator):
            out.append(p.value)
            continue

        name = p.name
        if name.startswith('__') or name in _INLINE_FORBIDDEN_PARAM_NAMES:
            return None

        if isinstance(p, PosOnlyParam):
            if p.default.present:
                return None  # omitted-suffix reconstruction not implemented - fall back to the key maker
            out.append(('po', name, False))
        elif isinstance(p, KwOnlyParam):
            out.append(('ko', name, p.default.present))
        elif isinstance(p, ValParam):
            if p.default.present:
                dflt_pk = True
            out.append(('pk', name, p.default.present))
        elif isinstance(p, ArgsParam):
            if dflt_pk:
                # Miss-path reconstruction re-passes defaulted pk params by keyword, which collides with re-passed
                # varargs when they were filled positionally - fall back to the key maker (see module TODO).
                return None
            out.append(('va', name, False))
        elif isinstance(p, KwargsParam):
            out.append(('vk', name, False))
        else:
            raise TypeError(p)

    return tuple(out)


def _resolve_key_shape(
        fn: ta.Any,
        *,
        bound: bool = False,
        slot_ok: bool = True,
        make_key_maker: bool = True,
) -> _ResolvedKeyShape:
    ufn, partials = unwrap_func_with_partials(fn)

    if inspect.isgeneratorfunction(ufn) or inspect.iscoroutinefunction(ufn):
        raise TypeError(ufn)

    if not partials:
        ps = ParamSpec.inspect(
            ufn,
            offset=1 if bound else 0,
            strip_annotations=True,
        )

        if not len(ps) and slot_ok:
            return _ResolvedKeyShape(_KeyShape.NULLARY, None, None)

        if (shape := _inline_shape(ps)) is not None:
            return _ResolvedKeyShape(_KeyShape.INLINE, shape, None)

    return _ResolvedKeyShape(
        _KeyShape.GENERAL,
        None,
        _make_cache_key_maker(fn, bound=bound) if make_key_maker else None,
    )


#


def _lock_factory(lock: DefaultLockable) -> ta.Callable[[], ta.Any] | None:
    """
    Normalizes an Opts.lock value into a per-wrapper lock factory (or None when unlocked), computed once per
    descriptor/wrapper rather than per bind. `lock=True` deliberately yields a fresh lock per bound instance.

    TODO: promote to contextmanagers.py as default_lock_factory, or at least dedupe with it
    """

    if lock is None or lock is False:
        return None

    if lock is True:
        return threading.RLock

    if callable(lock):
        return lock

    if isinstance(lock, ta.ContextManager):
        return lambda: lock

    raise TypeError(lock)


##


class _CachedFunction(Abstract, ta.Generic[T]):
    """
    Root of all cached-function wrappers: holds the shared Opts type and the state surface the generated code operates
    on. Heavy (metadata-carrying) wrappers populate it via _FullCachedFunction's init; bound wrappers mostly inherit it
    as class attributes of their per-descriptor generated class.
    """

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

    _opts: Opts
    _key_maker: CacheKeyMaker | None
    _value_fn: ta.Callable
    _values: ta.MutableMapping | None  # None exactly when the species is nullary (single-slot storage)
    _v: ta.Any  # the nullary single slot - _MISSING when empty
    _lock: ta.Any
    _cache_exceptions: type[BaseException] | tuple[type[BaseException], ...] | None

    def reset(self) -> None:
        if self._values is not None:
            self._values = self._opts.map_maker()
        self._v = _MISSING

    def __bool__(self) -> bool:
        # Guards against accidental truthiness checks (`if f:`) - a cached wrapper is not its value.
        raise TypeError

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        # Concrete species classes are given generated implementations - see _SpeciesCodeGen.
        raise NotImplementedError


#


class _FullCachedFunction(_CachedFunction[T], Abstract):
    """Shared heavy init for the wrappers that own their fn and carry wrapper metadata: free fns and descriptors."""

    def __init__(
            self,
            fn: ta.Callable[P, T],
            *,
            opts: _CachedFunction.Opts,
            key_maker: CacheKeyMaker | None = None,
            no_map: bool = False,
            values: ta.MutableMapping | None = None,
            value_fn: ta.Callable[P, T] | None = None,
    ) -> None:
        super().__init__()

        # Metadata is copied first so the state set below can't be clobbered by entries in a wrapped function's __dict__
        # (such as when wrapping another cached function).
        if not opts.no_wrapper_update:
            functools.update_wrapper(self, fn)

        self._fn = fn
        self._opts = opts
        self._key_maker = key_maker
        self._value_fn = value_fn if value_fn is not None else fn
        self._values = values if values is not None else (None if no_map else opts.map_maker())
        self._v = _MISSING
        self._lock = lf() if (lf := _lock_factory(opts.lock)) is not None else None
        self._cache_exceptions = opts.cache_exceptions


#


class _FreeCachedFunction(_FullCachedFunction[T], Abstract):
    """Species base for free (non-descriptor) caches: plain fns, runtime-bound methods, and staticmethods."""

    def __reduce__(self):
        if self._opts.transient:
            state = None
        elif self._v is not _MISSING:
            state = (True, self._v)  # nullary species: the value lives in the single slot
        else:
            state = (False, self._values)
        return (_unpickle_free, (self._fn, self._opts, state))


#


class _DescriptorCachedFunction(_FullCachedFunction[T], Abstract):
    """
    Species base for the descriptor of instance methods (scope=None) and classmethods (scope=classmethod). It is itself
    a directly-callable species (for when called as a plain function, e.g. a module-level cache), and additionally
    provides `__get__`: generated (with the warm bind inlined) for instance scope, hand-written (cold) for classmethod
    scope.
    """

    def __init__(
            self,
            fn: ta.Callable[P, T],
            scope: ta.Any,  # classmethod | None
            *,
            name: str | None = None,
            bound_resolution: _ResolvedKeyShape | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(fn, **kwargs)

        self._scope = scope
        self._given_name = name
        self._name: str = name if name is not None else unwrap_func(fn).__name__
        self._set_name: str | None = None
        self._bound_resolution = bound_resolution

        opts = self._opts
        self._meta: ta.Mapping[str, ta.Any] | None = None if opts.no_wrapper_update else self._make_wrapper_meta()

        # Populated once by _ensure_bound (all None/absent until then - _bound_cls doubles as the warm/cold sentinel
        # in the generated __get__):
        self._bound_cls: type | None = None
        self._bound_fn_get: ta.Any = None  # fn.__get__, or None for raw-fn species
        self._bound_map_maker: ta.Callable[[], ta.MutableMapping] | None = None  # None for nullary species
        self._bound_lock_factory: ta.Callable[[], ta.Any] | None = None
        self._unbound: _UnboundCachedMethod | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        if self._given_name is not None:
            return

        if self._set_name is None:
            self._set_name = name
            if name != self._name:
                # Adopt the attribute name so per-instance installs land on the attribute actually being accessed
                # (fn.__name__ may differ, e.g. `foo = cached_function(_impl)`).
                self._name = name

        elif name != self._set_name:
            raise TypeError(
                f'Cannot assign the same {type(self).__name__} to two different names: '
                f'{self._set_name!r} and {name!r}',
            )

    def __reduce__(self):
        # Module-level cached functions pickle by reference, exactly like the plain functions they wrap (and like
        # functools.lru_cache wrappers). In-class descriptors don't resolve by qualname (class attribute access yields
        # the bound/unbound wrappers, not the descriptor) and so fail with PicklingError, as they must - they are class
        # attributes, pickled only as part of their class. Read from __dict__ - plain attribute access would fall back
        # to the species class's own __qualname__ when metadata is absent (no_wrapper_update).
        try:
            return self.__dict__['__qualname__']
        except KeyError:
            raise TypeError(self) from None

    def _make_wrapper_meta(self) -> dict[str, ta.Any]:
        """
        The precomputed functools.update_wrapper-equivalent dict: splatted into the unbound singleton's instance dict,
        and (descriptor-neutralized) into the bound class's namespace. Per update_wrapper, __wrapped__ is set last so
        the fn __dict__ copy can't shadow it.
        """

        fn = self._fn
        meta: dict[str, ta.Any] = {}
        for a in functools.WRAPPER_ASSIGNMENTS:
            try:
                meta[a] = getattr(fn, a)
            except AttributeError:
                pass
        meta.update(getattr(fn, '__dict__', ()))
        meta['__wrapped__'] = fn
        return meta

    def _ensure_bound(self) -> type:
        fn = self._fn
        opts = self._opts
        dict_map = opts.map_maker is dict

        if (res := self._bound_resolution) is None:
            res = _resolve_key_shape(fn, bound=True, slot_ok=dict_map, make_key_maker=False)
        nullary = res.key_shape is _KeyShape.NULLARY
        km = _make_cache_key_maker(fn, bound=True) if res.key_shape is _KeyShape.GENERAL else None
        raw = type(fn) is types.FunctionType and self._scope is None

        self._bound_fn_get = fn.__get__ if not raw else None
        self._bound_map_maker = opts.map_maker if not nullary else None
        self._bound_lock_factory = _lock_factory(opts.lock)

        species = _get_species(_CacheSpec(
            bind_kind=_BindKind.BOUND,
            key_shape=res.key_shape,
            shape=res.shape,
            cls_scope=self._scope is classmethod,
            locked=self._bound_lock_factory is not None,
            cache_exceptions=opts.cache_exceptions is not None,
            raw_fn=raw,
        ))

        # The per-descriptor bound class: everything shared across this method's bindings lives here as class
        # attributes, leaving per-bind instance dicts holding only the truly per-instance state. Class attributes bind
        # on access, so descriptor-valued entries are neutralized: function values are staticmethod-wrapped, and the
        # back-reference to this descriptor (itself a __get__ provider!) is tuple-wrapped behind the _desc property.
        bag: dict[str, ta.Any] = {}
        if (meta := self._meta) is not None:
            for k, v in meta.items():
                bag[k] = staticmethod(v) if isinstance(v, types.FunctionType) else v
        bag.update(
            _desc_t=(self,),
            _opts=opts,
            _cache_exceptions=opts.cache_exceptions,
            _key_maker=staticmethod(km) if km is not None else None,
            _instance=None,
            _owner=None,
            _values=None,
            _v=_MISSING,
            _lock=None,
        )
        if raw:
            bag['_raw_fn'] = staticmethod(fn)

        self._bound_cls = bcls = type(self._name, (species,), bag)
        return bcls

    def _bind(
            self,
            instance: ta.Any,
            owner: ta.Any = None,
            *,
            values: ta.MutableMapping | None = None,
    ) -> _BoundCachedFunction:
        # The cold bind path: species/class assurance, unpickling, and classmethod-scope installs. The warm
        # instance-scope path is inlined into the generated __get__ and never reaches here.
        if (bcls := self._bound_cls) is None:
            bcls = self._ensure_bound()

        bound = bcls(instance, owner, values)

        if self._scope is classmethod:
            if owner is not None:
                setattr(owner, self._name, bound)
        elif instance is not None:
            instance.__dict__[self._name] = bound

        return bound

    def _get_unbound(self) -> _UnboundCachedMethod:
        if (u := self._unbound) is None:
            self._unbound = u = _UnboundCachedMethod(self)
        return u


#


class _BoundCachedFunction(_CachedFunction[T], Abstract):
    """
    Species base for the lightweight per-instance / per-owner wrapper a descriptor produces on __get__. Shared state
    lives as class attributes of the per-descriptor generated subclass; this (cold-path) init exists for unpickling and
    classmethod-scope binds - warm instance binds are inlined into the descriptor's generated __get__ and bypass it.
    """

    # The back-reference to the owning descriptor, tuple-wrapped in the per-descriptor class's namespace (a bare class
    # attr would invoke the descriptor's own __get__ on access).
    _desc_t: ta.ClassVar[tuple]

    def __init__(
            self,
            instance: ta.Any,
            owner: ta.Any = None,
            values: ta.MutableMapping | None = None,
    ) -> None:
        super().__init__()

        desc = self._desc
        self._instance = instance
        self._owner = owner
        if (fg := desc._bound_fn_get) is not None:  # noqa
            self._value_fn = fg(instance, owner)
        if (mm := desc._bound_map_maker) is not None:  # noqa
            self._values = values if values is not None else mm()
        if (lf := desc._bound_lock_factory) is not None:  # noqa
            self._lock = lf()

    @property
    def _desc(self) -> _DescriptorCachedFunction:
        return self._desc_t[0]  # noqa  # provided by the per-descriptor class

    def __reduce__(self):
        desc = self._desc
        if desc._scope is not None:  # noqa
            raise TypeError(self)
        if self._instance is None:
            raise TypeError(self)

        if desc._opts.transient:  # noqa
            state = None
        elif self._v is not _MISSING:
            state = (True, self._v)  # nullary species: the value lives in the single slot
        else:
            state = (False, self._values)
        return (_unpickle_bound, (self._instance, desc._name, state))  # noqa


#


class _UnboundCachedMethod:
    """
    Returned (as a per-descriptor singleton) by an instance-scope descriptor's __get__ for class-level access (`A.f`).
    Calling it as `A.f(inst, ...)` routes to inst's own per-instance cache - inst is clipped off and never keyed, and
    storage lives on inst, exactly as `inst.f(...)` would.
    """

    def __init__(self, desc: _DescriptorCachedFunction) -> None:
        super().__init__()

        if (meta := desc._meta) is not None:  # noqa
            self.__dict__.update(meta)
        self._desc = desc

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._desc!r})'

    def __bool__(self) -> bool:
        raise TypeError

    def __reduce__(self):
        # `A.f` pickles by reference (like a plain function's would) when the fn's qualname resolves back to this
        # singleton - which it does exactly when the descriptor sits in its defining class under its own name. Read
        # from __dict__ - plain attribute access would fall back to the class's own __qualname__ when metadata is
        # absent (no_wrapper_update).
        try:
            return self.__dict__['__qualname__']
        except KeyError:
            raise TypeError(self) from None

    def __call__(self, instance, /, *args, **kwargs):
        name = (desc := self._desc)._name  # noqa

        if (d := getattr(instance, '__dict__', None)) is not None and (b := d.get(name, _MISSING)) is not _MISSING:
            # Something already occupies the attribute slot on the instance: if it's our own bound wrapper, use it -
            # otherwise (a manually-set attribute, a subclass override's wrapper) leave it alone and fall through to an
            # uncached call.
            if isinstance(b, _BoundCachedFunction) and b._desc is desc:  # noqa
                return b(*args, **kwargs)

        else:
            # Only install a bound wrapper when the instance's own attribute resolution would reach this exact
            # descriptor - installing while a subclass override (or anything else) owns the name would poison that
            # name's cache slot.
            for klass in type(instance).__mro__:
                if name in klass.__dict__:
                    if klass.__dict__[name] is desc:
                        return desc._bind(instance, type(instance))(*args, **kwargs)  # noqa
                    break

        # Correct-but-uncached escape hatch: call the descriptor's fn bound to the instance, python semantics exactly.
        return desc._fn.__get__(instance, type(instance))(*args, **kwargs)  # noqa


##
# Hand-written __get__ variants for the cold or trivial cases. The hot one - instance-scope descriptor binding - is
# generated per species with the warm bind inlined (see _SpeciesCodeGen.render_get).


def _cls_descriptor_get(self, instance, owner=None):
    # Cold: runs once per owner class - the installed bound wrapper shadows this descriptor thereafter.
    return self._bind(None, owner)


def _instance_bound_get(self, instance, owner=None):
    # Instance-scope bound wrappers live in instance __dict__s and thus aren't normally descriptor-accessed - handled
    # anyway for manual class-attribute placement.
    if instance is None or instance is self._instance:
        return self
    return self._desc._bind(instance, owner)  # noqa


def _cls_bound_get(self, instance, owner=None):
    # Runs on every class-level access of an owner-installed classmethod-scope wrapper: rebind only when accessed
    # through a different owner (a subclass), giving subclasses their own per-owner cache.
    if owner is self._owner:
        return self
    return self._desc._bind(None, owner)  # noqa


##


def _species_tag(spec: _CacheSpec) -> str:
    return '_'.join([
        (
            f'inline{len(spec.shape)}' if spec.key_shape is _KeyShape.INLINE and spec.shape is not None
            else spec.key_shape.name.lower()
        ),
        spec.bind_kind.name.lower(),
        *(['cls'] if spec.cls_scope else []),
        *(['locked'] if spec.locked else []),
        *(['exc'] if spec.cache_exceptions else []),
        *(['raw'] if spec.raw_fn else []),
    ])


class _SpeciesCodeGen(Final):
    """
    Generates a species' hot code by composing per-axis fragments rather than enumerating every axis intersection: one
    signature fragment, one key fragment, one probe fragment, one store fragment (with original-call reconstruction for
    the INLINE tier), one unwrap fragment, a `locked` transform that wraps the miss path in a double-checked `with`
    block, and (for instance-scope descriptors) a __get__ with the warm bind inlined. Adding an axis means
    adding/adjusting one fragment, not doubling blocks.

    All generated names are __-prefixed (the exec namespace's helpers, the wrapper's own self slot, body locals) so
    INLINE signatures can carry arbitrary non-__-prefixed param names - including `self` - without collision.
    """

    def __init__(self, spec: _CacheSpec) -> None:
        super().__init__()

        self._spec = spec
        self._shape = spec.shape
        self._nullary = spec.key_shape is _KeyShape.NULLARY
        self._inline = spec.key_shape is _KeyShape.INLINE
        self._exc = spec.cache_exceptions

        self._ns: dict[str, ta.Any] = {
            '__missing': _MISSING,
            '__omitted': _OMITTED_ARG,
            '__cexc': _CachedException,
            '__tuple': tuple,
            '__sorted': sorted,
            '__new': object.__new__,
        }

    _INDENT: ta.ClassVar[str] = '    '

    @classmethod
    def _indent(cls, lines: ta.Iterable[str]) -> list[str]:
        return [cls._INDENT + l for l in lines]

    @property
    def ns(self) -> ta.Mapping[str, ta.Any]:
        return self._ns

    @property
    def call_name(self) -> str:
        return f'_cached_call__{_species_tag(self._spec)}'

    @property
    def get_name(self) -> str:
        return f'_cached_get__{_species_tag(self._spec)}'

    # __call__ fragments:

    def params_src(self) -> str:
        if self._nullary:
            return '(__self, /)'
        if not self._inline:
            return '(__self, /, *args, **kwargs)'

        shape = ta.cast(tuple, self._shape)
        out = ['__self']
        if '/' not in shape:
            out.append('/')
        for e in shape:
            if isinstance(e, str):
                out.append(e)
                continue
            kind, name, dflt = e
            if kind == 'va':
                out.append(f'*{name}')
            elif kind == 'vk':
                out.append(f'**{name}')
            elif dflt:
                out.append(f'{name}=__omitted')  # the omitted-arg key sentinel - see _OmittedArgSentinel
            else:
                out.append(name)
        return f'({", ".join(out)})'

    def key_lines(self) -> list[str]:
        # Nothing for NULLARY (slot storage); the key maker for GENERAL; inline construction for INLINE, with a bare
        # un-tupled key when there is exactly one contribution (safe: two calls produce equal bare keys iff they would
        # produce equal 1-tuples).
        if self._nullary:
            return []
        if not self._inline:
            return ['__k = __self._key_maker(*args, **kwargs)']

        ks = []
        for e in ta.cast(tuple, self._shape):
            if isinstance(e, str):
                continue
            kind, name, _ = e
            if kind == 'vk':
                ks.append(f'__tuple(__sorted({name}.items()))')
            else:
                ks.append(name)
        if len(ks) == 1:
            return [f'__k = {ks[0]}']
        return [f'__k = ({", ".join(ks)})']

    def compute_src(self) -> tuple[list[str], str]:
        """
        Returns (pre-lines, call-src) for invoking the value fn on a miss. For the INLINE tier this reconstructs the
        original call: non-defaulted positionals pass positionally, defaulted params whose value is the omission
        sentinel are omitted (rebuilt into a kwargs dict - equivalent for pk/ko params only in the absence of *args,
        which is why defaulted positional-only params and defaulted pos-or-kw params preceding *args are GENERAL-tier).
        """

        spec = self._spec

        if self._nullary:
            args_src = ''
            pre: list[str] = []
        elif not self._inline:
            args_src = '*args, **kwargs'
            pre = []
        else:
            pos: list[str] = []
            kw_direct: list[str] = []
            kw_cond: list[str] = []
            va = vk = None
            for e in ta.cast(tuple, self._shape):
                if isinstance(e, str):
                    continue
                kind, name, dflt = e
                if kind == 'va':
                    va = name
                elif kind == 'vk':
                    vk = name
                elif dflt:
                    kw_cond.append(name)
                elif kind == 'ko':
                    kw_direct.append(name)
                else:  # po / pk without defaults - always a positional prefix
                    pos.append(name)

            parts = [*pos]
            if va is not None:
                parts.append(f'*{va}')
            parts += [f'{n}={n}' for n in kw_direct]
            pre = []
            if kw_cond:
                pre.append('__kw = {}')
                for n in kw_cond:
                    pre.append(f'if {n} is not __omitted:')
                    pre.append(f'    __kw[{n!r}] = {n}')
                parts.append('**__kw')
            if vk is not None:
                parts.append(f'**{vk}')
            args_src = ', '.join(parts)

        if spec.raw_fn:
            call = f'__self._raw_fn(__self._instance{", " if args_src else ""}{args_src})'
        else:
            call = f'__self._value_fn({args_src})'
        return pre, call

    def unwrap_lines(self) -> list[str]:
        # The single place cache_exceptions changes how a hit (or freshly stored value) in `__v` is yielded.
        if not self._exc:
            return ['return __v']
        return [
            'if type(__v) is __cexc:',
            '    raise __v.ex',
            'return __v',
        ]

    def probe_lines(self) -> list[str]:
        # Probe the cache: on a hit, return (unwrapping a cached exception); on a miss, fall through. The unwrap must
        # sit in the `else` clause, outside the `except KeyError` scope - a cached KeyError re-raised inside it would
        # be swallowed as a miss and recomputed forever.
        if self._nullary:
            return [
                'if (__v := __self._v) is not __missing:',
                *self._indent(self.unwrap_lines()),
            ]
        return [
            'try:',
            '    __v = __self._values[__k]',
            'except KeyError:',
            '    pass',
            'else:',
            *self._indent(self.unwrap_lines()),
        ]

    def store_lines(self) -> list[str]:
        # Compute and store. The single place cache_exceptions changes computation: a matching exception is stored
        # wrapped rather than propagated.
        pre, call = self.compute_src()
        target = '__self._v' if self._nullary else '__self._values[__k]'
        if not self._exc:
            return [*pre, f'{target} = __v = {call}']
        return [
            *pre,
            'try:',
            f'    __v = {call}',
            'except __self._cache_exceptions as __e:',
            '    __v = __cexc(__e)',
            f'{target} = __v',
        ]

    def call_lines(self) -> list[str]:
        lines = self.key_lines()
        lines += self.probe_lines()

        miss = [
            *(self.probe_lines() if self._spec.locked else []),  # double-checked in-lock re-probe
            *self.store_lines(),
        ]
        if self._spec.locked:
            lines += ['with __self._lock:', *self._indent(miss)]
        else:
            lines += miss

        lines += self.unwrap_lines()
        return lines

    # __get__ (instance-scope descriptor only): the warm bind, inlined - one frame, no dead branches:

    def get_lines(self) -> list[str]:
        spec = self._spec

        entries = ["'_instance': instance"]
        if not spec.bound_raw_fn:
            entries.append("'_value_fn': __self._bound_fn_get(instance, owner)")
        if not spec.bound_nullary:
            entries.append("'_values': {}" if spec.dict_map else "'_values': __self._bound_map_maker()")
        if spec.locked:
            entries.append("'_lock': __self._bound_lock_factory()")

        return [
            'if instance is None:',
            '    if owner is None:',
            '        return __self',
            '    return __self._get_unbound()',
            'if (__bcls := __self._bound_cls) is None:',
            '    return __self._bind(instance, owner)',
            f'(__b := __new(__bcls)).__dict__ = {{{", ".join(entries)}}}',
            'instance.__dict__[__self._name] = __b',
            'return __b',
        ]

    def render(self) -> str:
        spec = self._spec
        blocks = [
            '\n'.join([
                f'def {self.call_name}{self.params_src()}:',
                *self._indent(self.call_lines()),
            ]),
        ]
        if spec.bind_kind is _BindKind.DESCRIPTOR and not spec.cls_scope:
            blocks.append('\n'.join([
                f'def {self.get_name}(__self, instance, owner=None):',
                *self._indent(self.get_lines()),
            ]))
        return '\n\n\n'.join([*blocks, ''])


#


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

    cg = _SpeciesCodeGen(spec)
    src = cg.render()
    ns = dict(cg.ns)
    _exec_src(src, _register_gen_src(cg.call_name, src), ns)  # noqa

    dct: dict = {'__call__': ns[cg.call_name]}
    if spec.bind_kind is _BindKind.DESCRIPTOR:
        dct['__get__'] = _cls_descriptor_get if spec.cls_scope else ns[cg.get_name]
    elif spec.bind_kind is _BindKind.BOUND:
        dct['__get__'] = _cls_bound_get if spec.cls_scope else _instance_bound_get

    cls = type(
        f'_CachedFunction[{_species_tag(spec)}]',
        (_SPECIES_BASES_BY_BIND_KIND[spec.bind_kind],),
        dct,
    )
    # setdefault so concurrent first-computations converge on one class.
    return _SPECIES_CACHE.setdefault(spec, cls)


##


def _make_free(
        fn: ta.Any,
        opts: _CachedFunction.Opts,
        *,
        values: ta.MutableMapping | None = None,
) -> _FreeCachedFunction:
    if isinstance(fn, types.MethodType):
        value_fn, bound = fn, True
    elif isinstance(fn, staticmethod):
        value_fn, bound = unwrap_func(fn), False
    else:
        value_fn, bound = fn, False

    res = _resolve_key_shape(fn, bound=bound, slot_ok=opts.map_maker is dict)

    species = _get_species(_CacheSpec(
        bind_kind=_BindKind.FREE,
        key_shape=res.key_shape,
        shape=res.shape,
        locked=_lock_factory(opts.lock) is not None,
        cache_exceptions=opts.cache_exceptions is not None,
    ))

    return species(
        fn,
        opts=opts,
        key_maker=res.key_maker,
        no_map=res.key_shape is _KeyShape.NULLARY,
        values=values,
        value_fn=value_fn,
    )


def _make_descriptor(
        fn: ta.Any,
        scope: ta.Any,
        opts: _CachedFunction.Opts,
) -> _DescriptorCachedFunction:
    dict_map = opts.map_maker is dict
    cls_scope = scope is classmethod

    # The descriptor's own (direct-call) key is unbound - it keys every argument, for when the descriptor is called as
    # a plain function (e.g. a module-level cache). This resolution also performs the generator/coroutine rejection.
    res = _resolve_key_shape(fn, slot_ok=dict_map)

    # The bound side is resolved (cheaply - no compilation) now so the species can be fully specified; the bound key
    # maker / class themselves stay lazy (_ensure_bound, at first bind).
    bound_res = _resolve_key_shape(fn, bound=True, slot_ok=dict_map, make_key_maker=False)
    bound_nullary = bound_res.key_shape is _KeyShape.NULLARY
    bound_raw = type(fn) is types.FunctionType and not cls_scope

    species = _get_species(_CacheSpec(
        bind_kind=_BindKind.DESCRIPTOR,
        key_shape=res.key_shape,
        shape=res.shape,
        cls_scope=cls_scope,
        locked=_lock_factory(opts.lock) is not None,
        cache_exceptions=opts.cache_exceptions is not None,
        dict_map=True if (cls_scope or bound_nullary) else dict_map,
        bound_nullary=False if cls_scope else bound_nullary,
        bound_raw_fn=bound_raw,
    ))

    return species(
        fn,
        scope,
        opts=opts,
        key_maker=res.key_maker,
        no_map=res.key_shape is _KeyShape.NULLARY,
        bound_resolution=bound_res,
        # The raw classmethod object is not callable - direct calls take the unbound (cls, ...) signature, matching
        # the unbound direct-call keying above.
        value_fn=unwrap_func(fn) if cls_scope else None,
    )


#


def _unpickle_free(fn, opts, state):
    if state is None:
        return _make_free(fn, opts)

    slot, data = state
    if slot:
        cf = _make_free(fn, opts)
        cf._v = data  # noqa
        return cf
    return _make_free(fn, opts, values=data)


def _unpickle_bound(instance, name, state):
    cls = type(instance)

    desc: _DescriptorCachedFunction
    for bc in cls.__mro__:
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
        return desc._bind(instance, cls)  # noqa

    slot, data = state
    if slot:
        bound = desc._bind(instance, cls)  # noqa
        bound._v = data  # noqa
        return bound
    return desc._bind(instance, cls, values=data)  # noqa


##


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
