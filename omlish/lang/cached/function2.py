"""
A cached-function ('memoization') mechanism supporting free functions, bound methods, staticmethods, classmethods, and
instance methods, with full descriptor-protocol and python-calling-convention fidelity.

The implementation is 'species'-based: the axes of a cache configuration that shape its hot code paths (key shape, bind
kind, scope, locking, exception caching) form a small NamedTuple (_CacheSpec), and a concrete class per spec - its
'species' - is generated, cached, and reused, much like the stdlib dataclasses/namedtuple machinery. The hot `__call__`
is fully code-generated per species (see _CallCodeGen), `__get__` is selected per species from prewritten per-scope
variants (removing all scope branching from bind paths), and everything cold (init, pickling, reset) lives on
hand-written base classes chosen by bind kind.

Key makers are themselves code-generated per wrapped-function signature, canonicalizing a call's (*args, **kwargs) into
a hashable tuple key while exactly reproducing the wrapped function's calling convention - including positional-only /
keyword-only separators, defaults (an omitted arg is keyed by a stable sentinel, distinct from explicitly passing the
default's value, matching functools.lru_cache), and **kwargs (keyed order-insensitively). Nullary species bypass key
making and the backing map entirely, caching in a single slot.

Binding is instance-dict based: a descriptor's `__get__` installs a lightweight per-instance bound wrapper in
`instance.__dict__[name]` (shadowing the non-data descriptor - later accesses never re-bind), holding its own values and
bound value fn. No shared/global store exists, no hard instance refs are held outside the instance itself, and `self`
is never a key component (bound key makers clip it). Classmethod-scope wrappers install on the owner class analogously.
`A.f(inst, ...)` routes through inst's own per-instance cache exactly as `inst.f(...)` would.

All generated source is registered with linecache under virtual filenames, so debuggers can step it and tracebacks
render it.

A future optional cext will replace the generated species with a single heap type switching on the same _CacheSpec axes
(python-level codegen becomes C-level iffing) - _get_species is the single seam where that swaps in. The python-side key
maker remains the calling-convention authority; only the nullary fast path may skip it.

TODO:
 - cext species (see above) - also gets the hot path out of debugger singlestepping
 - POSITIONAL key shape: no-default, no-vararg signatures can key `args` directly when no kwargs are passed
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
import linecache
import types
import typing as ta

from ..classes.abstract import Abstract
from ..classes.restrict import Final
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


_GEN_SRC_COUNT = itertools.count()


def _register_gen_src(name: str, src: str) -> str:
    """
    Registers generated source with linecache under a unique virtual filename (returned, for compile()) so debuggers can
    step it and tracebacks render it.
    """

    filename = f'<generated:{__name__}:{next(_GEN_SRC_COUNT)}:{name}>'
    linecache.cache[filename] = (len(src), None, src.splitlines(keepends=True), filename)
    return filename


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
    exec(compile(rendered, filename, 'exec'), ns)  # noqa

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


#


class _KeyShape(enum.Enum):
    NULLARY = enum.auto()  # zero effective params -> single-slot storage, no key maker, no backing map
    GENERAL = enum.auto()  # arbitrary signature -> backed by the codegen'd key maker + mapping


class _BindKind(enum.Enum):
    FREE = enum.auto()        # top-level callable: plain fn, runtime-bound method, staticmethod - no __get__
    BOUND = enum.auto()       # per-instance / per-owner wrapper produced by a descriptor's __get__
    DESCRIPTOR = enum.auto()  # the descriptor for an instance/class method: directly callable AND a __get__ provider


class _CacheSpec(ta.NamedTuple):
    """
    The axes of a cache configuration that shape its generated/selected hot code paths. Everything per-wrapper
    (values, locks, fns) lives on wrapper instances; a future cext species is one heap type switching on these axes.
    """

    key_shape: _KeyShape
    bind_kind: _BindKind
    cls_scope: bool  # classmethod scoping - selects the __get__ variant; always False for FREE
    locked: bool
    cache_exceptions: bool


#


def _opts_locked(opts: _CachedFunction.Opts) -> bool:
    return opts.lock is not None and opts.lock is not False


def _opts_lock(opts: _CachedFunction.Opts) -> ta.Any:
    # NOTE: called per wrapper construction - `lock=True` deliberately yields a fresh lock per bound instance.
    return default_lock(opts.lock, False)() if _opts_locked(opts) else None


##


class _CachedFunction(Abstract, ta.Generic[T]):
    """
    Root of all cached-function wrappers: holds the shared Opts type and the state surface the generated `__call__`s
    operate on. Subclass inits populate the state - heavy (metadata-carrying) wrappers via _FullCachedFunction, bound
    wrappers via a proto-dict splat.
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
    _key_maker: CacheKeyMaker
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
        # Concrete species classes are given generated implementations - see _CallCodeGen.
        raise NotImplementedError


