import abc
import contextlib
import typing as ta
import weakref

from .impls import find_impl as default_find_impl


T = ta.TypeVar('T')


##


class Dispatcher(ta.Generic[T]):
    def __init__(self, find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None] | None = None) -> None:
        super().__init__()

        if find_impl is None:
            find_impl = default_find_impl

        impls_by_arg_cls: dict[type, T] = {}
        self._impls_by_arg_cls = impls_by_arg_cls

        dispatch_cache: dict[ta.Any, T | None] = {}
        self._get_dispatch_cache = lambda: dispatch_cache

        def cache_remove(k, self_ref=weakref.ref(self)):
            if (ref_self := self_ref()) is not None:
                cache = ref_self._get_dispatch_cache()  # noqa
                with contextlib.suppress(KeyError):
                    del cache[k]

        cache_token: ta.Any = None
        self._get_cache_token = lambda: cache_token

        weakref_ref_ = weakref.ref

        def dispatch(cls: type) -> T | None:
            nonlocal cache_token

            if cache_token is not None and (current_token := abc.get_cache_token()) != cache_token:
                dispatch_cache.clear()
                cache_token = current_token

            cls_ref = weakref_ref_(cls)
            try:
                return dispatch_cache[cls_ref]
            except KeyError:
                pass
            del cls_ref

            impl: T | None
            try:
                impl = impls_by_arg_cls[cls]
            except KeyError:
                impl = find_impl(cls, impls_by_arg_cls)

            dispatch_cache[weakref_ref_(cls, cache_remove)] = impl
            return impl

        self.dispatch = dispatch

        def register(impl: T, cls_col: ta.Iterable[type]) -> T:
            nonlocal cache_token

            for cls in cls_col:
                impls_by_arg_cls[cls] = impl

                if cache_token is None and hasattr(cls, '__abstractmethods__'):
                    cache_token = abc.get_cache_token()

            dispatch_cache.clear()
            return impl

        self.register = register

    _get_cache_token: ta.Callable[[], int]
    _get_dispatch_cache: ta.Callable[[], ta.Any]

    def cache_size(self) -> int:
        return len(self._get_dispatch_cache())

    dispatch: ta.Callable[[type], T | None]

    register: ta.Callable[[T, ta.Iterable[type]], T]


##


# from x.dispatch import _gpto1_2 as _dispatch  # noqa
#
#
# class Dispatcher(ta.Generic[T]):  # noqa
#     def __init__(self, find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None] | None = None) -> None:
#         super().__init__()
#
#         if find_impl is None:
#             find_impl = default_find_impl
#         self._x = _dispatch.Dispatcher(find_impl)
#
#     def cache_size(self) -> int:
#         return self._x.cache_size()
#
#     def dispatch(self, cls: type) -> T | None:
#         return self._x.dispatch(cls)
#
#     def register(self, impl: T, cls_col: ta.Iterable[type]) -> T:
#         return self._x.register(impl, cls_col)
