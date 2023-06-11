import abc
import functools
import typing as ta
import weakref

from .. import c3
from .. import check


def _find_impl(cls, registry):
    mro = c3.compose_mro(cls, registry.keys())
    match = None
    for t in mro:
        if match is not None:
            if (  # type: ignore
                    t in registry and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError('Ambiguous dispatch: {} or {}'.format(match, t))
            break
        if t in registry:
            match = t
    return registry.get(match)


def _is_union_type(cls):
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


def _is_valid_dispatch_type(cls):
    if isinstance(cls, type):
        return True
    return (_is_union_type(cls) and all(isinstance(arg, type) for arg in ta.get_args(cls)))


class Dispatcher:
    def __init__(self) -> None:
        super().__init__()

        self._registry: ta.Dict[type, ta.Any] = {}
        self._dispatch_cache: ta.MutableMapping[type, ta.Any] = weakref.WeakKeyDictionary()
        self._cache_token: ta.Any = None

    def dispatch(self, cls: ta.Any) -> ta.Callable:
        if self._cache_token is not None:
            current_token = abc.get_cache_token()
            if self._cache_token != current_token:
                self._dispatch_cache.clear()
                self._cache_token = current_token

        try:
            impl = self._dispatch_cache[cls]
        except KeyError:
            try:
                impl = self._registry[cls]
            except KeyError:
                impl = _find_impl(cls, self._registry)
            self._dispatch_cache[cls] = impl

        return impl

    def register(self, impl: ta.Callable, cls: ta.Any = None) -> None:
        if cls is None:
            ann = getattr(impl, '__annotations__', {})
            if not ann:
                raise TypeError(f'Invalid first argument to `register()`: {impl!r}')

            arg_name, cls = next(iter(ta.get_type_hints(impl).items()))
            if not _is_valid_dispatch_type(cls):
                if _is_union_type(cls):
                    raise TypeError(f'Invalid annotation for {arg_name!r}. {cls!r} not all arguments are classes.')
                else:
                    raise TypeError(f'Invalid annotation for {arg_name!r}. {cls!r} is not a class.')

        check.arg(_is_valid_dispatch_type(cls))
        if _is_union_type(cls):
            for arg in ta.get_args(cls):
                self._registry[arg] = impl
        else:
            self._registry[cls] = impl

        if self._cache_token is None and hasattr(cls, '__abstractmethods__'):
            self._cache_token = abc.get_cache_token()

        self._dispatch_cache.clear()


def function(func):
    disp = Dispatcher()
    disp.register(func, object)

    func_name = getattr(func, '__name__', 'singledispatch function')

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{func_name} requires at least 1 positional argument')
        return disp.dispatch(type(args[0]))(*args, **kw)

    wrapper.register = disp.register  # type: ignore
    wrapper.dispatch = disp.dispatch  # type: ignore
    return wrapper


class Method:
    def __init__(self, func):
        if not callable(func) and not hasattr(func, '__get__'):
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self.dispatcher = function(func)
        self.func = func

        if isinstance(func, (staticmethod, classmethod)):
            self._wrapped_func = func.__func__
        else:
            self._wrapped_func = func

    def register(self, cls, method=None):
        if isinstance(cls, (staticmethod, classmethod)):
            cls.__annotations__ = getattr(cls.__func__, '__annotations__', {})
        return self.dispatcher.register(cls, func=method)

    def __get__(self, obj, cls=None):
        def _method(*args, **kwargs):
            method = self.dispatcher.dispatch(type(args[0]))
            return method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__  # type: ignore
        _method.register = self.register  # type: ignore
        functools.update_wrapper(_method, self._wrapped_func)
        return _method

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)


method = Method
