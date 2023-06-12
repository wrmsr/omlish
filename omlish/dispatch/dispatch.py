"""
TODO:
 - collections.defaultdict in C, _dispatch_by_cls ~could~ be all C hot, but it's actually a WeakKeyDict :/
"""
import abc
import functools
import typing as ta
import weakref

from .. import c3
from .. import check


##


def _is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


_IMPL_CLS_SET_CACHE: ta.MutableMapping[ta.Callable, ta.FrozenSet[type]] = weakref.WeakKeyDictionary()


def _get_impl_cls_set(func: ta.Callable) -> ta.FrozenSet[type]:
    try:
        return _IMPL_CLS_SET_CACHE[func]
    except KeyError:
        pass

    ann = getattr(func, '__annotations__', {})
    if not ann:
        raise TypeError(f'Invalid impl: {func!r}')

    _, cls = next(iter(ta.get_type_hints(func).items()))
    if _is_union_type(cls):
        ret = frozenset(check.isinstance(arg, type) for arg in ta.get_args(cls))
    else:
        ret = frozenset([check.isinstance(cls, type)])

    _IMPL_CLS_SET_CACHE[func] = ret
    return ret


def _find_impl(cls: type, registry: ta.Mapping[type, ta.Callable]) -> ta.Callable:
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

    impl: ta.Optional[ta.Callable] = None
    if match is not None:
        impl = registry.get(match)
    if impl is None:
        raise RuntimeError(f'No dispatch: {cls}')
    return impl


##


class Dispatcher:
    def __init__(self) -> None:
        super().__init__()

        impls_by_arg_cls: ta.Dict[type, ta.Callable] = {}
        self._impls_by_arg_cls = impls_by_arg_cls

        dispatch_cache: ta.MutableMapping[type, ta.Callable] = weakref.WeakKeyDictionary()
        self._dispatch_cache = dispatch_cache

        cache_token: ta.Any = None

        def dispatch(cls: type) -> ta.Callable:
            nonlocal cache_token

            if cache_token is not None:
                current_token = abc.get_cache_token()
                if cache_token != current_token:
                    dispatch_cache.clear()
                    cache_token = current_token

            try:
                return dispatch_cache[cls]
            except KeyError:
                pass

            try:
                impl = impls_by_arg_cls[cls]
            except KeyError:
                impl = _find_impl(cls, impls_by_arg_cls)

            dispatch_cache[cls] = impl
            return impl

        self.dispatch = dispatch

        def register(impl: ta.Callable, cls_col: ta.Iterable[type]) -> None:
            nonlocal cache_token

            for cls in cls_col:
                impls_by_arg_cls[cls] = impl

                if cache_token is None and hasattr(cls, '__abstractmethods__'):
                    cache_token = abc.get_cache_token()

            self._dispatch_cache.clear()

        self.register = register

    dispatch: ta.Callable[[type], ta.Callable]

    register: ta.Callable[[ta.Callable, ta.Iterable[type]], None]


##


def function(func):
    disp = Dispatcher()
    disp.register(func, [object])

    func_name = getattr(func, '__name__', 'singledispatch function')

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{func_name} requires at least 1 positional argument')
        return disp.dispatch(type(args[0]))(*args, **kw)

    def register(impl, cls=None):
        cls_col: ta.Iterable[type]
        if cls is None:
            cls_col = _get_impl_cls_set(impl)
        else:
            cls_col = frozenset([cls])
        disp.register(impl, cls_col)

    wrapper.register = register  # type: ignore
    wrapper.dispatch = disp.dispatch  # type: ignore
    return wrapper