#


class _FullCachedFunction(_CachedFunction[T], Abstract):
    """Shared heavy init for the wrappers that own their fn and carry wrapper metadata: free fns and descriptors."""

    def __init__(
            self,
            fn: ta.Callable[P, T],
            *,
            opts: _CachedFunction.Opts,
            key_maker: CacheKeyMaker,
            no_map: bool = False,
            values: ta.MutableMapping | None = None,
            value_fn: ta.Callable[P, T] | None = None,
    ) -> None:
        super().__init__()

        # Metadata is copied first so the state set below can't be clobbered by entries in a wrapped function's
        # __dict__ (such as when wrapping another cached function).
        if not opts.no_wrapper_update:
            functools.update_wrapper(self, fn)

        self._fn = (fn,)
        self._opts = opts
        self._key_maker = key_maker
        self._value_fn = value_fn if value_fn is not None else fn
        self._values = values if values is not None else (None if no_map else opts.map_maker())
        self._v = _MISSING
        self._lock = _opts_lock(opts)
        self._cache_exceptions = opts.cache_exceptions

    # `_fn` is exposed through a property (a data descriptor) so that the functools.update_wrapper __dict__ copy above
    # can never shadow it - the actual storage is the mangled `__fn` instance attr. It is tuple-wrapped to inertly
    # survive any descriptor machinery it may pass through.
    @property
    def _fn(self):
        return self.__fn

    @_fn.setter
    def _fn(self, x):
        self.__fn = x


#


class _FreeCachedFunction(_FullCachedFunction[T], Abstract):
    """Species base for free (non-descriptor) caches: plain fns, runtime-bound methods, and staticmethods."""

    def __reduce__(self):
        fn, = self._fn
        if self._opts.transient:
            state = None
        elif self._v is not _MISSING:
            state = (True, self._v)  # nullary species: the value lives in the single slot
        else:
            state = (False, self._values)
        return (_unpickle_free, (fn, self._opts, state))


#


