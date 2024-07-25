"""
TODO:
 - try_weak .. allow non-weakrefable keys to just fall through and not cache
"""
import enum
import functools
import typing as ta
import weakref

from .impl import new_cache
from .types import Cache


C = ta.TypeVar('C', bound=ta.Callable)
CC: ta.TypeAlias = ta.Callable[[C], C]


class Scope(enum.Enum):
    INSTANCE = 'INSTANCE'
    CLASS = 'CLASS'
    STATIC = 'STATIC'


class _HashedSeq(list):
    __slots__ = ['hash_value']

    def __init__(
            self,
            tup: tuple,
            hasher: ta.Callable[[ta.Any], int] = hash,
    ) -> None:
        super().__init__()

        self[:] = tup
        self.hash_value = hasher(tup)

    def __hash__(self) -> int:  # type: ignore
        return self.hash_value


def _make_key(
        args: tuple,
        kwargs: dict[str, ta.Any],
        typed: bool,
        kwd_mark=(object(),),
        fasttypes=frozenset([int, str, frozenset, type(None)]),
        tuple=tuple,  # noqa
        type=type,  # noqa
        len=len,  # noqa
) -> ta.Any:
    key = args
    if kwargs:
        key += kwd_mark
        for item in kwargs.items():
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwargs:
            key += tuple(type(v) for v in kwargs.values())
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


class Ignore:

    def __init__(self, value: ta.Any) -> None:
        super().__init__()

        self._value = value


def ignore(value: ta.Any) -> ta.Any:
    return Ignore(value)


class _CacheDescriptor:

    def __init__(
            self,
            fn: ta.Callable,
            scope: Scope,
            typed: bool,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__()

        self._fn = fn
        functools.update_wrapper(self, fn)
        self._scope = scope
        self._typed = typed
        self._kwargs = kwargs
        self.__static: Cache | None = None
        self.__static_built: ta.Callable | None = None
        self._by_class: ta.MutableMapping[ta.Type, Cache] | None = weakref.WeakKeyDictionary() if scope == Scope.CLASS else None  # noqa
        self._name = None
        self._unary = kwargs.get('identity_keys', False) or kwargs.get('weak_keys', False)

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name

    @property
    def _static(self) -> Cache:
        if self.__static is None:
            self.__static = new_cache(**self._kwargs)
        return self.__static

    def _build(self, fn: ta.Callable, cache: Cache):
        def miss(key, result):
            if isinstance(result, Ignore):
                return result._value  # noqa
            else:
                cache[key] = result
                return result

        if self._unary:
            @functools.wraps(fn)
            def inner(key):
                try:
                    return cache[key]
                except KeyError:
                    pass
                return miss(key, fn(key))

        else:
            @functools.wraps(fn)
            def inner(*args, **kwargs):
                key = _make_key(args, kwargs, self._typed)
                try:
                    return cache[key]
                except KeyError:
                    pass
                return miss(key, fn(*args, **kwargs))

        return inner

    def __get__(self, instance, owner=None):
        if self._scope == Scope.STATIC:
            cache = self._static

        elif self._scope == Scope.CLASS:
            if owner is None:
                raise TypeError
            try:
                cache = self._by_class[owner]  # type: ignore
            except KeyError:
                cache = self._by_class[owner] = new_cache(**self._kwargs)  # type: ignore

        elif self._scope == Scope.INSTANCE:
            if instance is not None:
                cache = new_cache()
            else:
                @functools.wraps(self._fn)
                def trampoline(this, *args, **kwargs):
                    return self.__get__(this, owner)(*args, **kwargs)
                return trampoline

        else:
            raise TypeError

        fn = self._build(self._fn.__get__(instance, owner), cache)  # noqa

        if self._scope == Scope.CLASS:
            setattr(owner, self._name, fn)  # type: ignore
        elif self._scope == Scope.INSTANCE:
            setattr(instance, self._name, fn)  # type: ignore

        return fn

    def __call__(self, *args, **kwargs):
        if self.__static_built is None:
            self.__static_built = self._build(self._fn, self._static)
        return self.__static_built(*args, **kwargs)


def cache(
        scope: Scope | str = Scope.INSTANCE,
        typed: bool = False,
        **kwargs,
) -> CC:
    if not isinstance(scope, Scope):
        scope = getattr(Scope, scope.upper())  # noqa

    def inner(fn):
        return _CacheDescriptor(fn, scope, typed, **kwargs)  # type: ignore

    return ta.cast(CC, inner)
