"""
TODO:
 - proper ManagedProvider[Impl], DeferringProvider[Impl], closing (-> Deferring('close'))
"""
import contextlib
import typing as ta

from ... import lang
from ..binder import bind
from ..elements import Elemental
from ..impl.inspect import build_kwargs_target


if ta.TYPE_CHECKING:
    from .. import injector as _injector
    from .. import maysync as _maysync
    from .. import sync as _sync
else:
    _injector = lang.proxy_import('..injector', __package__)
    _maysync = lang.proxy_import('..maysync', __package__)
    _sync = lang.proxy_import('..sync', __package__)


T = ta.TypeVar('T')


##


def create_async_managed_injector(*args: Elemental) -> ta.AsyncContextManager['_injector.AsyncInjector']:
    @contextlib.asynccontextmanager
    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            yield await _injector.create_async_injector(
                bind(contextlib.AsyncExitStack, to_const=aes),
                *args,
            )
    return inner()


def make_async_managed_provider(
        fac: ta.Callable[..., T],
        *fns: ta.Callable[[T], ta.AsyncContextManager[T]],
) -> ta.Callable[..., ta.Awaitable[T]]:
    kt = build_kwargs_target(fac)

    async def _provide(
            ai: _injector.AsyncInjector,
            aes: contextlib.AsyncExitStack,
    ):
        obj = await ai.inject(kt)
        if not fns:
            obj = await aes.enter_async_context(obj)
        else:
            for fn in fns:
                await aes.enter_async_context(fn(obj))
        return obj

    return _provide


##


def create_managed_injector(*args: Elemental) -> ta.ContextManager['_sync.Injector']:
    @contextlib.contextmanager
    def inner():
        with contextlib.ExitStack() as es:
            yield _sync.create_injector(
                bind(contextlib.ExitStack, to_const=es),
                *args,
            )
    return inner()


def make_managed_provider(
        fac: ta.Callable[..., T],
        *fns: ta.Callable[[T], ta.ContextManager[T]],
) -> ta.Callable[..., T]:
    kt = build_kwargs_target(fac)

    def _provide(
            i: _sync.Injector,
            es: contextlib.ExitStack,
    ):
        obj = i.inject(kt)
        if not fns:
            obj = es.enter_context(obj)
        else:
            for fn in fns:
                es.enter_context(fn(obj))
        return obj

    return _provide


##


def create_maysync_managed_injector(*args: Elemental) -> ta.ContextManager['_maysync.MaysyncInjector']:
    @contextlib.contextmanager
    def inner():
        with contextlib.ExitStack() as es:
            yield _maysync.create_maysync_injector(
                bind(contextlib.ExitStack, to_const=es),
                *args,
            )
    return inner()


def make_maysync_managed_provider(
        fac: ta.Callable[..., T],
        *fns: ta.Callable[[T], ta.ContextManager[T]],
) -> ta.Callable[..., T]:
    kt = build_kwargs_target(fac)

    def _provide(
            i: _maysync.MaysyncInjector,
            es: contextlib.ExitStack,
    ):
        obj = i.inject(kt)
        if not fns:
            obj = es.enter_context(obj)
        else:
            for fn in fns:
                es.enter_context(fn(obj))
        return obj

    return _provide
