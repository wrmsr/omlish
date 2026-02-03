import abc
import typing as ta
import weakref

from .impls import find_impl as default_find_impl


T = ta.TypeVar('T')


##


_build_dispatch_cache_impl: ta.Callable | None = None

try:
    from . import _dispatch  # type: ignore  # noqa
except ImportError:
    pass
else:
    _build_dispatch_cache_impl = _dispatch.build_dispatch_cache


##


class Dispatcher(ta.Generic[T]):
    """Shared dispatching system for functions and methods. Logic directly mimics `functools.singledispatch`."""

    def __init__(self, find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None] | None = None) -> None:
        super().__init__()

        if find_impl is None:
            find_impl = default_find_impl
        self._find_impl = find_impl

        self._impls_by_arg_cls: dict[type, T] = {}

        self._reset_cache(None)

    class _Cache:
        def __init__(
                self,
                impls_by_arg_cls: dict[type, T],
                find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None],
                reset_cache_for_token: ta.Callable[['Dispatcher._Cache'], None],
                token: ta.Any | None,
        ) -> None:
            self.token = token

            self.dct: dict[weakref.ref[type], ta.Any] = {}

            def dct_remove(k, self_ref=weakref.ref(self)):  # noqa
                if (ref_self := self_ref()) is not None:
                    try:
                        del ref_self.dct[k]
                    except KeyError:
                        pass

            dct = self.dct
            weakref_ref_ = weakref.ref

            def dispatch(cls: type) -> ta.Any | None:
                if token is not None and abc.get_cache_token() != token:
                    reset_cache_for_token(self)
                    return find_impl(cls, impls_by_arg_cls)

                cls_ref = weakref_ref_(cls)
                try:
                    return dct[cls_ref]
                except KeyError:
                    pass
                del cls_ref

                impl: ta.Any | None
                try:
                    impl = impls_by_arg_cls[cls]
                except KeyError:
                    impl = find_impl(cls, impls_by_arg_cls)

                dct[weakref_ref_(cls, dct_remove)] = impl
                return impl

            self.dispatch: ta.Callable[[type], ta.Any | None] = dispatch

    _cache: _Cache

    def _reset_cache(self, token: ta.Any | None) -> None:
        if _build_dispatch_cache_impl is not None:
            self._cache = _build_dispatch_cache_impl(  # noqa
                self._impls_by_arg_cls,
                self._find_impl,
                self._reset_cache_for_token,
                token,
            )

        else:
            self._cache = Dispatcher._Cache(
                self._impls_by_arg_cls,
                self._find_impl,
                self._reset_cache_for_token,
                token,
            )

    def _reset_cache_for_token(self, prev: _Cache) -> None:
        if prev is None or self._cache is prev:
            self._reset_cache(abc.get_cache_token())

    def dispatch(self, cls: type) -> ta.Any | None:
        return self._cache.dispatch(cls)

    def cache_size(self) -> int:
        return len(self._cache.dct)

    def register(self, impl: T, cls_col: ta.Iterable[type]) -> T:
        has_token = self._cache.token is not None

        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl

            if not has_token and hasattr(cls, '__abstractmethods__'):
                has_token = True

        self._reset_cache(abc.get_cache_token() if has_token else None)
        return impl
