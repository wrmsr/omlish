"""
TODO:
 - proper ManagedProvider[Impl], DeferringProvider[Impl], closing (-> Deferring('close'))
"""
import contextlib
import typing as ta

from .. import lang
from .binder import bind
from .elements import Elemental
from .impl.inspect import build_kwargs_target
from .injector import Injector
from .injector import create_injector


if ta.TYPE_CHECKING:
    from .. import asyncs as _asyncs
else:
    _asyncs = lang.proxy_import('..asyncs', __package__)


T = ta.TypeVar('T')


##


@contextlib.contextmanager
def create_managed_injector(*args: Elemental) -> ta.Generator[Injector, None, None]:
    i = create_injector(
        bind(contextlib.ExitStack, singleton=True, eager=True),
        *args,
    )
    with i[contextlib.ExitStack]:
        yield i


def make_managed_provider(
        fac: ta.Callable[..., T],
        *fns: ta.Callable[[T], ta.ContextManager[T]],
) -> ta.Callable[..., T]:
    kt = build_kwargs_target(fac)

    def _provide(
            i: Injector,
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


@contextlib.asynccontextmanager
async def create_async_managed_injector(*args: Elemental) -> ta.AsyncGenerator[Injector, None]:
    i = await _asyncs.s_to_a(create_injector)(
        bind(contextlib.AsyncExitStack, singleton=True, eager=True),
        *args,
    )
    async with i[contextlib.AsyncExitStack]:
        yield i


def make_async_managed_provider(
        fac: ta.Callable[..., T],
        *fns: ta.Callable[[T], ta.AsyncContextManager[T]],
) -> ta.Callable[..., T]:
    kt = build_kwargs_target(fac)

    def _provide(
            i: Injector,
            aes: contextlib.AsyncExitStack,
    ):
        obj = i.inject(kt)
        if not fns:
            obj = _asyncs.a_to_s(aes.enter_async_context)(obj)
        else:
            for fn in fns:
                _asyncs.a_to_s(aes.enter_async_context)(fn(obj))
        return obj

    return _provide