class _DescriptorCachedFunction(_FullCachedFunction[T], Abstract):
    """
    Species base for the descriptor of instance methods (scope=None) and classmethods (scope=classmethod). It is itself
    a directly-callable species (for when called as a plain function, e.g. a module-level cache), and additionally
    provides `__get__` (selected per scope), producing lightweight per-instance/owner _BoundCachedFunctions on access.
    """

    def __init__(
            self,
            fn: ta.Callable[P, T],
            scope: ta.Any,  # classmethod | None
            *,
            name: str | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(fn, **kwargs)

        self._scope = scope
        self._given_name = name
        self._name: str = name if name is not None else unwrap_func(fn).__name__
        self._set_name: str | None = None

        opts = self._opts
        self._meta: ta.Mapping[str, ta.Any] | None = None if opts.no_wrapper_update else self._make_wrapper_meta()

        self._bound_species: type | None = None
        self._bound_key_maker: CacheKeyMaker | None = None
        self._bound_map_maker: ta.Callable[[], ta.MutableMapping] | None = None
        self._bound_proto: dict[str, ta.Any] | None = None
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
                if (bp := self._bound_proto) is not None:
                    bp['_name'] = name

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
        The precomputed functools.update_wrapper-equivalent dict splatted into each bound wrapper's __dict__ - one
        C-speed dict update per bind instead of a python attr-copy loop. Per update_wrapper, __wrapped__ is set last so
        the fn __dict__ copy can't shadow it.
        """

        fn, = self._fn
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
        fn, = self._fn
        opts = self._opts

        self._bound_key_maker = km = _make_cache_key_maker(fn, bound=True)
        nullary = km is _nullary_cache_key_maker and opts.map_maker is dict
        self._bound_map_maker = None if nullary else opts.map_maker

        proto: dict[str, ta.Any] = dict(self._meta) if self._meta is not None else {}
        proto.update(
            # State defaults - _values/_lock are overridden per-bind as needed. Set after the metadata so entries in a
            # wrapped fn's __dict__ can't clobber them.
            _values=None,
            _v=_MISSING,
            _lock=None,
            # Config shared by every bound wrapper of this descriptor.
            _opts=opts,
            _name=self._name,
            _key_maker=km,
            _cache_exceptions=opts.cache_exceptions,
        )
        self._bound_proto = proto

        self._bound_species = bs = _get_species(_CacheSpec(
            key_shape=_KeyShape.NULLARY if nullary else _KeyShape.GENERAL,
            bind_kind=_BindKind.BOUND,
            cls_scope=self._scope is classmethod,
            locked=_opts_locked(opts),
            cache_exceptions=opts.cache_exceptions is not None,
        ))
        return bs

    def _bind(
            self,
            instance: ta.Any,
            owner: ta.Any = None,
            *,
            values: ta.MutableMapping | None = None,
    ) -> _BoundCachedFunction:
        if (species := self._bound_species) is None:
            species = self._ensure_bound()

        fn, = self._fn
        bound = species(self, instance, owner, fn.__get__(instance, owner), values)

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
    Species base for the lightweight per-instance / per-owner wrapper a descriptor produces on __get__. Construction is
    deliberately minimal - a precomputed proto-dict splat (metadata + shared config + state defaults) plus a few
    per-bind fields - as it runs on the first access of every new instance.
    """

    def __init__(
            self,
            desc: _DescriptorCachedFunction,
            instance: ta.Any,
            owner: ta.Any,
            value_fn: ta.Callable,
            values: ta.MutableMapping | None = None,
    ) -> None:
        super().__init__()

        self.__dict__.update(desc._bound_proto)  # type: ignore[arg-type]  # noqa  # always set by _ensure_bound
        self._desc = desc
        self._instance = instance
        self._owner = owner
        self._value_fn = value_fn
        if (mm := desc._bound_map_maker) is not None:  # noqa
            self._values = values if values is not None else mm()
        if (lock := _opts_lock(desc._opts)) is not None:  # noqa
            self._lock = lock

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
        desc = self._desc
        name = desc._name  # noqa

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
        fn, = desc._fn  # noqa
        return fn.__get__(instance, type(instance))(*args, **kwargs)


##
# Per-scope __get__ variants, selected per species (no scope branching remains on any bind path). These are plain
# functions rather than generated code - they don't compose axis-wise like __call__ does, and real source beats exec'd
# source when stepping.


def _instance_descriptor_get(self, instance, owner=None):
    if instance is None:
        if owner is None:
            return self
        return self._get_unbound()
    return self._bind(instance, owner)


def _cls_descriptor_get(self, instance, owner=None):
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
        spec.key_shape.name.lower(),
        spec.bind_kind.name.lower(),
        *(['cls'] if spec.cls_scope else []),
        *(['locked'] if spec.locked else []),
        *(['exc'] if spec.cache_exceptions else []),
    ])


class _CallCodeGen(Final):
    """
    Generates a species' hot `__call__` by composing per-axis fragments rather than enumerating every axis
    intersection: one probe fragment, one store fragment, one unwrap fragment, and a `locked` transform that wraps the
    miss path in a double-checked `with` block. Adding an axis means adding/adjusting one fragment, not doubling
    blocks.
    """

    def __init__(self, spec: _CacheSpec) -> None:
        super().__init__()

        self._spec = spec
        self._nullary = spec.key_shape is _KeyShape.NULLARY
        self._exc = spec.cache_exceptions

    _INDENT: ta.ClassVar[str] = '    '

    @classmethod
    def _indent(cls, lines: ta.Iterable[str]) -> list[str]:
        return [cls._INDENT + l for l in lines]

    @property
    def name(self) -> str:
        return f'_cached_call__{_species_tag(self._spec)}'

    def params_src(self) -> str:
        return '(self)' if self._nullary else '(self, *args, **kwargs)'

    def compute_src(self) -> str:
        return 'self._value_fn()' if self._nullary else 'self._value_fn(*args, **kwargs)'

    def unwrap_lines(self) -> list[str]:
        # The single place cache_exceptions changes how a hit (or freshly stored value) in `v` is yielded.
        if not self._exc:
            return ['return v']
        return [
            'if type(v) is _CachedException:',
            '    raise v.ex',
            'return v',
        ]

    def probe_lines(self) -> list[str]:
        # Probe the cache: on a hit, return (unwrapping a cached exception); on a miss, fall through. The unwrap must
        # sit in the `else` clause, outside the `except KeyError` scope - a cached KeyError re-raised inside it would
        # be swallowed as a miss and recomputed forever.
        if self._nullary:
            return [
                'if (v := self._v) is not _MISSING:',
                *self._indent(self.unwrap_lines()),
            ]
        return [
            'try:',
            '    v = self._values[k]',
            'except KeyError:',
            '    pass',
            'else:',
            *self._indent(self.unwrap_lines()),
        ]

    def store_lines(self) -> list[str]:
        # Compute and store. The single place cache_exceptions changes computation: a matching exception is stored
        # wrapped rather than propagated.
        target = 'self._v' if self._nullary else 'self._values[k]'
        if not self._exc:
            return [f'{target} = v = {self.compute_src()}']
        return [
            'try:',
            f'    v = {self.compute_src()}',
            'except self._cache_exceptions as e:',
            '    v = _CachedException(e)',
            f'{target} = v',
        ]

    def body_lines(self) -> list[str]:
        lines: list[str] = []
        if not self._nullary:
            lines.append('k = self._key_maker(*args, **kwargs)')
        lines += self.probe_lines()

        miss = [
            *(self.probe_lines() if self._spec.locked else []),  # double-checked in-lock re-probe
            *self.store_lines(),
        ]
        if self._spec.locked:
            lines += ['with self._lock:', *self._indent(miss)]
        else:
            lines += miss

        lines += self.unwrap_lines()
        return lines

    def render(self) -> str:
        return '\n'.join([
            f'def {self.name}{self.params_src()}:',
            *self._indent(self.body_lines()),
            '',
        ])


