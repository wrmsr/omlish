import abc
import typing as ta
import weakref

from .dispatch import find_impl


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


class Dispatcher(ta.Generic[T], abc.ABC):

    @abc.abstractmethod
    def register(self, impl: U, cls_col: ta.Iterable[type]) -> U:
        raise NotImplementedError

    @abc.abstractmethod
    def dispatch(self, cls: type) -> ta.Optional[T]:
        raise NotImplementedError


class _DispatchCache(ta.Protocol):
    def remove(self, k: type) -> ta.Any: ...
    def clear(self) -> None: ...
    def get(self, k: type) -> ta.Any: ...  # Raises[KeyError]
    def put(self, k: type, v: ta.Any) -> None: ...


##


class _DefaultDispatchCache:
    def __init__(self) -> None:
        super().__init__()

    def remove(self, k: type) -> ta.Any:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def get(self, k: type) -> ta.Any:
        raise NotImplementedError

    def put(self, k: type, v: ta.Any) -> None:
        raise NotImplementedError


class _Dispatcher(Dispatcher[T]):
    def __init__(self) -> None:
        super().__init__()

        self._impls_by_arg_cls: dict[type, T] = {}
        self._dispatch_cache: dict[ta.Any, T] = {}

        def cache_remove(k, self_ref=weakref.ref(self)):
            if (ref_self := self_ref()) is not None:
                cache = ref_self._dispatch_cache  # noqa
                try:
                    del cache[k]
                except KeyError:
                    pass

        self._cache_remove = cache_remove

        self._cache_token: ta.Any = None

    def register(self, impl: U, cls_col: ta.Iterable[type]) -> U:
        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl  # type: ignore

            if self._cache_token is None and hasattr(cls, '__abstractmethods__'):
                self._cache_token = abc.get_cache_token()

        self._dispatch_cache.clear()
        return impl

    def dispatch(self, cls: type) -> ta.Optional[T]:
        if self._cache_token is not None and (current_token := abc.get_cache_token()) != self._cache_token:
            self._dispatch_cache.clear()
            self._cache_token = current_token

        cls_ref = weakref.ref(cls)
        try:
            return self._dispatch_cache[cls_ref]
        except KeyError:
            pass
        del cls_ref

        try:
            impl = self._impls_by_arg_cls[cls]
        except KeyError:
            impl = find_impl(cls, self._impls_by_arg_cls)  # type: ignore

        self._dispatch_cache[weakref.ref(cls, self._cache_remove)] = impl
        return impl
