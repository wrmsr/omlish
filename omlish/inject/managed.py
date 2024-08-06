"""
TODO:
 - proper ManagedProvider[Impl], DeferringProvider[Impl], closing (-> Deferring('close'))
"""
import contextlib
import typing as ta

from .binder import bind
from .elements import Elemental
from .injector import Injector
from .injector import create_injector


@contextlib.contextmanager
def create_managed_injector(*args: Elemental) -> ta.Generator[Injector, None, None]:
    i = create_injector(
        bind(contextlib.ExitStack, singleton=True, eager=True),
        *args,
    )
    with i[contextlib.ExitStack]:
        yield i


@contextlib.asynccontextmanager
async def create_async_managed_injector(*args: Elemental) -> ta.AsyncGenerator[Injector, None]:
    i = create_injector(
        bind(contextlib.AsyncExitStack, singleton=True, eager=True),
        *args,
    )
    async with i[contextlib.AsyncExitStack]:
        yield i