#


_SPECIES_BASES_BY_BIND_KIND: ta.Mapping[_BindKind, type] = {
    _BindKind.FREE: _FreeCachedFunction,
    _BindKind.BOUND: _BoundCachedFunction,
    _BindKind.DESCRIPTOR: _DescriptorCachedFunction,
}

_SPECIES_GETS_BY_BIND_KIND_SCOPE: ta.Mapping[tuple[_BindKind, bool], ta.Callable] = {
    (_BindKind.DESCRIPTOR, False): _instance_descriptor_get,
    (_BindKind.DESCRIPTOR, True): _cls_descriptor_get,
    (_BindKind.BOUND, False): _instance_bound_get,
    (_BindKind.BOUND, True): _cls_bound_get,
}

_SPECIES_CACHE: dict[_CacheSpec, type] = {}


def _get_species(spec: _CacheSpec) -> type:
    try:
        return _SPECIES_CACHE[spec]
    except KeyError:
        pass

    cg = _CallCodeGen(spec)
    src = cg.render()
    ns: dict = {
        '_MISSING': _MISSING,
        '_CachedException': _CachedException,
    }
    exec(compile(src, _register_gen_src(cg.name, src), 'exec'), ns)  # noqa

    dct: dict = {'__call__': ns[cg.name]}
    if (get := _SPECIES_GETS_BY_BIND_KIND_SCOPE.get((spec.bind_kind, spec.cls_scope))) is not None:
        dct['__get__'] = get

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

    key_maker = _make_cache_key_maker(fn, bound=bound)
    nullary = key_maker is _nullary_cache_key_maker and opts.map_maker is dict

    species = _get_species(_CacheSpec(
        key_shape=_KeyShape.NULLARY if nullary else _KeyShape.GENERAL,
        bind_kind=_BindKind.FREE,
        cls_scope=False,
        locked=_opts_locked(opts),
        cache_exceptions=opts.cache_exceptions is not None,
    ))

    return species(
        fn,
        opts=opts,
        key_maker=key_maker,
        no_map=nullary,
        values=values,
        value_fn=value_fn,
    )


def _make_descriptor(
        fn: ta.Any,
        scope: ta.Any,
        opts: _CachedFunction.Opts,
) -> _DescriptorCachedFunction:
    # The descriptor's own (direct-call) key maker is unbound - it keys every argument, for when the descriptor is
    # called as a plain function (e.g. a module-level cache). This also performs the generator/coroutine rejection.
    key_maker = _make_cache_key_maker(fn)
    nullary = key_maker is _nullary_cache_key_maker and opts.map_maker is dict

    species = _get_species(_CacheSpec(
        key_shape=_KeyShape.NULLARY if nullary else _KeyShape.GENERAL,
        bind_kind=_BindKind.DESCRIPTOR,
        cls_scope=scope is classmethod,
        locked=_opts_locked(opts),
        cache_exceptions=opts.cache_exceptions is not None,
    ))

    return species(
        fn,
        scope,
        opts=opts,
        key_maker=key_maker,
        no_map=nullary,
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
