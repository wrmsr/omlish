import contextlib
import typing as ta


P = ta.ParamSpec('P')
T = ta.TypeVar('T')


##


async def call_with_async_exit_stack(  # type: ignore[return]  # ???
        fn: ta.Callable[ta.Concatenate[contextlib.AsyncExitStack, P], ta.Awaitable[T]],
        *args: ta.Any,
        **kwargs: ta.Any,
) -> T:
    async with contextlib.AsyncExitStack() as aes:
        return await fn(aes, *args, **kwargs)
