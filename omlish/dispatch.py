import abc
import functools
import types
import typing as ta
import weakref

from . import c3


def _find_impl(cls, registry):
    mro = c3.compose_mro(cls, registry.keys())
    match = None
    for t in mro:
        if match is not None:
            if (
                    t in registry and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError('Ambiguous dispatch: {} or {}'.format(match, t))
            break
        if t in registry:
            match = t
    return registry.get(match)


def function(func):
    registry = {}
    dispatch_cache = weakref.WeakKeyDictionary()
    cache_token = None

    def dispatch(cls):
        nonlocal cache_token
        if cache_token is not None:
            current_token = abc.get_cache_token()
            if cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            try:
                impl = registry[cls]
            except KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        return impl

    def _is_union_type(cls):
        if hasattr(ta, 'UnionType'):
            return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
        else:
            return ta.get_origin(cls) in {ta.Union}

    def _is_valid_dispatch_type(cls):
        if isinstance(cls, type):
            return True
        return (_is_union_type(cls) and all(isinstance(arg, type) for arg in ta.get_args(cls)))

    def register(cls, func=None):
        nonlocal cache_token
        if _is_valid_dispatch_type(cls):
            if func is None:
                return lambda f: register(cls, f)
        else:
            if func is not None:
                raise TypeError(f'Invalid first argument to `register()`. {cls!r} is not a class or union type.')
            ann = getattr(cls, '__annotations__', {})
            if not ann:
                raise TypeError(
                    f'Invalid first argument to `register()`: {cls!r}. Use either `@register(some_class)` or plain '
                    f'`@register` on an annotated function.'
                )
            func = cls

            argname, cls = next(iter(ta.get_type_hints(func).items()))
            if not _is_valid_dispatch_type(cls):
                if _is_union_type(cls):
                    raise TypeError(f'Invalid annotation for {argname!r}. {cls!r} not all arguments are classes.')
                else:
                    raise TypeError(f'Invalid annotation for {argname!r}. {cls!r} is not a class.')

        if _is_union_type(cls):
            for arg in ta.get_args(cls):
                registry[arg] = func
        else:
            registry[cls] = func
        if cache_token is None and hasattr(cls, '__abstractmethods__'):
            cache_token = abc.get_cache_token()
        dispatch_cache.clear()
        return func

    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{funcname} requires at least 1 positional argument')

        return dispatch(type(args[0]))(*args, **kw)

    funcname = getattr(func, '__name__', 'singledispatch function')
    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    functools.update_wrapper(wrapper, func)
    return wrapper


class method:

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

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        functools.update_wrapper(_method, self._wrapped_func)
        return _method

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)
