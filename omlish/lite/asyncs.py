# ruff: noqa: UP045
import functools
import typing as ta


T = ta.TypeVar('T')


##


async def opt_await(aw: ta.Optional[ta.Awaitable[T]]) -> ta.Optional[T]:
    return (await aw if aw is not None else None)


def as_async(fn: ta.Callable[..., T], *, wrap: bool = False) -> ta.Callable[..., ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner


##


@ta.final
class SyncToAsyncContextManager(ta.Generic[T]):
    def __init__(self, cm: ta.ContextManager[T]) -> None:
        self._cm = cm

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cm!r})'

    async def __aenter__(self) -> T:
        return self._cm.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback, /):
        return self._cm.__exit__(exc_type, exc_value, traceback)


as_async_context_manager = SyncToAsyncContextManager
