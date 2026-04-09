import abc
import asyncio
import functools
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class AsyncThreadRunner(lang.Abstract):
    @abc.abstractmethod
    def run_in_thread(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]:
        raise NotImplementedError


##


class AsyncioAsyncThreadRunner(AsyncThreadRunner):
    def run_in_thread(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> ta.Awaitable[T]:
        return asyncio.to_thread(functools.partial(fn, *args, **kwargs))
