import asyncio
import concurrent.futures as cf
import contextvars
import functools
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


@ta.final
class AsyncioToThread:
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop | None = None,
            exe: cf.Executor | None = None,
    ) -> None:
        self._loop = loop
        self._exe = exe

    async def __call__(self, func: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        if (loop := self._loop) is None:
            loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        func_call = functools.partial(ctx.run, func, *args, **kwargs)
        return await loop.run_in_executor(self._exe, func_call)
