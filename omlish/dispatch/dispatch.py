import abc
import functools
import typing as ta
import weakref

from .. import c3
from .. import check


T = ta.TypeVar('T')


##


def _is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


def _get_impl_cls_set(func: ta.Callable) -> ta.Set[type]:
    ann = getattr(func, '__annotations__', {})
    if not ann:
        raise TypeError(f'Invalid impl: {func!r}')

    _, cls = next(iter(ta.get_type_hints(func).items()))
    if _is_union_type(cls):
        return {check.isinstance(arg, type) for arg in ta.get_args(cls)}
    else:
        return {check.isinstance(cls, type)}


def _find_impl(cls: type, registry: ta.Mapping[type, ta.Callable]) -> ta.Callable:
    mro = c3.compose_mro(cls, registry.keys())

    match: ta.Optional[type] = None
    for t in mro:
        if match is not None:
            # If *match* is an implicit ABC but there is another unrelated, equally matching implicit ABC, refuse the
            # temptation to guess.
            if (
                    t in registry
                    and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError(f'Ambiguous dispatch: {match} or {t}')
            break

        if t in registry:
            match = t

    impl: ta.Optional[ta.Callable] = None
    if match is not None:
        impl = registry.get(match)
    if impl is None:
        raise RuntimeError(f'No dispatch: {cls}')
    return impl


##


class Dispatcher:
    def __init__(self) -> None:
        super().__init__()

        self._impls_by_arg_cls: ta.Dict[type, ta.Callable] = {}
        self._dispatch_cache: ta.MutableMapping[type, ta.Callable] = weakref.WeakKeyDictionary()
        self._cache_token: ta.Any = None

    def dispatch(self, cls: type) -> ta.Callable:
        if self._cache_token is not None:
            current_token = abc.get_cache_token()
            if self._cache_token != current_token:
                self._dispatch_cache.clear()
                self._cache_token = current_token

        try:
            impl = self._dispatch_cache[cls]
        except KeyError:
            try:
                impl = self._impls_by_arg_cls[cls]
            except KeyError:
                impl = _find_impl(cls, self._impls_by_arg_cls)
            self._dispatch_cache[cls] = impl

        return impl

    def register(self, impl: ta.Callable, cls_col: ta.Iterable[type]) -> None:
        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl

            if self._cache_token is None and hasattr(cls, '__abstractmethods__'):
                self._cache_token = abc.get_cache_token()

        self._dispatch_cache.clear()


##


def function(func):
    disp = Dispatcher()
    disp.register(func, [object])

    func_name = getattr(func, '__name__', 'singledispatch function')

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{func_name} requires at least 1 positional argument')
        return disp.dispatch(type(args[0]))(*args, **kw)

    def register(impl, cls=None):
        if cls is None:
            cls_set = _get_impl_cls_set(impl)
        else:
            cls_set = {cls}
        disp.register(impl, cls_set)

    wrapper.register = register  # type: ignore
    wrapper.dispatch = disp.dispatch  # type: ignore
    return wrapper


##


class Method:
    def __init__(self, func: ta.Callable) -> None:
        if not callable(func) and not hasattr(func, '__get__'):  # type: ignore
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self._func = func

        self._impls: ta.MutableSet[ta.Callable] = weakref.WeakSet()

        self._dispatchers_by_cls: ta.MutableMapping[type, Dispatcher] = weakref.WeakKeyDictionary()

        # bpo-45678: special-casing for classmethod/staticmethod in Python <=3.9, as functools.update_wrapper doesn't
        # work properly in singledispatchmethod.__get__ if it is applied to an unbound classmethod/staticmethod
        unwrapped_func: ta.Any
        if isinstance(func, (staticmethod, classmethod)):
            unwrapped_func = func.__func__  # type: ignore
        else:
            unwrapped_func = func
        self._unwrapped_func = unwrapped_func

        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)  # noqa

    def register(self, impl: T) -> T:
        # bpo-39679: in Python <= 3.9, classmethods and staticmethods don't inherit __annotations__ of the wrapped
        # function (fixed in 3.10+ as a side-effect of bpo-43682) but we need that for annotation-derived
        # singledispatches. So we add that just-in-time here.
        if isinstance(impl, (staticmethod, classmethod)):
            impl.__annotations__ = getattr(impl.__func__, '__annotations__', {})

        check.callable(impl)
        if impl not in self._impls:
            self._impls.add(impl)  # type: ignore
            self._dispatchers_by_cls.clear()

        return impl

    def get_dispatcher(self, cls: type) -> Dispatcher:
        try:
            return self._dispatchers_by_cls[cls]
        except KeyError:
            pass

        disp = Dispatcher()
        disp.register(self._func, [object])

        for mro_cls in reversed(cls.__mro__):
            for nam, att in mro_cls.__dict__.items():
                if att in self._impls:
                    disp.register(att, _get_impl_cls_set(att))

        self._dispatchers_by_cls[cls] = disp
        return disp

    def __get__(self, obj, cls=None):
        check.not_none(cls)  # FIXME:

        @functools.wraps(self._unwrapped_func)
        def method(*args, **kwargs):  # noqa
            impl = self.get_dispatcher(cls).dispatch(type(args[0]))
            return impl.__get__(obj, cls)(*args, **kwargs)  # noqa

        method.register = self.register  # type: ignore

        method.__isabstractmethod__ = self.__isabstractmethod__  # type: ignore  # noqa

        return method


def method(func):
    return Method(func)
