"""
TODO:
 - inline WeakKeyDictionary
"""
import abc
import typing as ta
import weakref

from .. import c3
from .. import check


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


def is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


_IMPL_FUNC_CLS_SET_CACHE: ta.MutableMapping[ta.Callable, ta.FrozenSet[type]] = weakref.WeakKeyDictionary()


def get_impl_func_cls_set(func: ta.Callable) -> ta.FrozenSet[type]:
    try:
        return _IMPL_FUNC_CLS_SET_CACHE[func]
    except KeyError:
        pass

    ann = getattr(func, '__annotations__', {})
    if not ann:
        raise TypeError(f'Invalid impl func: {func!r}')

    _, cls = next(iter(ta.get_type_hints(func).items()))
    if is_union_type(cls):
        ret = frozenset(check.isinstance(arg, type) for arg in ta.get_args(cls))
    else:
        ret = frozenset([check.isinstance(cls, type)])

    _IMPL_FUNC_CLS_SET_CACHE[func] = ret
    return ret


def find_impl(cls: type, registry: ta.Mapping[type, T]) -> ta.Optional[T]:
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

    return registry.get(match)


##


class _WeakKeyDictionary:
    def __init__(self):
        self._data = {}

        def remove(k, selfref=weakref.ref(self)):
            self = selfref()
            if self is not None:
                try:
                    del self._data[k]
                except KeyError:
                    pass

        self._remove = remove

    def __getitem__(self, key):
        return self._data[weakref.ref(key)]

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, value):
        self._data[weakref.ref(key, self._remove)] = value


class Dispatcher(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()

        impls_by_arg_cls: ta.Dict[type, T] = {}
        self._impls_by_arg_cls = impls_by_arg_cls

        dispatch_cache: ta.Any = _WeakKeyDictionary()
        self._get_dispatch_cache = lambda: dispatch_cache

        cache_token: ta.Any = None
        self._get_cache_token = lambda: cache_token

        def dispatch(cls: type) -> ta.Optional[T]:
            nonlocal cache_token
            nonlocal dispatch_cache

            if cache_token is not None:
                current_token = abc.get_cache_token()
                if cache_token != current_token:
                    dispatch_cache = _WeakKeyDictionary()
                    cache_token = current_token

            try:
                return dispatch_cache[cls]  # ~98ns
            except KeyError:
                pass

            try:
                impl = impls_by_arg_cls[cls]
            except KeyError:
                impl = find_impl(cls, impls_by_arg_cls)

            dispatch_cache[cls] = impl
            return impl

        self.dispatch = dispatch

        def register(impl: T, cls_col: ta.Iterable[type]) -> T:
            nonlocal cache_token
            nonlocal dispatch_cache

            for cls in cls_col:
                impls_by_arg_cls[cls] = impl  # type: ignore

                if cache_token is None and hasattr(cls, '__abstractmethods__'):
                    cache_token = abc.get_cache_token()

            dispatch_cache = _WeakKeyDictionary()
            return impl

        self.register = register

    _get_cache_token: ta.Callable[[], int]
    _get_dispatch_cache: ta.Callable[[], ta.Any]

    dispatch: ta.Callable[[type], ta.Optional[T]]

    register: ta.Callable[[U, ta.Iterable[type]], U]
