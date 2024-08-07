import abc
import typing as ta
import weakref

from .dispatch import find_impl


T = ta.TypeVar('T')


##


class Dispatcher(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()

        self._impls_by_arg_cls: dict[type, T] = {}
        self._dispatch_cache: dict[ta.Any, T | None] = {}

        def cache_remove(k, self_ref=weakref.ref(self)):
            if (ref_self := self_ref()) is not None:
                cache = ref_self._dispatch_cache  # noqa
                try:
                    del cache[k]
                except KeyError:
                    pass

        self._cache_remove = cache_remove

        self._cache_token: ta.Any = None

    def cache_size(self) -> int:
        return len(self._dispatch_cache)

    def register(self, impl: T, cls_col: ta.Iterable[type]) -> T:
        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl

            if self._cache_token is None and hasattr(cls, '__abstractmethods__'):
                self._cache_token = abc.get_cache_token()

        self._dispatch_cache.clear()
        return impl

    def dispatch(self, cls: type) -> T | None:
        if self._cache_token is not None and (current_token := abc.get_cache_token()) != self._cache_token:
            self._dispatch_cache.clear()
            self._cache_token = current_token

        cls_ref = weakref.ref(cls)
        try:
            return self._dispatch_cache[cls_ref]
        except KeyError:
            pass
        del cls_ref

        impl: T | None
        try:
            impl = self._impls_by_arg_cls[cls]
        except KeyError:
            impl = find_impl(cls, self._impls_by_arg_cls)

        self._dispatch_cache[weakref.ref(cls, self._cache_remove)] = impl
        return impl
