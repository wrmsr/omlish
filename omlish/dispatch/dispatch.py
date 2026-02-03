import abc
import typing as ta
import weakref

from .impls import find_impl as default_find_impl


T = ta.TypeVar('T')


##


class Dispatcher(ta.Generic[T]):
    """Shared dispatching system for functions and methods. Logic directly mimics `functools.singledispatch`."""

    def __init__(self, find_impl: ta.Callable[[type, ta.Mapping[type, T]], T | None] | None = None) -> None:
        super().__init__()

        if find_impl is None:
            find_impl = default_find_impl
        self._find_impl = find_impl

        self._impls_by_arg_cls: dict[type, T] = {}

        self._cache: Dispatcher._Cache = Dispatcher._Cache(self, None)

    class _Cache:
        def __init__(self, dispatcher: 'Dispatcher', token: ta.Any | None) -> None:
            self.dispatcher = dispatcher
            self.token = token

            self.dct: dict[weakref.ref[type], ta.Any] = {}

            def dct_remove(k, self_ref=weakref.ref(self)):  # noqa
                if (ref_self := self_ref()) is not None:
                    try:
                        del ref_self.dct[k]
                    except KeyError:
                        pass

            dct = self.dct
            impls_by_arg_cls = dispatcher._impls_by_arg_cls  # noqa
            find_impl = dispatcher._find_impl  # noqa
            weakref_ref_ = weakref.ref

            def dispatch(cls: type) -> ta.Any | None:
                if token is not None and abc.get_cache_token() != token:
                    dispatcher._reset_cache_for_token(self)  # noqa
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

    def dispatch(self, cls: type) -> ta.Any | None:
        return self._cache.dispatch(cls)

    def _reset_cache_for_token(self, prev: _Cache) -> None:
        if prev is None or self._cache is prev:
            self._cache = Dispatcher._Cache(self, abc.get_cache_token())

    def cache_size(self) -> int:
        return len(self._cache.dct)

    def register(self, impl: T, cls_col: ta.Iterable[type]) -> T:
        has_token = self._cache.token is not None

        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl

            if not has_token and hasattr(cls, '__abstractmethods__'):
                has_token = True

        self._cache = Dispatcher._Cache(self, abc.get_cache_token() if has_token else None)
        return impl
