"""
TODO:
 - integrate / expose with collections.cache
 - weakrefs (selectable by arg)
 - more rigorous descriptor pickling
  - must support free functions (which have no instance nor owner)
  - 'staticmethod' or effective equiv - which must resolve to the shared instance
   - and must be transient?
"""
import abc
import dataclasses as dc
import functools
import inspect
import typing as ta

from .attrs import transient_getattr
from .attrs import transient_setattr
from .classes.abstract import Abstract
from .contextmanagers import DefaultLockable
from .contextmanagers import default_lock
from .descriptors import unwrap_func
from .descriptors import unwrap_func_with_partials


P = ta.ParamSpec('P')
T = ta.TypeVar('T')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

_IGNORE = object()


##


def _nullary_cache_key_maker():
    return ()


def _simple_cache_key_maker(*args, **kwargs):
    return (args, tuple(sorted(kwargs.items())))


def _make_cache_key_maker(fn, *, simple=False, bound=False):
    if simple:
        return _simple_cache_key_maker

    fn, partials = unwrap_func_with_partials(fn)

    if inspect.isgeneratorfunction(fn) or inspect.iscoroutinefunction(fn):
        raise TypeError(fn)

    sig = inspect.signature(fn)
    sig_params = list(sig.parameters.values())[1 if bound else 0:]
    if not sig_params:
        return _nullary_cache_key_maker

    ns = {}
    src_params = []
    src_vals = []
    kwargs_name = None
    render_pos_only_separator = False
    render_kw_only_separator = True
    for p in sig_params:
        formatted = p.name
        if p.default is not inspect.Parameter.empty:
            ns[p.name] = p.default
            formatted = f'{formatted}={formatted}'
        kind = p.kind
        if kind == inspect.Parameter.VAR_POSITIONAL:
            formatted = '*' + formatted
        elif kind == inspect.Parameter.VAR_KEYWORD:
            formatted = '**' + formatted
        if kind == inspect.Parameter.POSITIONAL_ONLY:
            render_pos_only_separator = True
        elif render_pos_only_separator:
            src_params.append('/')
            render_pos_only_separator = False
        if kind == inspect.Parameter.VAR_POSITIONAL:
            render_kw_only_separator = False
        elif kind == inspect.Parameter.KEYWORD_ONLY and render_kw_only_separator:
            src_params.append('*')
            render_kw_only_separator = False
        src_params.append(formatted)
        if kind == inspect.Parameter.VAR_KEYWORD:
            kwargs_name = p.name
        else:
            src_vals.append(p.name)
    if render_pos_only_separator:
        src_params.append('/')

    kwa = f', __builtins__.tuple(__builtins__.sorted({kwargs_name}.items()))' if kwargs_name else ''
    rendered = (
        f'def __func__({", ".join(src_params)}):\n'
        f'    return ({", ".join(src_vals)}{kwa})\n'
    )
    exec(rendered, ns)

    kfn = ns['__func__']
    for part in partials[::-1]:
        kfn = functools.partial(kfn, *part.args, **part.keywords)

    return kfn


##


class _CachedFunction(ta.Generic[T], Abstract):
    @dc.dataclass(frozen=True)
    class Opts:
        map_maker: ta.Callable[[], ta.MutableMapping] = dict
        simple_key: bool = False
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
        self._key_maker = key_maker if key_maker is not None else _make_cache_key_maker(fn, simple=opts.simple_key)

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
            self._bound_key_maker = _make_cache_key_maker(fn, simple=self._opts.simple_key, bound=True)

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


##


class _CachedProperty(property, Abstract):
    def __init__(
            self,
            fn,
            *,
            name=None,
            ignore_if=lambda _: False,
    ):
        if isinstance(fn, property):
            fn = fn.fget

        super().__init__(fn)

        self._fn = fn
        self._ignore_if = ignore_if

        self._name = name

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name

    @abc.abstractmethod
    def _instance_get(self, instance: ta.Any) -> tuple[ta.Any, bool]:
        raise NotImplementedError

    @abc.abstractmethod
    def _instance_set(self, instance: ta.Any, value: ta.Any) -> None:
        raise NotImplementedError

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self._name is None:
            raise TypeError(self)

        value, ok = self._instance_get(instance)
        if ok:
            return value

        value = self._fn.__get__(instance, owner)()
        if value is _IGNORE:
            return None

        self._instance_set(instance, value)
        return value

    def __set__(self, instance, value):
        if self._ignore_if(value):
            return

        ev, ok = self._instance_get(instance)
        if ok and ev == value:
            return

        raise TypeError(self._name)

    def __delete__(self, instance):
        raise TypeError


#


class _DictCachedProperty(_CachedProperty):
    def _instance_get(self, instance: ta.Any) -> tuple[ta.Any, bool]:
        try:
            value = instance.__dict__[self._name]
        except KeyError:
            return None, False
        else:
            return value, True

    def _instance_set(self, instance: ta.Any, value: ta.Any) -> None:
        instance.__dict__[self._name] = value


#


class _TransientCachedProperty(_CachedProperty):
    def _instance_get(self, instance: ta.Any) -> tuple[ta.Any, bool]:
        try:
            value = transient_getattr(instance, self._name)
        except AttributeError:
            return None, False
        else:
            return value, True

    def _instance_set(self, instance: ta.Any, value: ta.Any) -> None:
        transient_setattr(instance, self._name, value)


#


def cached_property(fn=None, *, transient=False, **kwargs):  # noqa
    if fn is None:
        return functools.partial(cached_property, transient=transient, **kwargs)
    if transient:
        return _TransientCachedProperty(fn, **kwargs)
    else:
        return _DictCachedProperty(fn, **kwargs)
