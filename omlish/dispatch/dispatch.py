import abc
import typing as ta
import weakref

from .impls import find_impl as default_find_impl


T = ta.TypeVar('T')
U = ta.TypeVar('U')
U_co = ta.TypeVar('U_co', covariant=True)


##


_build_weak_dispatch_cache_impl: ta.Callable | None = None
_build_strong_dispatch_cache_impl: ta.Callable | None = None

try:
    from . import _dispatch  # type: ignore  # noqa
except ImportError:
    pass
else:
    _build_strong_dispatch_cache_impl = _dispatch.build_strong_dispatch_cache


##


class Dispatcher(ta.Generic[T]):
    """Shared dispatching system for functions and methods. Logic directly mimics `functools.singledispatch`."""

    def __init__(
            self,
            find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None] | None = None,
            *,
            strong_cache: bool = False,
    ) -> None:
        super().__init__()

        if find_impl is None:
            find_impl = default_find_impl
        self._find_impl = find_impl
        self._strong_cache = strong_cache

        self._impls_by_arg_cls: dict[type, T] = {}

        if strong_cache:
            if _build_strong_dispatch_cache_impl is not None:
                self._cache_factory = _build_strong_dispatch_cache_impl
            else:
                self._cache_factory = Dispatcher._StrongCache  # noqa
        elif _build_weak_dispatch_cache_impl is not None:
            self._cache_factory = _build_weak_dispatch_cache_impl
        else:
            self._cache_factory = Dispatcher._WeakCache  # noqa

        self._reset_cache(None)

    #

    class _CacheFactory(ta.Protocol[U]):
        def __call__(
            self,
            impls_by_arg_cls: dict[type, U],
            find_impl: ta.Callable[[type, ta.Mapping[type, U]], U | None],
            reset_cache_for_token: ta.Callable[['Dispatcher._Cache[U]'], None],
            token: ta.Any | None,
        ) -> 'Dispatcher._Cache[U]': ...

    class _Cache(ta.Protocol[U_co]):
        @property
        def token(self) -> ta.Any | None: ...

        @property
        def dct(self) -> ta.Mapping[ta.Any, U_co]: ...

        def dispatch(self, cls: type) -> ta.Any | None: ...

    _cache_factory: _CacheFactory[T]

    _cache: _Cache[T]

    #

    class _StrongCache:
        def __init__(
                self,
                impls_by_arg_cls: dict[type, T],
                find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None],
                reset_cache_for_token: ta.Callable[['Dispatcher._Cache'], None],
                token: ta.Any | None,
        ) -> None:
            self.token = token

            self.dct: dict[type, ta.Any] = {}

            dct = self.dct

            def dispatch(cls: type) -> ta.Any | None:
                if token is not None and abc.get_cache_token() != token:
                    reset_cache_for_token(self)
                    return find_impl(cls, impls_by_arg_cls)

                try:
                    return dct[cls]
                except KeyError:
                    pass

                impl: ta.Any | None
                try:
                    impl = impls_by_arg_cls[cls]
                except KeyError:
                    impl = find_impl(cls, impls_by_arg_cls)

                dct[cls] = impl
                return impl

            self.dispatch: ta.Callable[[type], ta.Any | None] = dispatch

    class _WeakCache:
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

    #

    def _reset_cache(self, token: ta.Any | None) -> None:
        self._cache = self._cache_factory(  # noqa
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
