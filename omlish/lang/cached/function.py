"""
TODO:
 - !! reconcile A().f() with A.f(A())
  - unbound descriptor *should* still hit instance cache
 - integrate / expose with collections.cache
 - weakrefs (selectable by arg)
 - more rigorous descriptor pickling
  - must support free functions (which have no instance nor owner)
  - 'staticmethod' or effective equiv - which must resolve to the shared instance
   - and must be transient?
 - use __transient_dict__ to support common state nuking
"""
import dataclasses as dc
import functools
import inspect
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
    for p in ps:
        if isinstance(p, ParamSeparator):
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


class _CachedFunction(ta.Generic[T], Abstract):
    @dc.dataclass(frozen=True)
    class Opts:
        map_maker: ta.Callable[[], ta.MutableMapping] = dict
        lock: DefaultLockable = None
        transient: bool = False

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
        functools.update_wrapper(self, fn)

    @property
    def _fn(self):
        return self.__fn

    @_fn.setter
    def _fn(self, x):
        self.__fn = x

    def reset(self) -> None:
        self._values = {}

    def __bool__(self) -> bool:
        raise TypeError

    def __call__(self, *args, **kwargs) -> T:
        k = self._key_maker(*args, **kwargs)

        try:
            return self._values[k]
        except KeyError:
            pass

        if self._lock is not None:
            with self._lock:
                try:
                    return self._values[k]
                except KeyError:
                    pass

                value = self._value_fn(*args, **kwargs)

        else:
            value = self._value_fn(*args, **kwargs)

        self._values[k] = value
        return value


#


class _FreeCachedFunction(_CachedFunction[T]):
    @classmethod
    def _unpickle(
            cls,
            fn,
            opts,
            values,
    ):
        return cls(
            fn,
            opts=opts,
            values=values,
        )

    def __reduce__(self):
        return (
            _FreeCachedFunction._unpickle,
            (
                self._fn,
                self._opts,
                self._values if not self._opts.transient else None,
            ),
        )


#


class _DescriptorCachedFunction(_CachedFunction[T]):
    def __init__(
            self,
            fn: ta.Callable[P, T],
            scope: ta.Any,  # classmethod | None
            *,
            instance: ta.Any = None,
            owner: ta.Any = None,
            name: str | None = None,
            **kwargs,
    ) -> None:
        super().__init__(fn, **kwargs)

        self._scope = scope
        self._instance = instance
        self._owner = owner
        self._name = name if name is not None else unwrap_func(fn).__name__
        self._bound_key_maker = None

    @classmethod
    def _unpickle(
            cls,
            scope,
            instance,
            owner,
            name,
            values,
    ):
        if scope is not None:
            raise NotImplementedError

        if instance is None:
            raise RuntimeError
        obj = type(instance)

        desc: _DescriptorCachedFunction = object.__getattribute__(obj, name)
        if not isinstance(desc, cls):
            raise TypeError(desc)
        if (desc._instance is not None or desc._owner is not None):
            raise RuntimeError

        return desc._bind(
            instance,
            owner,
            values=values,
        )

    def __reduce__(self):
        if self._scope is not None:
            raise NotImplementedError

        if not (self._instance is not None or self._owner is not None):
            raise RuntimeError

        return (
            _DescriptorCachedFunction._unpickle,
            (
                self._scope,
                self._instance,
                self._owner,
                self._name,
                self._values if not self._opts.transient else None,
            ),
        )

    def _bind(
            self,
            instance,
            owner=None,
            *,
            values: ta.MutableMapping | None = None,
    ):
        scope = self._scope
        if owner is self._owner and (instance is self._instance or scope is classmethod):
            return self

        fn, = self._fn
        name = self._name
        bound_fn = fn.__get__(instance, owner)
        if self._bound_key_maker is None:
            self._bound_key_maker = _make_cache_key_maker(fn, bound=True)

        bound = self.__class__(
            fn,
            scope,
            opts=self._opts,
            instance=instance,
            owner=owner,
            name=name,
            key_maker=self._bound_key_maker,
            # values=None if scope is classmethod else self._values,  # FIXME: ?
            values=values,
            value_fn=bound_fn,
        )

        if scope is classmethod and owner is not None:
            setattr(owner, name, bound)
        elif instance is not None:
            instance.__dict__[name] = bound

        return bound

    def __get__(self, instance, owner=None):
        return self._bind(instance, owner)


#


def cached_function(fn=None, **kwargs):  # noqa
    if fn is None:
        return functools.partial(cached_function, **kwargs)
    opts = _CachedFunction.Opts(**kwargs)
    if isinstance(fn, staticmethod):
        return _FreeCachedFunction(fn, opts=opts, value_fn=unwrap_func(fn))
    scope = classmethod if isinstance(fn, classmethod) else None
    return _DescriptorCachedFunction(fn, scope, opts=opts)


def static_init(fn: CallableT) -> CallableT:
    fn = cached_function(fn)
    fn()
    return fn
