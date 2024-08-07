import abc
import typing as ta
import weakref

from .dispatch import find_impl


T = ta.TypeVar('T')


##


class DispatchCacheProtocol(ta.Protocol[T]):
    def size(self) -> int: ...
    def prepare(self, cls: type) -> None: ...
    def clear(self) -> None: ...
    def put(self, cls: type, impl: T) -> None: ...
    def get(self, cls: type) -> T: ...  # Raises[KeyError]


class DispatcherProtocol(ta.Protocol[T]):
    def cache_size(self) -> int: ...
    def register(self, impl: T, cls_col: ta.Iterable[type]) -> T: ...
    def dispatch(self, cls: type) -> T | None: ...


##


class DispatchCache(DispatchCacheProtocol[T]):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[ta.Any, T] = {}

        def remove(k, self_ref=weakref.ref(self)):
            if (ref_self := self_ref()) is not None:
                dct = ref_self._dct  # noqa
                try:
                    del dct[k]
                except KeyError:
                    pass

        self._remove = remove

        self._token: ta.Any = None

    def size(self) -> int:
        return len(self._dct)

    def prepare(self, cls: type) -> None:
        if self._token is None and hasattr(cls, '__abstractmethods__'):
            self._token = abc.get_cache_token()

        self.clear()

    def clear(self) -> None:
        if self._dct:
            self._dct.clear()

    def put(self, cls: type, impl: T) -> None:
        self._dct[weakref.ref(cls, self._remove)] = impl

    def get(self, cls: type) -> T:
        if self._token is not None and (current_token := abc.get_cache_token()) != self._token:
            self._dct.clear()
            self._token = current_token

        cls_ref = weakref.ref(cls)
        return self._dct[cls_ref]


class Dispatcher(DispatcherProtocol[T]):
    def __init__(self) -> None:
        super().__init__()

        self._impls_by_arg_cls: dict[type, T] = {}
        self._cache: DispatchCache[T | None] = DispatchCache()

    def cache_size(self) -> int:
        return self._cache.size()

    def register(self, impl: T, cls_col: ta.Iterable[type]) -> T:
        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl
            self._cache.prepare(cls)

        return impl

    def dispatch(self, cls: type) -> T | None:
        try:
            return self._cache.get(cls)
        except KeyError:
            pass

        impl: T | None
        try:
            impl = self._impls_by_arg_cls[cls]
        except KeyError:
            impl = find_impl(cls, self._impls_by_arg_cls)

        self._cache.put(cls, impl)
        return impl
